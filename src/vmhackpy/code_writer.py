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
        "    D=M",      # Pop top value off stack, D = (y = Memory[A])
        "    A=A-1",    # Decrement again
        "    D=D+M",    # Pop + add: D = (x = Memory[A]) + y
        "    M=D",      # Write over last value we popped with add result
        "    D=A",      # Store decremented address to update @SP
        "    @SP",      # set up to update stack pointer
        "    M=D+1",    # Make stack pointer point to location after add result
    ])


def write_sub(lines: list[str]):
    lines.extend([
        "    @SP",      # set A register to RAM[0]
        "    A=M",      # set A register to *value* of RAM[0] 
        "    A=A-1",    # decrement to point to top value on stack
        "    D=M",      # Pop top value off stack, D = (y = Memory[A])
        "    A=A-1",    # Decrement again
        "    D=M-D",    # Pop + sub: D = (x = Memory[A]) - y
        "    M=D",      # Write over last value we popped with add result
        "    D=A",      # Store decremented address to update @SP
        "    @SP",      # set up to update stack pointer
        "    M=D+1",    # Make stack pointer point to location after add result
    ])


def write_neg(lines: list[str]):
    lines.extend([
        "    @SP",      # set A register to RAM[0]
        "    A=M",      # set A register to *value* of RAM[0] 
        "    A=A-1",    # decrement to point to top value on stack
        "    D=-M",     # Pop top value off stack and make negative, y = -Memory[A]
        "    M=D",      # Write over last value we popped with neg result
        # note we don't need to update stack pointer since 
        # we just wrote over top value on the stack, so next empty word stays the same
    ])


def write_eq(lines: list[str], jump_counter: int):
    lines.extend([
        "    @SP",      # Set A register to RAM[0]
        "    M=M-1",    # Decrement stack pointer "in place" *before we pop!*
        "    A=M",      # Get the address we just decremented
        "    D=M",      # Pop top value off stack, D = (y = Memory[A])
        "    @SP",      # Decrement before pop again
        "    M=M-1",
        "    A=M",
        "    D=M-D",    # Pop + sub: D = (x = Memory[A]) - y
       f"    @ISEQUAL_{jump_counter}",
        "    D;JEQ",    # jump if D=0
       f"    @ISNOTEQUAL_{jump_counter}",
        "    0;JMP",    # if we didn't jump then D != 0
       f"(ISEQUAL_{jump_counter})",
        "    D=-1",     # D=True
       f"    @EQUALEND_{jump_counter}",
        "    0;JMP",
       f"(ISNOTEQUAL_{jump_counter})",
        "    D=0",      # D=False
       f"    @EQUALEND_{jump_counter}",
        "    0;JMP",
       f"(EQUALEND_{jump_counter})",
        "    @SP",      # Get stack pointer address
        "    A=M",      # Load pointer itself into A-register
        "    M=D",      # Push eq result to stack
        "    @SP",      # Get stack pointer address again, to increment
        "    M=M+1",    # Increment stack pointer
    ])


def write_gt(lines: list[str], jump_counter: int):
    lines.extend([
        "    @SP",      # Set A register to RAM[0]
        "    M=M-1",    # Decrement stack pointer "in place" *before we pop!*
        "    A=M",      # Get the address we just decremented
        "    D=M",      # Pop top value off stack, D = (y = Memory[A])
        "    @SP",      # Decrement before pop again
        "    M=M-1",
        "    A=M",
        "    D=M-D",    # Pop + sub: D = (x = Memory[A]) - y
       f"    @ISGT_{jump_counter}",
        "    D;JGT",    # jump if D>0
       f"    @ISNOTGT_{jump_counter}",
        "    0;JMP",    # if we didn't jump then D != 0
       f"(ISGT_{jump_counter})",
        "    D=-1",     # D=True
       f"    @GTEND_{jump_counter}",
        "    0;JMP",
       f"(ISNOTGT_{jump_counter})",
        "    D=0",      # D=False
       f"    @GTEND_{jump_counter}",
        "    0;JMP",
       f"(GTEND_{jump_counter})",
        "    @SP",      # Get stack pointer address
        "    A=M",      # Load pointer itself into A-register
        "    M=D",      # Push gt result to stack
        "    @SP",      # Get stack pointer address again, to increment
        "    M=M+1",    # Increment stack pointer
    ])


