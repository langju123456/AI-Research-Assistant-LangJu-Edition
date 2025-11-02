def summarize_text(text: str, max_len: int = 500) -> str:
    text = text.strip().replace("\n", " ")
    return text[:max_len] + ("..." if len(text) > max_len else "")
