import re
from decimal import Decimal, InvalidOperation


def _to_decimal(value):
    if value is None:
        return None
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    if not match:
        return None
    try:
        return Decimal(match.group(0))
    except InvalidOperation:
        return None


def _parse_range(normal_range):
    text = (normal_range or "").strip().replace(" ", "")
    if not text:
        return None

    between = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*-\s*(-?\d+(?:\.\d+)?)", text)
    if between:
        low = Decimal(between.group(1))
        high = Decimal(between.group(2))
        return ("between", min(low, high), max(low, high))

    less_than = re.fullmatch(r"<=?(-?\d+(?:\.\d+)?)", text)
    if less_than:
        return ("lt", Decimal(less_than.group(1)))

    greater_than = re.fullmatch(r">=?(-?\d+(?:\.\d+)?)", text)
    if greater_than:
        return ("gt", Decimal(greater_than.group(1)))

    return None


def auto_flag_result(test, result_value):
    value = _to_decimal(result_value)
    parsed = _parse_range(getattr(test, "normal_range", ""))
    if value is None or parsed is None:
        return "NORMAL"

    kind = parsed[0]
    if kind == "between":
        low, high = parsed[1], parsed[2]
        if low <= value <= high:
            return "NORMAL"
        critical_low = low * Decimal("0.5")
        critical_high = high * Decimal("1.5")
        if value < critical_low or value > critical_high:
            return "CRITICAL"
        return "L" if value < low else "H"

    threshold = parsed[1]
    if kind == "lt":
        if value < threshold:
            return "NORMAL"
        critical_threshold = threshold * Decimal("1.5")
        return "CRITICAL" if value >= critical_threshold else "H"

    if value > threshold:
        return "NORMAL"
    critical_threshold = threshold * Decimal("0.5")
    return "CRITICAL" if value <= critical_threshold else "L"
