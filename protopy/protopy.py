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
        self._method_calls = {}
        '''
        dictionary structure
        {
            param_name: {
                    method_name: {
                            args: list[tuple[object]]
                            kwargs: list[tuple(tuple(str, object))]
                    }
            }

        }
        '''

    @property
    def method_calls(self):
        return self._method_calls

    def visit_Call(self, node):
        if not isinstance(node, ast.Call):
            return

        try:
            param_name = node.func.value.id
            method_name = node.func.attr
            args = tuple(arg.value for arg in node.args)
            kwargs = tuple((kwarg.arg, kwarg.value.value) for kwarg in node.keywords)

            if param_name not in self.method_calls:
                self.method_calls[param_name] = {}

            if method_name not in self.method_calls[param_name]:
                self.method_calls[param_name][method_name] = {"args": [], "kwargs": []}

            self.method_calls[param_name][method_name]["args"].append(args)
            self.method_calls[param_name][method_name]["kwargs"].append(kwargs)

        except AttributeError:
            self.generic_visit(node)


def _get_source(obj: object, /) -> str:
    source = inspect.getsource(obj)
    return textwrap.dedent(source).strip()


def _analyze_argument_callables(func: Callable[..., object], /) -> list[_MethodCall]:
    source = _get_source(func)
    tree = ast.parse(source)
    callvisitor = _MethodCallVisitor()
    callvisitor.visit(tree)
    return callvisitor.method_calls
