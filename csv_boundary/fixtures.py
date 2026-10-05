"""Trusted inert strings; no formula evaluation or consumer application."""


def demo_cases() -> list[tuple[str, list[list[str]]]]:
    return [
        ("ordinary text", [["name", "value"], ["sample", "text"]]),
        ("arithmetic-looking text", [["=1+1", "-1"]]),
        ("quoted delimiters", [["a,b", 'a"b'], ["line\nbreak", "semi;colon"]]),
        ("leading space and control", [[" =1+1", "\t=1+1"]]),
        ("fullwidth and format", [["＝1+1", "\u200b=1+1"]]),
        ("empty and existing apostrophe", [["", "'=1+1"]]),
    ]
