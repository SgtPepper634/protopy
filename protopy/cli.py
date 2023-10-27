import ast
import sys
import inspect
import protopy
import argparse
import textwrap
from typing import Callable
from collections.abc import Sequence
from collections import OrderedDict


_parser = argparse.ArgumentParser()
_parser.add_argument("file", type=argparse.FileType("r"), default="-", nargs="?")
_parser.add_argument("--output", "-o", type=argparse.FileType("w"), default="w")


def extract_functions(code: str) -> list[Callable]:
    tree = ast.parse(code)

    # recursively walk through AST tree and retrieve function definitions
    function_nodes = [
        node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
    ]

    extracted_functions: list[
        tuple(str, OrderedDict[str, inspect.Parameter] | None)
    ] = []

    for node in function_nodes:
        function_str = textwrap.dedent(ast.unparse(node)).strip()

        # compile function code and execute to retrieve params if they exist
        function_code = compile(ast.Module([node], []), filename="<ast>", mode="exec")
        exec(function_code)
        extracted_function = locals()[node.name]

        params = inspect.signature(extracted_function).parameters

        if len(params) == 0:
            params = None

        extracted_functions.append((function_str, params))

    return extracted_functions


def main(argv: Sequence[str] | None = None, /) -> None:
    args = _parser.parse_args(argv)
    with args.file as input_file:
        content = input_file.read()
        extracted_functions = extract_functions(content)
    with args.output as outputfile:
        protocols: list[str] = ["from typing import Protocol"]
        for source in extracted_functions:
            protocols.extend(iter(protopy.generate_protocols(*source)))

        outputfile.write("\n\n".join(protocols))


if __name__ == "__main__":
    main(sys.argv[1:])
