from dataclasses import dataclass


@dataclass
class OutlineItem:
    start: int   # 1-based line number
    count: int   # number of lines covered
    signature: str

    @property
    def num_width(self) -> int:
        return len(str(self.start))

    def format(self, num_width, line_width):
        field = f"{str(self.start).rjust(num_width)},{self.count}"
        line = f"{field.ljust(2 * num_width + 1)}  {self.signature}"
        if line_width and len(line) > line_width:
            line = line[:line_width - 3] + "..."
        return line
