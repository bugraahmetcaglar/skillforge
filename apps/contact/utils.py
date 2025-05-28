import hashlib
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
        case d if d.startswith("90") and len(d) == 12:
            # Already has country code: 905321234567
            return f"+{d}"

        case d if d.startswith("05") and len(d) == 11:
            # Turkish with leading zero: 05321234567
            return f"+90{d[1:]}"

        case d if d.startswith("5") and len(d) == 10:
            # Turkish mobile: 5321234567
            return f"+90{d}"

        case _:
            # Non-Turkish formats: keep original input
            return phone


def generate_external_id(data: str, source: str) -> str:
    clean_str = data.strip().lower()

    # Generate MD5 hash
    hash_object = hashlib.md5(clean_str.encode("utf-8"))
    return f"{source}_sf_{hash_object.hexdigest()}"
