from dataclasses import dataclass


@dataclass
class OutlineItem:
    start: int   # 1-based line number
    count: int   # number of lines covered
    signature: str
