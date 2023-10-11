import textwrap

import pytest

import protopy

from sys import settrace


def test_generate_protocol_1() -> None:
    def func(arg):
        return arg

    expected = textwrap.dedent("""\
        class Arg(Protocol):
            ...
    """)

    result = protopy.generate_protocol(func, "arg")

    assert result == expected


def test_generate_protocol_2() -> None:
    def func(arg):
        return arg.foo()

    # NOTE(Will): We might be able to also deduce what the return type
    # of `foo` is and add it to the protocol. But let's not do that for
    # now.
    expected = textwrap.dedent("""\
        class Arg(Protocol):
            def foo(self):
                ...
    """)

    result = protopy.generate_protocol(func, "arg")

    assert result == expected

''' TODO: turn contents of old main.py into test

def test_generate_protocol_3() -> None:
    class David:
        def plays_video_games(self):
            return True

        def watches_movies(self):
            return True

        def return_name(self):
            return "David"


    david = David()


    def who_is_this(person: David, age=53):
        return person


    # set tracing function
    settrace(protopy.callable_tracer)

    who_is_this(david)

'''
