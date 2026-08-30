
def split_in_lines(content: str, max_width: int = 75) -> list[str]:
    line_char_count: int = 0
    line: str = ""
    
    content_lines: list[str] = []
    words = content.split(" ")
    for idx, word in enumerate(words):
        line += " " + word
        line_char_count += len(word)
        if idx + 1 >= len(words):
            content_lines.append(line)
            break

        if line_char_count >= max_width:
            content_lines.append(line)
            line_char_count = 0
            line = ""

    return content_lines