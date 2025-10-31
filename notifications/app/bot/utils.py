def escape_mdv2(text: str | None) -> str:
    """
    Экранирование специальных символов MarkdownV2
    """

    if not text:
        return ""

    md_chars = r"\_*[]()~`>#+-=|{}.!"

    for ch in md_chars:
        text = text.replace(ch, '\\' + ch)

    return text


def prepare_expandable(caption: str | None, text: str | None) -> str:
    """
    Подготовка текста для Expandable block (для Markdown V2)
    """

    if not text:
        return ""

    caption = escape_mdv2(caption) + "\n" if caption else ""

    lines = text.split("\n")
    modified_lines = [">" + escape_mdv2(line) for line in lines]
    modified_text = "\n".join(modified_lines)

    return f"\n**>{caption}{modified_text}||"
