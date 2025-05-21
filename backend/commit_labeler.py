
def label_commit(message):
    if "fix" in message.lower():
        return "bugfix", "core", "medium"
    elif "feature" in message.lower():
        return "feature", "ui", "high"
    return "general", "misc", "low"
