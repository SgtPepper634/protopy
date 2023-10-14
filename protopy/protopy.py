import ast
import inspect
import textwrap
from dataclasses import dataclass
from collections.abc import Callable


@dataclass
class _MethodCall:
    param_name: str
    method_name: str
    args: tuple[object]
    kwargs: tuple[tuple[str, object]]


class _MethodCallVisitor(ast.NodeVisitor):
    def __init__(self):
        self._method_calls = []

    @property
    def method_calls(self):
        return self._method_calls

    def visit_Call(self, node):
        if isinstance(node, ast.Call):
            try:
                method_call = _MethodCall(
                    param_name=node.func.value.id,
                    method_name=node.func.attr,
                    args=tuple((arg.value for arg in node.args)),
                    kwargs=tuple((kwarg.arg, kwarg.value.value) for kwarg in node.keywords),
                )

                self.method_calls.append(method_call)

            except AttributeError:
                self.generic_visit(node)


def _get_source(obj: object, /) -> str:
    source = inspect.getsource(obj)
    return textwrap.dedent(source).strip()


def _analyze_callable(func: Callable[..., object], /) -> list[_MethodCall]:
    source = _get_source(func)
    tree = ast.parse(source)
    callvisitor = _MethodCallVisitor()
    callvisitor.visit(tree)
    return callvisitor.method_calls
