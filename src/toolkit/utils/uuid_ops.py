import uuid


def create_uuid() -> str:
    """
    Generate a new UUID.

    Returns:
        String representation of a UUID
    """
    return str(uuid.uuid4())