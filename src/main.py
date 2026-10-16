import argparse
import pathlib

from .code_writer import CodeWriter
from .parser import Parser


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "name",
        type=pathlib.Path,
        help="Name, of either a .vm file or a directory containing .vm files"
    )
    args: argparse.Namespace = parser.parse_args()

    name = pathlib.Path(args.name)
    if name.is_dir():
        vm_files = sorted(name.glob("*.vm"))
        
    else:
        if not name.suffix == ".vm":
            raise ValueError(
                "Argument `name` should be directory or filename with '.vm' suffix, "
               f"but suffix was: '{name.suffix}'"
            )
        vm_files = [name]
    # next line works regardless of whether we have a dir of files or a single file
    output_filename = f"{name.name}.asm"

    writer = CodeWriter()
    writer.set_filename(output_filename)
    for vm_file in vm_files:
    