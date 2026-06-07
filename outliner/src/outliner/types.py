from dataclasses import dataclass


@dataclass
class OutlineItem:
    start: int = 0
    count: int = 0
    locator: str = ""
    signature: str = ""

    @property
    def fmt_width(self) -> int:
        if self.start > 0:
            return len(str(self.start + self.count))
        if self.locator:
            return len(self.locator)
        return 0

    def format(self, fmt_width, line_width):
        if self.start > 0:
            field = f"{str(self.start).rjust(fmt_width)},{self.count}"
            field = field.ljust(2 * fmt_width + 1)
        elif self.locator:
            field = self.locator.ljust(fmt_width)
        else:
            field = ""
        line = f"{field}  {self.signature}"
        if line_width and len(line) > line_width:
            line = line[:line_width - 3] + "..."
        return line
