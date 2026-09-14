def bold(text: str, ) -> str:
    return f"<b>{text}</b>"

def italic(text: str, ) -> str:
    return f"<i>{text}</i>"

def underline(text: str, ) -> str:
    return f"<u>{text}</u>"

def strikethrough(text: str, ) -> str:
    return f"<strike>{text}</strike>"

def code(text: str, ) -> str:
    return f"<code>{text}</code>"

def quote(text: str, ) -> str:
    return f"<quote>{text}</quote>"

def link(text: str, href: str) -> str:
    return f'<a href="{href}">{text}</a>'

