__all__ = [
    "generate_protocol",
]
import ast
import inspect
import textwrap
from collections.abc import Callable
from dataclasses import dataclass, field
from collections import defaultdict, OrderedDict


@dataclass
class _Method:
    args: tuple[object, ...] = field(default_factory=tuple)
    kwargs: tuple[tuple[str, object], ...] = field(default_factory=tuple)


@dataclass
class _Parameter:
    methods: dict[str, _Method] = field(default_factory=dict)


@dataclass
class _FunctionData:
    parameters: dict[str, _Parameter] = field(default_factory=defaultdict(_Parameter))


class _MethodCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self._method_calls = defaultdict(_Parameter)

    def visit_Call(self, node: ast.Call):
        try:
            param_name = node.func.value.id
            method_name = node.func.attr
            args = tuple(arg.value for arg in node.args)
            kwargs = tuple((kwarg.arg, kwarg.value.value) for kwarg in node.keywords)

        except AttributeError:
            self.generic_visit(node)

        method_data = _Method(args=args, kwargs=kwargs)
        self._method_calls[param_name].methods[method_name] = method_data

    def get_function_data(self) -> _FunctionData:
        return _FunctionData(parameters=dict(self._method_calls))


def _get_source(obj: object, /) -> str:
    source = inspect.getsource(obj)
    return textwrap.dedent(source).strip()


def _analyze_callables(func: Callable[..., object] | str, /) -> _FunctionData:
    source = _get_source(func) if isinstance(func, Callable) else func
    tree = ast.parse(source)
    callvisitor = _MethodCallVisitor()
    callvisitor.visit(tree)
    return callvisitor.get_function_data()


def _generate_argument_protocol_def(param_name: str) -> str:
    # Example:
    #   param_name = this_is_a_param_name
    #   return -> class ThisIsAParamName(Protocol)
    protocol = "class "
    for name_component in param_name.split("_"):
        protocol += name_component[0].upper() + name_component[1:]
    return f"{protocol}(Protocol):"


def _generate_argument_protocol_methods(methods: dict[str, _Method]) -> str:
    return "\n".join(
        [
            f"\n\tdef {method_name}(self, *args, **kwargs):\n\t\t..."
            for method_name in methods
        ]
    )


def _generate_protocol_string_list(
    argument_callables: _FunctionData, params: OrderedDict[str, inspect.Parameter]
) -> tuple[str]:
    protocols = []
    for param_name in params:
        protocol = _generate_argument_protocol_def(param_name)
        if param_name in argument_callables.parameters:
            arg_methods = argument_callables.parameters[param_name].methods
            protocol += _generate_argument_protocol_methods(arg_methods)
        else:
            protocol += "\n\t..."

        protocols.append(protocol.expandtabs(4))
    return protocols


def generate_protocols(
    # func comes in as str if called from cli otherwise the function was called with a Callable
    func: Callable[..., object] | str,
    # params is None if:
    #   1. called from cli and func simply has no params
    #   2. func not called from cli
    #    - Example: generate_protocols(some_func)
    params: OrderedDict[str, inspect.Parameter] | None = None,
    /,
) -> list[str]:
    argument_callables = _analyze_callables(func)

    # if function not called from cli
    if params is None and not isinstance(func, str):
        params = inspect.signature(func).parameters

    return _generate_protocol_string_list(argument_callables, params)
