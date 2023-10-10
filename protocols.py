from textwrap import dedent
from collections.abc import Iterable, Callable


def generate_protocol_name(class_name: str, method_name: str) -> str:
    protocol_name = class_name + "_"
    for name_component in method_name.split("_"):
        protocol_name += name_component[0].upper() + name_component[1:]

    return protocol_name


def write_protocols(method_list: Iterable[tuple[str, Callable]]) -> None:
    with open("main.py", "a+") as file:  # TODO: Write Protocols in the proper file
        for method_name, method in method_list:
            class_name = method.__self__.__class__.__name__
            protocol_name = generate_protocol_name(class_name, method_name)

            file.write(
                dedent(
                    f"""\
                        class {protocol_name}(Protocol):
                            def {method_name}(self):
                                ...
                    """
                )
            )

        file.close()
