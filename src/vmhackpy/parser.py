import enum
import pathlib
import re

# taken from my py-hack-assembler;
# IIUC the specification in EoCS chapter 8
# for VM labels is exactly the same as asm symbols,
# perhaps not surprisingly
LabelPattern = re.compile(r"""
^
([a-zA-Z_.$:]     # first char must be alpha or special
[0-9a-zA-Z_.$:]*)* # subsequent chars can also be numeric  
$
""", re.VERBOSE
)


class ParseError(BaseException):
    pass


class CommandType(enum.Enum):
    C_ARITHMETIC = 0
    C_PUSH = 1
    C_POP = 2
    C_LABEL = 3
    C_GOTO = 4
    C_IF = 5
    C_FUNCTION = 6
    C_RETURN = 7
    C_CALL = 8


class Parser:
    def __init__(
        self,
        input_file,
    ):
        input_file = pathlib.Path(input_file)
        with input_file.open("r") as fp:
            self.lines = fp.read().splitlines()
        self.command = None
        self.line_no = -1

        self._command_type = None
        self._line = None
        self._arg1 = None
        self._arg2 = None

    def has_more_commands(self):
        if self.line_no < len(self.lines) - 1:
            return True
        return False

    def advance(self):
        if not self.has_more_commands():
            raise ValueError(
                f"No more commands"
            )

        self.line_no += 1

        is_empty_line_or_comment = True
        while is_empty_line_or_comment:
            line = self.lines[self.line_no]
            if line.split() == []:  # if stripping whitespace returns an empty list ->
                # then we must have an empty line
                self.line_no += 1
                continue

            line_no_comment = line.split("//")[0]
            if line_no_comment.split() == []:
                # -> whole line is a comment
                self.line_no += 1
                continue
            else:
                line = line_no_comment
                is_empty_line_or_comment = False

        self._line = line
        command_parts = line.split()  # remove whitespace
        if len(command_parts) > 3:
            raise ParseError(
                f"Greater than 3 parts to command {self.line_no}: {line}"
            )

        command = command_parts[0]
        match command:
            case "add" | "sub" | "eq" | "gt" | "lt" | "and" | "or" | "neg" | "not":
                if len(command_parts) > 1:
                    raise ValueError(
                        f"Command '{command_parts[0]}' should not have any arguments, "
                        f"but had {len(command_parts) - 1}"
                    )

                self._command_type = CommandType.C_ARITHMETIC
                self._arg1 = command
                self._arg2 = None
            case "push" | "pop":
                if len(command_parts) != 3:
                    raise ValueError(
                        f"Command '{command_parts[0]}' should have 2 arguments, "
                        f"but had {len(command_parts) - 1}"
                    )

                match command:
                    case "push":
                        self._command_type = CommandType.C_PUSH
                    case "pop":
                        self._command_type = CommandType.C_POP
                _, segment, index = command_parts
                self._arg1 = segment
                try:
                    self._arg2 = int(index)
                except ValueError as e:
                    raise(
                        "Parser.advance: could not convert arg2 to integer: {index}"
                    ) from e
            case ("label" | "goto" | "if-goto"):
                if len(command_parts) != 2:
                    raise ValueError(
                        f"Command '{command_parts[0]}' should have 1 argument `label`, "
                        f"but had {len(command_parts) - 1}"
                    )
                match command:
                    case "label":
                        self._command_type = CommandType.C_LABEL
                    case "goto":
                        self._command_type = CommandType.C_GOTO
                    case "if-goto":
                        self._command_type = CommandType.C_IF

                label: list[str] = LabelPattern.findall(command_parts[1])
                if len(label) == 1:
                    label = label[0]
                else:
                    raise ParseError(
                        f"Line {self.line_no}: '{command_parts[1]}' is not a valid label:\n{command}"
                    )

                self._arg1 = label  # label
                self._arg2 = None
            case _:
                raise ParseError(f"Unknown command: '{command}'")

    @property
    def line(self):
        return self._line

    @property
    def command_type(self):
        return self._command_type

    @property
    def arg1(self):
        return self._arg1

    @property
    def arg2(self):
        return self._arg2
