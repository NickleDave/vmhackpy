import argparse
import pathlib

from .code_writer import CodeWriter
from .parser import CommandType, Parser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        type=pathlib.Path,
        help="Source of VM code, either a .vm file or a directory containing .vm files"
    )
    args: argparse.Namespace = parser.parse_args()

    source = pathlib.Path(args.source)
    if source.is_dir():
        vm_files = sorted(source.glob("*.vm"))
        output_path = source / f"{source.stem}.asm"
    else:
        if not source.suffix == ".vm":
            raise ValueError(
                "Argument `source` should be either directory or filename with '.vm' suffix, "
               f"but suffix was: '{source.suffix}'"
            )
        vm_files = [source]
        output_path = source.parent / f"{source.stem}.asm"

    writer = CodeWriter()
    writer.set_filename(output_path)
    writer.write_init()

    for vm_file in vm_files:
        parser = Parser(vm_file)
        while parser.has_more_commands():
            parser.advance()
            writer.write_comment(parser.line)
            match parser.command_type:
                case CommandType.C_ARITHMETIC:
                    writer.write_arithmetic(parser.arg1)
                case CommandType.C_PUSH | CommandType.C_POP:
                    writer.write_push_pop(command=parser.command_type, segment=parser.arg1, index=parser.arg2)
                case CommandType.C_LABEL:
                    writer.write_label(label=parser.arg1)
                case CommandType.C_GOTO:
                    writer.write_goto(label=parser.arg1)
                case CommandType.C_IF:
                    writer.write_if(label=parser.arg1)
                case CommandType.C_FUNCTION:
                    writer.write_function(label=parser.arg1, num_args=parser.arg2)
                case CommandType.C_RETURN:
                    writer.write_return()

    writer.close()
