__all__ = [
    "generate_protocol",
]

import ast
import inspect
import textwrap
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class _Method:
    args: List[object]
    kwargs: Tuple[str, object] = field(default_factory=tuple)


@dataclass
class _Parameter:
    methods: Dict[str, _Method] = field(default_factory=dict)


@dataclass
class _FunctionData:
    parameters: Dict[str, _Parameter] = field(default_factory=defaultdict(_Parameter))


class _MethodCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self._method_calls = defaultdict(_Parameter)

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

        method_data = _Method(args=args, kwargs=kwargs)
        self.method_calls[param_name].methods[method_name] = method_data

    def get_function_data(self) -> _FunctionData:
        return _FunctionData(parameters=dict(self.method_calls))


def _get_source(obj: object, /) -> str:
    source = inspect.getsource(obj)
    return textwrap.dedent(source).strip()


def _analyze_callables(func: Callable[..., object], /) -> _FunctionData:
    source = _get_source(func)
    tree = ast.parse(source)
    callvisitor = _MethodCallVisitor()
    callvisitor.visit(tree)
    return callvisitor.get_function_data()


def generate_argument_protocol_def(param_name: str) -> str:
    protocol = "class "
    for name_component in param_name.split("_"):
        protocol += name_component[0].upper() + name_component[1:]
    return f"{protocol}(Protocol):"


def generate_argument_protocol_methods(methods: _Parameter) -> str:
    return "\n".join(
        [
            f"\n\tdef {method_name}(self, *args, **kwargs):\n\t\t..."
            for method_name in methods
        ]
    )


def generate_protocols(func: Callable[..., object], /) -> list[str]:
    argument_callables = _analyze_callables(func)
    params = inspect.signature(func).parameters
    protocols = []
    for param_name in params:
        protocol = generate_argument_protocol_def(param_name)
        if param_name in argument_callables.parameters:
            protocol += generate_argument_protocol_methods(
                argument_callables.parameters[param_name].methods
            )
        else:
            protocol += "\n\t..."

        protocols.append(protocol.expandtabs(4))

    return protocols
