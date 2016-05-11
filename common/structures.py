from enum import unique, Enum


@unique
class ChoiceEnum(Enum):
    """
    ChoiceEnum is used when you want to use an enumeration for the choices of an integer django field.
    """
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
