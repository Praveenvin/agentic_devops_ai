def label_commit(message: str) -> str:
    message = message.lower()
    if "fix" in message or "bug" in message:
        return "bugfix"
    elif "feature" in message or "add" in message:
        return "feature"
    elif "refactor" in message:
        return "refactor"
    else:
        return "other"
