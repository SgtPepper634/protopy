import ast
import inspect
import textwrap
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol


@dataclass
class _MethodCall:
    param_name: str
    method_name: str
    args: tuple[object, ...]
    kwargs: dict[str, object]


class _MethodCallVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.method_calls: list[_MethodCall] = []

    def visit_Call(self, node: ast.Call) -> None:
        match node:
            case ast.Call(
                func=ast.Attribute(
                    value=ast.Name(id=param_name),
                    attr=method_name,
                ),
                args=args,
                keywords=keywords,
            ):
                # TODO: Figure out how to get the arguments and keyword arguments
                # out of args and keywords, respectively.

                positional_args = []
                for expr_node in args:
                    print(ast.dump(expr_node, indent=4))

                keyword_args = {}
                for keyword_node in keywords:
                    print(ast.dump(keyword_node, indent=4))

                method_call = _MethodCall(
                    param_name=param_name,
                    method_name=method_name,
                    args=tuple(positional_args),
                    kwargs=keyword_args,
                )

                self.method_calls.append(method_call)

        # TODO: Determine if we need to call the generic_visit method.
        self.generic_visit(node)


def _get_source(obj: object, /) -> str:
    source = inspect.getsource(obj)
    return textwrap.dedent(source).strip()


def _analyze_callable(func: Callable[..., object], /) -> list[_MethodCall]:
    source = _get_source(func)
    tree = ast.parse(source)
    visitor = _MethodCallVisitor()
    visitor.visit(tree)
    return visitor.method_calls


def generate_protocol(func: Callable[..., object], param_name: str, /) -> str:
    # all_method_calls = _analyze_callable(func)
    # pprint.pprint(f"{all_method_calls=}")

    # print()

    # method_calls = [mc for mc in all_method_calls if mc.param_name == param_name]
    # pprint.pprint(f"{method_calls=}")

    # # Need to dedupe method_calls, probably?
    raise NotImplementedError


if __name__ == "__main__":
    # Inspiration from unittest.mock.MagicMock:
    # from unittest.mock import MagicMock
    # mock_a = MagicMock()
    # some_function(mock_a)
    # print(mock_a.method_calls)
    # method_call = mock_a.method_calls[0]
    # print(method_call.args)
    # print(method_call.kwargs)

    def some_function(a):
        print("Hello from some_function!")

        a.foo(1)
        a.foo(baz=2, qux=False)

        raise RuntimeError("This should never be called!")

    # method_calls = _analyze_callable(some_function)
    # pprint.pprint(method_calls)

    # The data in method_calls is enough to generate:
    # class AProtocol(Protocol):
    #     def foo(self, *args: object, **kwargs: object) -> object:
    #         ...

    _analyze_callable(some_function)