def write_lt(lines: list[str], jump_counter: int):
    lines.extend([
        "    @SP",      # Set A register to RAM[0]
        "    M=M-1",    # Decrement stack pointer "in place" *before we pop!*
        "    A=M",      # Get the address we just decremented
        "    D=M",      # Pop top value off stack, D = (y = Memory[A])
        "    @SP",      # Decrement before pop again
        "    M=M-1",
        "    A=M",
        "    D=M-D",    # Pop + sub: D = (x = Memory[A]) - y
       f"@ISLT_{jump_counter}",
        "    D;JLT",    # jump if D<0
       f"@ISNOTLT_{jump_counter}",
        "    0;JMP",    # if we didn't jump then D != 0
       f"(ISLT_{jump_counter})",
        "    D=-1",     # D=True
       f"    @LTEND_{jump_counter}",
        "    0;JMP",
       f"(ISNOTLT_{jump_counter})",
        "    D=0",      # D=False
       f"    @LTEND_{jump_counter}",
        "    0;JMP",
       f"(LTEND_{jump_counter})",
        "    @SP",      # Get stack pointer address
        "    A=M",      # Load pointer itself into A-register
        "    M=D",      # Push lt result to stack
        "    @SP",      # Get stack pointer address again, to increment
        "    M=M+1",    # Increment stack pointer
    ])


def write_and(lines: list[str]):
    lines.extend([
        "    @SP",      # set A register to RAM[0]
        "    A=M",      # set A register to *value* of RAM[0] 
        "    A=A-1",    # decrement to point to top value on stack
        "    D=M",      # Pop top value off stack, y = Memory[A]
        "    A=A-1",    # Decrement again
        "    D=M&D",    # Pop + AND: D = (x =  Memory[A]) && y
        "    M=D",      # Write over last value we popped with add result
        "    D=A",      # Store decremented address to update @SP
        "    @SP",      # set up to update stack pointer
        "    M=D+1",    # Make stack pointer point to location after add result
    ])


def write_or(lines: list[str]):
    lines.extend([
        "    @SP",      # set A register to RAM[0]
        "    A=M",      # set A register to *value* of RAM[0] 
        "    A=A-1",    # decrement to point to top value on stack
        "    D=M",      # Pop top value off stack, x = Memory[A]
        "    A=A-1",    # Decrement again
        "    D=M|D",    # Pop + OR: D = (x = Memory[A]) || y
        "    M=D",      # Write over last value we popped with add result
        "    D=A",      # Store decremented address to update @SP
        "    @SP",      # set up to update stack pointer
        "    M=D+1",    # Make stack pointer point to location after add result
    ])


def write_not(lines: list[str]):
    lines.extend([
        "    @SP",      # set A register to RAM[0]
        "    A=M",      # set A register to *value* of RAM[0] 
        "    A=A-1",    # decrement to point to top value on stack
        "    D=!M",     # Pop top value off stack, x = ! Memory[A]
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
        self.jump_counter = 0

    def set_filename(self, filename: str | pathlib.Path):
        self.filename = pathlib.Path(filename)

    def write_arithmetic(self, command: str):
        match command:
            case "add":
                write_add(self.lines)
            case "sub":
                write_sub(self.lines)
            case "eq":
                write_eq(self.lines, self.jump_counter)
                self.jump_counter += 1
            case "gt":
                write_gt(self.lines, self.jump_counter)
                self.jump_counter += 1
            case "lt":
                write_lt(self.lines, self.jump_counter)
                self.jump_counter += 1
            case "and":
                write_and(self.lines)
            case "or":
                write_or(self.lines)

    def write_push_pop(self, command: CommandType, segment: str, index: int):
        if command == CommandType.C_PUSH:
            if segment == "constant":
                write_push_constant(self.lines, constant=index)

    def close(self):
        write_end(self.lines)
        with self.filename.open("w") as fp:
            fp.writelines(line + "\n" for line in self.lines)
