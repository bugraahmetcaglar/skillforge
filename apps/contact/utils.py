import re


def normalize_phone_number(phone: str) -> str:
    """Normalize Turkish phone numbers to +90XXXXXXXXXX format
    Non-Turkish numbers are kept in their original format

    Used by contact import services (vCard, CSV, Excel, JSON, etc.)

    Args:
        phone: Raw phone number string

    Returns:
        Normalized phone number or original if not Turkish format

    Examples:
        >>> normalize_phone_number('05321234567')
        '+905321234567'
        >>> normalize_phone_number('532-123-45-67')
        '+905321234567'
        >>> normalize_phone_number('+18042003448')
        '+18042003448'
        >>> normalize_phone_number('123456')
        '123456'
        >>> normalize_phone_number('0532 123 45 67')
        '+905321234567'
        >>> normalize_phone_number('0212 555 1234')
        '+902125551234'
    """
    if not phone:
        return ""

    # Handle international format (already has +)
    if phone.strip().startswith("+"):
        # Clean everything except digits after +
        digits = re.sub(r"[^\d]", "", phone[1:])
        return f"+{digits}" if digits else phone

    # Extract only digits for domestic numbers
    digits = re.sub(r"[^\d]", "", phone)
    if not digits:
        return phone

    # Turkish phone number pattern matching
    match digits:
        # Remove or change here if you want to keep non-Turkish formats
        case d if d.startswith("90") and len(d) == 12:
            # Already has country code: 905321234567
            return f"+{d}"

        # Remove or change here if you want to keep non-Turkish formats
        case d if d.startswith("05") and len(d) == 11:
            # Turkish with leading zero: 05321234567
            return f"+90{d[1:]}"

        # Remove or change here if you want to keep non-Turkish formats
        case d if d.startswith("5") and len(d) == 10:
            # Turkish mobile: 5321234567
            return f"+90{d}"

        # Remove or change here if you want to keep non-Turkish formats
        case d if d.startswith("0") and len(d) == 11:
            # Turkish landline with leading zero: 02121234567
            return f"+90{d[1:]}"

        case _:
            # Non-Turkish formats: keep original input
            return phone
