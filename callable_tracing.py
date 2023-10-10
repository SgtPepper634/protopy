import inspect
from protocols import write_protocols
from collections.abc import Iterable, Callable


def is_user_defined_method(method) -> bool:
    # TODO: handle decorator functions
    return inspect.isroutine(method) and not inspect.isbuiltin(method)


def get_arguments_user_defined_methods(arg_value) -> Iterable[tuple[str, Callable]]:
    # filter out builtin methods and return a list of only bound methods created by the user
    return [
        method
        for method in inspect.getmembers(arg_value)
        if is_user_defined_method(method[1])
    ]


# local trace function which returns itself
def callable_tracer(frame, event, arg=None):
    # https://www.geeksforgeeks.org/python-sys-settrace/
    # https://docs.python.org/3/library/inspect.html
    # https://docs.python.org/3/library/sys.html#sys.settrace

    # extracts the line number where the function was called
    line_no = frame.f_back.f_lineno
    # extracts frame code
    code = frame.f_code
    # extracts name of function that was called
    func_name = code.co_name
    # extracts argument count
    arg_count = code.co_argcount
    # extracts argument and local variable names
    arg_names = code.co_varnames

    custom_methods = None

    match event:
        case "call":
            for arg_name in arg_names[:arg_count]:
                if arg_name == "self":
                    continue
                arg_value = frame.f_locals[arg_name]
                custom_methods = get_arguments_user_defined_methods(arg_value)
        case "return":
            custom_methods = get_arguments_user_defined_methods(arg)
        case "line":
            return
        case _:
            return

    write_protocols(custom_methods)

    return callable_tracer
