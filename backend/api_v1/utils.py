def normalize_phone(phone: str) -> str:
    """Extracts only digits from a phone number string."""
    if not phone:
        return ""
    return ''.join(filter(str.isdigit, str(phone)))
