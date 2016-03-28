from . import exceptions

def get_choice_getter_func(field_name, choicer):

    def func(self):
        value = getattr(self, field_name)
        try:
            return choicer.get_by_value(value)
        except exceptions.ChoiceDoesNotExist:
            raise exceptions.ChoicesOutOfSyncError(value, field_name, type(self))
    return func


def get_getter_func(field_name, value):
    """
    Returns the getter function patched to the target model.
    :param field_name: the name of the field storing the choice
    :param value: the value to check against
    :return: function
    """

    def func(self):
        return getattr(self, field_name) == value

    return func


def get_setter_func(field_name, value):
    """
    Returns the setter function patched to the target model.
    :param field_name: the name of the field storing the choice
    :param value: the value to set
    :return: function
    """

    def func(self, commit=False):
        setattr(self, field_name, value)
        if commit:
            self.save()

    return func
