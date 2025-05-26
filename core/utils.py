from __future__ import annotations

from typing import Any


def recursive_getattr(obj: Any, attr_path: str, default: Any = None) -> Any:
    """Recursively get nested attributes from an object using dot notation.

    Args:
        obj: The object to get attributes from
        attr_path: Dot-separated attribute path (e.g., "user.profile.name")
        default: Default value to return if attribute doesn't exist

    Returns:
        The value of the nested attribute or default value

    Examples:
        >>> user = User(profile=Profile(name="John"))
        >>> recursive_getattr(user, "profile.name")
        "John"
        >>> recursive_getattr(user, "profile.age", 25)
        25
        >>> recursive_getattr(user, "nonexistent.attr", "default")
        "default"
    """
    try:
        # Split the attribute path by dots
        attrs = attr_path.split(".")

        # Start with the original object
        current_obj = obj

        # Traverse through each attribute in the path
        for attr in attrs:
            if current_obj is None:
                return default

            # Handle list/dict access with bracket notation
            if "[" in attr and "]" in attr:
                attr_name, index_part = attr.split("[", 1)
                index = index_part.rstrip("]")

                # Get the attribute first
                if attr_name:
                    current_obj = getattr(current_obj, attr_name, None)
                    if current_obj is None:
                        return default

                # Handle index access
                try:
                    if index.isdigit():
                        # Numeric index for lists
                        current_obj = current_obj[int(index)]
                    else:
                        # String key for dicts
                        index = index.strip("'\"")  # Remove quotes if present
                        current_obj = current_obj[index]
                except (KeyError, IndexError, TypeError):
                    return default
            else:
                # Regular attribute access
                current_obj = getattr(current_obj, attr, None)
                if current_obj is None:
                    return default

        return current_obj

    except (AttributeError, TypeError):
        return default
