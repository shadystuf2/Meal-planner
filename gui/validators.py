"""
Small input-validation helpers shared by the GUI screens.

Each function takes a raw string from a Tkinter Entry widget and
either returns the parsed/cleaned value, or raises ValueError with a
human-readable message. The screens catch that ValueError and show it
to the user with messagebox.showerror, instead of letting bad input
reach the database (or crash the app with an unhandled exception).
"""


def require_non_empty(value, field_name):
    """Strip whitespace and return the value, or raise if it's empty."""
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} cannot be empty.")
    return value


def require_positive_number(value, field_name):
    """Parse value as a float and require it to be greater than zero."""
    try:
        number = float(value)
    except ValueError:
        raise ValueError(f"{field_name} must be a number.")

    if number <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return number


def require_positive_int(value, field_name):
    """Parse value as a whole number and require it to be greater than zero."""
    try:
        number = int(value)
    except ValueError:
        raise ValueError(f"{field_name} must be a whole number.")

    if number <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return number


def require_non_negative_int(value, field_name):
    """Parse value as a whole number and require it to be zero or more."""
    try:
        number = int(value)
    except ValueError:
        raise ValueError(f"{field_name} must be a whole number.")

    if number < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    return number


def optional_positive_int(value, field_name):
    """Like require_positive_int, but a blank value means "not set" (returns None)."""
    value = value.strip()
    if not value:
        return None
    return require_positive_int(value, field_name)


def optional_non_negative_int(value, field_name):
    """Like require_non_negative_int, but a blank value means "not set" (returns None)."""
    value = value.strip()
    if not value:
        return None
    return require_non_negative_int(value, field_name)
