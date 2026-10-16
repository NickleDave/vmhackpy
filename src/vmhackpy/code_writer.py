import pathlib

from .parser import CommandType


def write_add(lines: list[str], x:int, y:int):
    lines.extend([
        f"@{x}",
        "D=A",
        f"@{y}",
        "D=D+A",
        "M=D",
    ])


class CodeWriter:
    def __init__(
        self,
    ):
        self.stack = []

    def set_filename(self, filename: str):
        self.filename = filename
        self.lines = []

    def write_arithmetic(self, command: str):
        y = self.stack.pop()
        if command in ("add", "sub", "eq", "gt", "lt", "and", "or"):
            x = self.stack.pop()
        

    def write_push_pop(self, command: CommandType, segment: str, index: int):
        if command == CommandType.C_PUSH:
            if segment == "constant":
                self.stack.append(index)

    def close(self):
        with pathlib.Path(self.filename).open("w") as fp:
            fp.writelines(self.lines)
