import pathlib
from typing import Literal

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


# ---- Stack arithmetic commands --------------------------------------------------------
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
        # note we don't need to update stack pointer since 
        # we just wrote over top value on the stack, so next empty word stays the same
    ])


# ---- Memory access commands -----------------------------------------------------------
# N.B.: these are orded by "the order the book tells us to implement them in"
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


def write_push_lcl_arg_this_that(lines: list[str], symbol:str, index: int):
    lines.extend([
       f"    @{symbol}",# put symbol index into A register
        "    D=M",      # put symbol pointer in D: base of segment
       f"    @{index}", # put value of offset index into A register
        "    A=D+A",    # store segment base + offset index in A
        "    D=M",      # store the *value* of RAM[ARG base + offset] in D
        "    @SP",      # Set A register to RAM[0]
        "    A=M",      # Set A to Memory[0]
        "    M=D",      # Push ARG value in D onto stack, Memory[A]
        "    @SP",      # Set up to increment stack pointer
        "    M=M+1",    # Increment stack pointer; Memory[0] = Memory[0] + 1
    ])


def write_pop_lcl_arg_this_that(lines: list[str], symbol:str, index: int):
    lines.extend([
       f"    @{symbol}",# put symbol index into A register
        "    D=M",      # put symbol pointer in D: base of segment
       f"    @{index}", # put value of offset index into A register        
        "    D=D+A",    # store segment base + offset in D
        "    @R13",     # put VM register address in A
        "    M=D",      # stash segment base + offset from D in VM register
        "    @SP",      # Set A register to RAM[0]
        "    M=M-1",    # Decrement stack pointer, RAM[0] = RAM[0] - 1
        "    A=M",      # put *value* of stack pointer in A
        "    D=M",      # pop top value off stack in D
        "    @R13",     # put VM register address in A, pointer to segment base + offset
        "    A=M",      # Set A to segment base + offset
        "    M=D",      # Put value from D that we popped off stack into segment at offset
    ])


def write_push_pointer_temp(lines: list[str], ram_address: int):
    lines.extend([
       f"    @{ram_address}",   # Put address within pointer or temp segment in A
        "    D=M",              # Put value from pointer/temp in D, to push onto stack
        "    @SP",              # Set A to 0
        "    A=M",              # Set A to stack pointer
        "    M=D",              # Push value from pointer / temp on to stack
        "    @SP",              # Set up to increment stack pointer
        "    M=M+1",            # Actually increment stack pointer           
    ])


def write_pop_pointer_temp(lines: list[str], ram_address: int):
    lines.extend([
        "    @SP",              # Set up to decrement stack pointer
        "    M=M-1",            # Actually decrement stack pointer
        "    A=M",              # Put *value* of RAM[stack pointer] in A
        "    D=M",              # Pop value off stack into D
       f"    @{ram_address}",   # Put address within pointer or temp segment in A
        "    M=D",              # Put value we popped off stack into pointer/temp
    ])


def write_push_static(lines: list[str], stem:str, index: int):
    lines.extend([
       f"    @{stem}.{index}",  # Put static variable address in A
        "    D=M",              # Put value from address in D
        "    @SP",              # Set A to 0
        "    A=M",              # Set A to stack pointer
        "    M=D",              # Push value from pointer / temp on to stack
        "    @SP",              # Set up to increment stack pointer
        "    M=M+1",            # Actually increment stack pointer           
    ])


def write_pop_static(lines: list[str], stem:str, index: int):
    lines.extend([
        "    @SP",              # Set up to decrement stack pointer
        "    M=M-1",            # Actually decrement stack pointer
        "    A=M",              # Put *value* of RAM[stack pointer] in A
        "    D=M",              # Pop value off stack into D
       f"    @{stem}.{index}",  # Put static variable address in A
        "    M=D",              # Put value popped off stack into static variable
    ])


# ---- program flow ------------------------------------------------------------------------
def write_label(lines: list[str], stem: str, label: str) -> None:
    lines.extend([
        f"({stem}.{label})",    # Write label
    ])


def write_goto(lines: list[str], stem: str, label: str) -> None:
    lines.extend([
      f"    @{stem}.{label}",   # Put label in A
       "    0;JMP",             # Idiomatic way of writing unconditional jump in Hack assembly
    ])


