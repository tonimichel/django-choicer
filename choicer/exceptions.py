from __future__ import unicode_literals


class MalformedChoiceDefinition(Exception):
    """
    Indicates that some choices do not provide the required keys.
    """


class ChoiceDoesNotExist(Exception):
    """
    Indicates that a requested choice - e.g. via self.get_by_name or self.get_by_value -
    does not exist.
    """


class ChoicesOutOfSyncError(Exception):
    """
    Indicates that the database and the defined choices are out of sync.
    This can happen if existing rows reference choices that habe been changed in value
    or removed.
    """

    def __init__(self, choice_value, field_name, model_class):
        self.choice_value = choice_value
        self.field_name = field_name
        self.model_class = model_class

    def __str__(self):
        return (
            'Your choices definition for field %(field_name)s on model %(model_name)s'
            'do not provide a choice with value %(value)s'
            'It seems as if your database stores choice values that are not '
            'represented in your current choices.\n\n'
            'This can happen if you change a choice value / remove a '
            'choice and your database still provides entries referencing the old choice.\n\n'
            'Either handle this exception explicitly or add a choice with value %(value)s'
            'and legacy=True to your choices definition.'
            'Legacy choices dont provide setters an dont turn up into your model field\'s '
            'choices.'
        ) % dict(
            value=self.value,
            field_name=self.field_name,
            model_name=str(self.model_class)
        )
