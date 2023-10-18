__all__ = [
    "generate_protocol",
]

import ast
import inspect
import textwrap
from dataclasses import dataclass
from collections.abc import Callable


@dataclass(frozen=True)
class _MethodCall:
    param_name: str
    method_name: str
    args: tuple[object, ...]
    kwargs: tuple[tuple[str, object], ...]


class _MethodCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self._method_calls = {}
        # dictionary structure
        # {
        #    param_name: {
        #        method_name: {
        #                args: list[tuple[object]]
        #                kwargs: list[tuple(tuple(str, object))]
        #        }
        #    }
        # }

    @property
    def method_calls(self):
        return self._method_calls

    def visit_Call(self, node: ast.Call):
        try:
            param_name = node.func.value.id
            method_name = node.func.attr
            args = tuple(arg.value for arg in node.args)
            kwargs = tuple((kwarg.arg, kwarg.value.value) for kwarg in node.keywords)

        except AttributeError:
            self.generic_visit(node)

        self.method_calls.setdefault(param_name, {})
        self.method_calls[param_name].setdefault(
            method_name, {"args": [], "kwargs": []}
        )

        self.method_calls[param_name][method_name]["args"].append(args)
        self.method_calls[param_name][method_name]["kwargs"].append(kwargs)


def _get_source(obj: object, /) -> str:
    source = inspect.getsource(obj)
    return textwrap.dedent(source).strip()


def _analyze_callables(func: Callable[..., object], /) -> list[_MethodCall]:
    source = _get_source(func)
    tree = ast.parse(source)
    callvisitor = _MethodCallVisitor()
    callvisitor.visit(tree)
    return callvisitor.method_calls


def generate_protocols(func: Callable[..., object], /) -> list[str]:
    argument_callables = _analyze_callables(func)
    params = inspect.signature(func).parameters
    protocols = []
    for param_name in params:
        protocol = "class "
        for name_component in param_name.split("_"):
            protocol += name_component[0].upper() + name_component[1:]
        protocol += "(Protocol):"
        try:
            print(argument_callables[param_name])
            for method_name in argument_callables[param_name]:
                protocol += f"\n\tdef {method_name}(self, *args, **kwargs):\n\t\t..."
        except KeyError:
            protocol += "\n\t..."
        protocols.append(protocol.expandtabs(4))

    return protocols
