import hashlib
import pydenticon


def generate_avatar(email: str) -> bytes:
    foreground = [
        "#e05923",
        "#d9534f",
        "#337ab7",
        "#006400",
        "#5bc0de",
        "#333",
    ]
    blocks = (10, 10)
    size = (250, 250)
    background = "rgb(255, 255, 255)"
    generator = pydenticon.Generator(*blocks,
                                     digest=hashlib.sha1,
                                     foreground=foreground,
                                     background=background)
    return generator.generate(email, *size,
                              output_format="png")
