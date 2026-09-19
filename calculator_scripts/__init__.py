from importlib import import_module
from pkgutil import walk_packages


def is_calculator_object(value) -> bool:
    """Identify calculator/table objects by the methods used by the app."""
    return (
        not isinstance(value, type)
        and isinstance(getattr(value, "title", None), str)
        and callable(getattr(value, "initialize_session_state", None))
        and callable(getattr(value, "render_main_canvas", None))
    )


def discover_calculators() -> dict:
    discovered = {}
    seen_objects = set()

    # Recursively find every module inside calculator_scripts.
    for module_info in walk_packages(
        path=__path__,
        prefix=f"{__name__}.",
    ):
        if module_info.ispkg:
            continue

        module = import_module(module_info.name)

        for value in vars(module).values():

            # Support dictionaries such as data_table_calculators.
            if isinstance(value, dict):
                candidates = value.values()
            else:
                candidates = [value]

            for calculator in candidates:
                if not is_calculator_object(calculator):
                    continue

                # Prevent the same object from being registered twice.
                object_id = id(calculator)
                if object_id in seen_objects:
                    continue

                seen_objects.add(object_id)

                title = calculator.title.strip()

                if not title:
                    continue

                if title in discovered:
                    raise ValueError(
                        f"Duplicate calculator title found: {title!r}"
                    )

                discovered[title] = calculator

    return dict(
        sorted(
            discovered.items(),
            key=lambda item: item[0].casefold(),
        )
    )


CALCULATORS = discover_calculators()