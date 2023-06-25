def format_email_to_key(email: str) -> str:
    return email.replace("@", "_").replace(".", "_")
