def validate_enum(value, allowed):
    if value not in allowed:
        raise ValueError(f"{value} not in {allowed}")


def validate_range(value, min_value=None, max_value=None):
    try:
        num = float(value)
    except ValueError:
        raise ValueError("Value must be numeric")

    if min_value is not None and num < min_value:
        raise ValueError(f"{num} below minimum {min_value}")

    if max_value is not None and num > max_value:
        raise ValueError(f"{num} above maximum {max_value}")