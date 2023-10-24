import protopy
import textwrap


def test_generate_protocol_1() -> None:
    def func(arg):
        return arg

    expected = textwrap.dedent(
        """\
        class Arg(Protocol):
            ...
    """
    ).strip()

    result = protopy.generate_protocols(func)[0]

    assert result == expected


def test_generate_protocol_2() -> None:
    def func(arg):
        return arg.foo()

    # NOTE(Will): We might be able to also deduce what the return type
    # of `foo` is and add it to the protocol. But let's not do that for
    # now.
    expected = textwrap.dedent(
        """\
        class Arg(Protocol):
            def foo(self, *args, **kwargs):
                ...
    """
    ).strip()

    result = protopy.generate_protocols(func)[0]
    assert result == expected
