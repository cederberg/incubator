"""JSON / NDJSON outline parser.

Produces path-based locators (jq-style) with type, optionality, and
truncated scalar samples in the signature column.
"""

import io
import json
import os
from collections.abc import Iterator, Sequence

from outliner.types import OutlineItem

SYNTAX = "json"
EXTENSIONS = (".json", ".jsonl", ".ndjson")

NDJSON_SAMPLE = 200


# -- detection -----------------------------------------------------------

def detect(lines: list[str]) -> bool:
    """Detect NDJSON (each non-blank line is a valid JSON object)."""
    non_empty = [l for l in lines if l.strip()]
    if not non_empty:
        return False
    for line in non_empty[:5]:
        try:
            val = json.loads(line)
            if not isinstance(val, dict):
                return False
        except json.JSONDecodeError:
            return False
    return True


# -- entry point ---------------------------------------------------------

def read(fh) -> Iterator[OutlineItem]:
    first_line = fh.readline()
    if not first_line.strip():
        return

    stripped = first_line.strip()

    # Single-doc array — first char is '['
    if stripped.startswith("["):
        fh.seek(0)
        yield from _outline_single(fh)
        return

    # Try NDJSON — first line is a valid JSON dict
    try:
        val = json.loads(stripped)
    except json.JSONDecodeError:
        pass
    else:
        if isinstance(val, dict):
            # Check second line for NDJSON confirmation
            second_line = fh.readline()
            if second_line.strip():
                try:
                    json.loads(second_line.strip())
                except json.JSONDecodeError:
                    pass
                else:
                    fh.seek(0)
                    yield from _outline_ndjson(fh)
                    return
            # Second line empty or not valid JSON → single-doc object
            fh.seek(0)
            yield from _outline_single(fh)
            return

    # Fall back to single-doc check with larger read
    fh.seek(0)
    head = fh.read(65536)
    fh.seek(0)

    if _is_single_doc(head):
        yield from _outline_single(fh)


# -- format detection ----------------------------------------------------

def _is_single_doc(head: str) -> bool:
    stripped = head.strip()
    if not stripped:
        return False
    try:
        json.loads(stripped)
    except json.JSONDecodeError:
        return False
    return True


# -- NDJSON --------------------------------------------------------------

def _outline_ndjson(fh) -> Iterator[OutlineItem]:
    records: list[dict] = []
    sample_bytes = 0
    for line in fh:
        stripped = line.strip()
        if not stripped:
            continue
        if len(records) < NDJSON_SAMPLE:
            records.append(json.loads(stripped))
            sample_bytes += len(line)
        elif sample_bytes:
            break

    if not records:
        return

    fsize = _file_size(fh)
    avg_line = sample_bytes / len(records)
    est_total = int(fsize / avg_line) if avg_line else 0
    size_str = _format_size(fsize)
    yield OutlineItem(
        locator="$",
        signature=f"{size_str} · json · ndjson · ~{_format_count(est_total)} records",
    )

    yield from _emit_schema(records)


# -- single-doc JSON -----------------------------------------------------

def _outline_single(fh) -> Iterator[OutlineItem]:
    try:
        data = json.load(fh)
    except json.JSONDecodeError:
        return

    fsize = _file_size(fh)
    size_str = _format_size(fsize)

    if isinstance(data, list):
        kind = f"array[{len(data)}]"
    elif isinstance(data, dict):
        kind = "object"
    elif data is None:
        kind = "null"
    else:
        kind = type(data).__name__

    yield OutlineItem(
        locator="$",
        signature=f"{size_str} · json · {kind}",
    )

    if isinstance(data, dict):
        samples = [data]
    elif isinstance(data, list):
        samples = data[:NDJSON_SAMPLE]
    else:
        samples = [data]
    yield from _emit_schema(samples)


# -- schema emission -----------------------------------------------------

def _emit_schema(samples: Sequence) -> Iterator[OutlineItem]:
    if not samples:
        return
    schema = _collect_schema(samples)
    for locator, sig in _flatten_schema(schema):
        yield OutlineItem(locator=locator, signature=sig)


