from __future__ import unicode_literals, print_function
from . import factory
from . import exceptions


__all__ = ['Choicer']


class Choicer(object):

    # stores the mandatory choice fields
    _mandatory_keys = ['name', 'value', 'verbose_name']


    def __init__(self, choice_list):
        self._ensure_choices_format(choice_list)
        self._choice_list = choice_list
        self._choice_name_dict = self._list_to_dict(choice_list, 'name')
        self._choice_value_dict = self._list_to_dict(choice_list, 'value')

    def _get_func_name(self, prefix, field_name, entry):
        """
        Constructs the function name to be patched.
        E.g. get_state_approved where get is the prefix, state is the field_name
        and approved is the choice name.

        :param prefix: set|is
        :param field_name: the name of the field storing the choice
        :param entry: a choice dict
        :return: the function name as string
        """
        return '%(prefix)s_%(field_name)s_%(choice_name)s' % dict(
            prefix=prefix,
            field_name=field_name,
            choice_name=entry['name']
        )

    def _list_to_dict(self, choice_list, key):
        """
        Transforms the choice_list to a dict representation with param key
        as key. Used to construct internal data structure to optimize performance
        of get_by_name and get_by_value to avoid choice_list interation.

        :param choice_list: list of choices
        :param key: the key of the choice the dict will use as key
        :return: a dict representation of the choice_list
        """

        choice_dict = dict()
        for choice in choice_list:
            choice_dict[choice[key]] = choice
        return choice_dict

    def _ensure_choices_format(self, choice_list):
        """
        Called on instatiation to ensure that the passed choice list choices provide all
        mandatory keys. Raises an exception is any of the choices is malformed.
        :param choice_list: the choice_list
        :return:
        """
        errors = []
        msg = 'Mandatory key "%(key)s" missing'

        for idx, choice in enumerate(choice_list):
            choice_error = dict()
            for key in self._mandatory_keys:
                if key not in choice.keys():
                    choice_error['choices[%s]' % idx] = msg % dict(key=key)
            if len(choice_error.keys()):
                errors.append(choice_error)

        if len(errors):
            raise exceptions.MalformedChoiceDefinition(errors)


    def patch_choice_getter(self, model_class, field_name):
        """
        Patches the choice getter func which returns the choice dict associated with the
        model's choice-storing field.
        :param model_class:
        :param field_name:
        :return:
        """
        setattr(model_class, 'get_%s' % field_name, factory.get_choice_getter_func(field_name, self))

    def patch_getters(self, model_class, field_name):
        """
        Takes the model_class and the choice-storing field name and patches the
        getters for each choice in the Choicer's choice_list. Getters are patched
        as boolean getters - so use is_state_approved instead of get_state_approved.
        :param model_class: the model_class to be patched.
        :param field_name: the choice-storing field_name of the model_class
        :return:
        """
        for entry in self._choice_list:
            func_name = self._get_func_name('is', field_name, entry)
            setattr(model_class, func_name, factory.get_getter_func(field_name, entry['value']))

    def patch_setters(self, model_class, field_name, custom_impl=None):
        """

        :param model_class:
        :param field_name:
        :param custom_impl:
        :return:
        """
        for entry in self._choice_list:
            if not entry.get('legacy', False):
                func_name = self._get_func_name('set', field_name, entry)
                if custom_impl:
                    setattr(model_class, func_name, custom_impl(field_name, entry['value']))
                else:
                    setattr(model_class, func_name, factory.get_setter_func(field_name, entry['value']))

    def patch_choicer(self, model_class, name=None):
        """
        Patches the choice instance itself to the model_class in order to
        access the choicer instance directly via the model.
        :param model_class: the model_class to be patched.
        :param name: the name of the choicer which should be <field_name>_CHOICER.
        :return:
        """
        setattr(model_class, name, self)


    def patch(self, model_class, field_name, attr=None):
        """
        Applies all patches in one.
        :param model_class: the model_class to be patched.
        :param field_name: the choice-storing field name of the model class
        :param attr: (optional); the name of the choicer instance patched to the model.
        :return:
        """
        attr = attr or '%s_CHOICER' % field_name.upper()
        self.patch_choice_getter(model_class, field_name)
        self.patch_getters(model_class, field_name)
        self.patch_setters(model_class, field_name)
        self.patch_choicer(model_class, attr)


    def get_by_value(self, val):
        """
        Pass the value of a choice and get the dict representation of that choice.
        Raises a ChoiceDoesNotExist exception if there is no choice with that value.
        :param val: the value of the choice
        :return: dict
        """
        try:
            return self._choice_value_dict[val]
        except KeyError:
            raise exceptions.ChoiceDoesNotExist('There is no choice with value=%s' % val)

    def get_by_name(self, name):
        """
        Pass the name of a choice and get the dict representation of that choice.
        Raises a ChoiceDoesNotExist exception if there is no choice with that name.
        :param name: the name of the choice
        :return: dict
        """
        try:
            return self._choice_name_dict[name]
        except KeyError:
            raise exceptions.ChoiceDoesNotExist('There is no choice with name=%s' % name)

    def get_list(self):
        """
        Returns the original choice list passed to the constructor.
        :return: list
        """
        return self._choice_list

    def get_dict(self):
        """
        Returns the choice list in dict representation to access each choice by name.
        :return:
        """
        return self._choice_name_dict

    def get_choices(self):
        """
        Returns the choices as required for model field instatiation.
        :return: list of tuples (<value>, verbose_name)
        """
        choices = []
        for entry in self._choice_list:
            if not entry.get('legacy', False):
                choices.append((entry['value'], entry['verbose_name']))
        return choices


    def get_api_doc(self):
        """

        :return:
        """
        return self.func_name_dict


    def apply(self, field_name):
        """
        Decorator to apply the patches to a decorated model class
        :param field_name: the choice-storing field of the model class
        :return: function
        """

        def apply_patch(cls):
            self.patch(
                model_class=cls,
                field_name=field_name
            )

            return cls
        return apply_patch





