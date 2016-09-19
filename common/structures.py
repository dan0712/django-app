from enum import unique, Enum


@unique
class ChoiceEnum(Enum):
    """
    ChoiceEnum is used when you want to use an enumeration for the choices of an integer django field.
    If you want to give the choice a human name, either create the enum normally, but with the value, use a tuple with
    the id as the first element, and the human name as the second. Alternatively, override the __init__ and set the
    human_name somewhere within that.
    """

    def __new__(cls, *args):
        """
        Override __new__ so we can use the normal "value" semantics for the enum, even if people pass in other data.
        :param args: All the extra data the user wants to create the enum item with.
        :return: The new enum object.
        """
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, id, human_name=None):
        """
        Default implementation which sets the second item to the human name for the enum. Override for anything special.
        :param id:
        :param human_name:
        """
        if human_name is not None:
            self._human_name_ = human_name

    @property
    def human_name(self):
        return getattr(self, '_human_name_', self.name)

    @classmethod
    def choices(cls):
        return [(item.value, item.human_name) for item in cls]