def _collect_schema(samples: Sequence) -> dict:
    """Collect type and optionality info from sample records."""
    if not samples:
        return {"_type": "?", "_optional": False}

    first = samples[0]

    if isinstance(first, dict):
        schema: dict = {"_type": "object", "_fields": {}}
        all_keys: set[str] = set()
        dict_samples = [s for s in samples if isinstance(s, dict)]
        for s in dict_samples:
            all_keys.update(s.keys())
        for key in sorted(all_keys):
            # Skip keys that are always null (treat as absent)
            present = sum(1 for s in dict_samples if key in s and s[key] is not None)
            if present == 0:
                continue
            sub_samples = [s[key] for s in dict_samples if key in s and s[key] is not None]
            child = _collect_schema(sub_samples)
            child["_optional"] = present < len(dict_samples)
            schema["_fields"][key] = child
        return schema

    if isinstance(first, list):
        elements = [e for s in samples if isinstance(s, list) for e in s]
        child = _collect_schema(elements)
        result: dict = {"_type": "array", "_element": child}
        if not _is_container(child["_type"]):
            result["_samples"] = samples[:5]
        return result

    # Scalar
    types: set[str] = set()
    for s in samples:
        types.add(_type_name(s))
    return {"_type": "|".join(sorted(types)), "_samples": samples, "_optional": False}


def _flatten_schema(schema: dict, locator: str = "") -> Iterator[tuple[str, str]]:
    """Yield (locator, signature) pairs in depth-first order, scalars first."""

    if "_fields" in schema:
        if locator and not locator.endswith("]"):
            sig = _sig_line(schema["_type"], schema.get("_optional", False))
            yield locator, sig

        fields = schema["_fields"]
        scalar_keys = [k for k in fields if not _is_container(fields[k]["_type"])]
        container_keys = [k for k in fields if _is_container(fields[k]["_type"])]

        for key in scalar_keys:
            child = fields[key]
            sub_loc = f"{locator}.{key}" if locator else f".{key}"
            child_opt = child.get("_optional", False) or schema.get("_optional", False)
            sig = _sig_line(child["_type"], child_opt)
            sample = _sample_str(child)
            if sample:
                sig = f"{sig} -- {sample}"
            yield sub_loc, sig

        for key in container_keys:
            child = fields[key]
            sub_loc = f"{locator}.{key}" if locator else f".{key}"
            # Propagate parent optionality to children
            if schema.get("_optional", False):
                child["_optional"] = True
            yield from _flatten_schema(child, sub_loc)

    elif "_element" in schema:
        elem = schema["_element"]
        elem_loc = f"{locator}[]"
        if _is_container(elem["_type"]):
            if locator:
                sig = _sig_line("array", schema.get("_optional", False))
                yield elem_loc, sig
            yield from _flatten_schema(elem, elem_loc)
        else:
            sig = _sig_line(f"array[{elem['_type']}]", schema.get("_optional", False))
            sample = _sample_str(schema)
            if sample:
                sig = f"{sig} -- {sample}"
            yield elem_loc, sig


def _is_container(type_str: str) -> bool:
    return type_str in ("object", "array") or type_str.startswith("array")


def _sig_line(type_str: str, optional: bool) -> str:
    opt = "?" if optional else ""
    return f"{type_str}{opt}"


def _sample_str(child: dict) -> str:
    samples = child.get("_samples")
    if not samples:
        return ""
    val = samples[0]
    if val is None:
        return "null"
    s = json.dumps(val, ensure_ascii=False, default=str)
    if len(s) > 40:
        s = s[:38] + "…"
        if isinstance(val, str):
            s += '"'
    return s


def _type_name(val) -> str:
    if val is None:
        return "null"
    if isinstance(val, bool):
        return "bool"
    if isinstance(val, int):
        return "int"
    if isinstance(val, float):
        return "float"
    if isinstance(val, str):
        return "str"
    if isinstance(val, list):
        elem_types = {_type_name(e) for e in val[:10]}
        inner = "|".join(sorted(elem_types)) if elem_types else "?"
        return f"array[{inner}]" if len(elem_types) == 1 else "array"
    if isinstance(val, dict):
        return "object"
    return type(val).__name__


# -- helpers -----------------------------------------------------------

def _file_size(fh) -> int:
    try:
        return os.fstat(fh.fileno()).st_size
    except (io.UnsupportedOperation, OSError):
        return 0

def _format_size(size_bytes: int) -> str:
    if size_bytes >= 1_000_000_000:
        return f"{size_bytes / 1_000_000_000:.1f} GB"
    if size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.1f} MB"
    if size_bytes >= 1_000:
        return f"{size_bytes / 1_000:.1f} KB"
    return f"{size_bytes} B"


def _format_count(n: int) -> str:
    if n >= 1_000_000:
        return f"{n // 1_000_000}M"
    if n >= 1_000:
        return f"{n // 1_000}K"
    return str(n)
