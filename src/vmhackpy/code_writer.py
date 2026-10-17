import pathlib

from .parser import CommandType


# ---- preludes
def write_prelude(lines: list[str]):
    """Write "prelude", initialization that must occur 
    at the start of each Hack assembly program to set up 
    the Virtual Machine
    """
    lines.extend([
        "// initialize",
        "    @256",
        "    D=A",
        "    @SP",
        "    M=D",
        "",
        "// program start",
    ])


# ---- Arithmetic commands
def write_add(lines: list[str]):
    lines.extend([
        "    @SP",      # set A register to RAM[0]
        "    A=M",      # set A register to *value* of RAM[0] 
        "    A=A-1",    # decrement to point to top value on stack
        "    D=M",      # Pop top value off stack, x = Memory[A]
        "    A=A-1",    # Decrement again
        "    D=D+M",    # Pop + add: D = x + (y = Memory[A])
        "    M=D",      # Write over last value we popped with add result
        "    D=A",      # Store decremented address to update @SP
        "    @SP",      # set up to update stack pointer
        "    M=D+1",    # Make stack pointer point to location after add result
    ])


def write_subtract(lines: list[str]):
    lines.extend([
        "    @SP",      # set A register to RAM[0]
        "    A=M",      # set A register to *value* of RAM[0] 
        "    A=A-1",    # decrement to point to top value on stack
        "    D=M",      # Pop top value off stack, x = Memory[A]
        "    A=A-1",    # Decrement again
        "    D=D-M",    # Pop + add: D = x - (y = Memory[A])
        "    M=D",      # Write over last value we popped with add result
        "    D=A",      # Store decremented address to update @SP
        "    @SP",      # set up to update stack pointer
        "    M=D+1",    # Make stack pointer point to location after add result
    ])


# ---- push
def write_push_constant(lines: list[str], constant: int):
    lines.extend([
       f"    @{constant}",  # put constant value into A register
        "    D=A",          # store value in A in D register so we can load stack pointer
        "    @SP",          # Set A register to 0
        "    A=M",          # Set A to Memory[0]
        "    M=D",          # Set Memory[A] to the value we put in D
        "    @SP",          # Set up to increment stack pointer
        "    M=M+1",        # Increment stack pointer; Memory[0] = Memory[0] + 1
    ])


# ---- end of program
def write_end(lines: list[str]):
    """Write code that signals end of assembly program"""
    lines.extend([
        "(END)",
        "    @END",
        "    0;JMP",
    ])


class CodeWriter:
    def __init__(
        self,
    ):
        self.lines = []
        write_prelude(self.lines)

    def set_filename(self, filename: str):
        self.filename = filename

    def write_arithmetic(self, command: str):
        match command:
            case "add":
                write_add(self.lines)
            case "sub":
                pass
            case "eq":
                pass
            case "gt":
                pass
            case "lt":
                pass
            case "and":
                pass
            case "or":
                pass
        

    def write_push_pop(self, command: CommandType, segment: str, index: int):
        if command == CommandType.C_PUSH:
            if segment == "constant":
                write_push_constant(self.lines, constant=index)

    def close(self):
        write_end(self.lines)
        with pathlib.Path(self.filename).open("w") as fp:
            fp.writelines(line + "\n" for line in self.lines)