def write_if(lines: list[str], stem: str, label: str) -> None:
    lines.extend([
        "    @SP",              # Set up to pop
        "    A=M",              # Set A to M[0]
        "    D=M",              # Pop into D
       f"    @{stem}.{label}",  # Put label in A
        "    D;JNE",            # Jump if the value we popped off the stack is not equal to zero
    ])


# ---- end of program
def write_end(lines: list[str]):
    """Write code that signals end of assembly program"""
    lines.extend([
        "(END)",
        "    @END",
        "    0;JMP",
    ])


VM_SEGMENT_ASM_SYMBOL_MAP = {
    "argument": "ARG",
    "local": "LCL",
    "this": "THIS",
    "that": "THAT",
}


def pointer_temp_ram_address(
    segment: Literal["pointer", "temp"],
    index: int,
):
    if segment not in ("pointer", "temp"):
        raise ValueError(
            f"pointer_temp_ram_address: Segment should be one of ('pointer', 'temp') but was: '{segment}'"
        )
    match segment:
        case "pointer":
            if index not in (0, 1):
                raise ValueError(
                    "pointer_temp_ram_address: when `segment` is 'pointer', "
                    f"`index` must be 0 or 1 but was: {index}"
                )
            return 3 + index
        case "temp":
            if index < 0 or index > 7:
                raise ValueError(
                    "pointer_temp_ram_address: when `segment` is 'temp', "
                    f"`index` must be int in range 0-7 but was: {index}"
                )
            return 5 + index


class CodeWriter:
    def __init__(
        self,
    ):
        self.lines = []
        self.jump_counter = 0
        self.stem: str = None

    def set_filename(self, filename: str | pathlib.Path):
        self.filename = pathlib.Path(filename)
        self.stem = self.filename.stem

    def write_arithmetic(self, command: str):
        match command:
            case "add":
                write_add(self.lines)
            case "sub":
                write_sub(self.lines)
            case "neg":
                write_neg(self.lines)
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
            case "not":
                write_not(self.lines)

    def write_push_pop(self, command: CommandType, segment: str, index: int):
        # N.B.: these are orded by "PUSH or POP, then, the order the book tells us to implement them in"
        match (command, segment):
            # ---- PUSH cases --------------------------------------------------
            case (CommandType.C_PUSH, "constant"):
                write_push_constant(self.lines, constant=index)
            case (
                (CommandType.C_PUSH, "argument") | 
                (CommandType.C_PUSH, "local" ) |
                (CommandType.C_PUSH, "this" ) |
                (CommandType.C_PUSH, "that" )
            ):
                symbol = VM_SEGMENT_ASM_SYMBOL_MAP[segment]
                write_push_lcl_arg_this_that(self.lines, symbol, index)
            case (
                (CommandType.C_PUSH, "pointer") |
                (CommandType.C_PUSH, "temp")
            ):
                ram_address = pointer_temp_ram_address(segment, index)
                write_push_pointer_temp(self.lines, ram_address)
            case (CommandType.C_PUSH, "static"):
                write_push_static(self.lines, self.stem, index)
            # ---- POP cases ---------------------------------------------------
            case (
                (CommandType.C_POP, "argument") |
                (CommandType.C_POP, "local") |
                (CommandType.C_POP, "this") |
                (CommandType.C_POP, "that")
            ):
                symbol = VM_SEGMENT_ASM_SYMBOL_MAP[segment]
                write_pop_lcl_arg_this_that(self.lines, symbol, index)
            case (
                (CommandType.C_POP, "pointer") |
                (CommandType.C_POP, "temp")
            ):
                ram_address = pointer_temp_ram_address(segment, index)
                write_pop_pointer_temp(self.lines, ram_address)
            case (CommandType.C_POP, "static"):
                write_pop_static(self.lines, self.stem, index)
            # ---- error handling ----------------------------------------------
            case _:
                raise ValueError(
                    f"CodeWriter.write_push_pop: Invalid combination of command and segment: {command}, {segment}"
                )

    def write_label(self, label: str) -> None:
        write_label(self.lines, self.stem, label)

    def write_goto(self, label: str) -> None:
        write_goto(self.lines, self.stem, label)

    def write_if(self, label: str) -> None:
        write_if(self.lines, self.stem, label)

    def write_comment(self, comment: str):
        self.lines.append(
            f"// {comment}"
        )

    def close(self):
        write_end(self.lines)
        with self.filename.open("w") as fp:
            fp.writelines(line + "\n" for line in self.lines)
