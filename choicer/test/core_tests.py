from __future__ import unicode_literals, print_function
import unittest
import choicer
from choicer import exceptions


class ChoicerTests(unittest.TestCase):

    def setUp(self):
        self.CHOICE_LIST = [
            dict(
                name='approved',
                value=0,
                verbose_name='Approved'
            ),
            dict(
                name='dismissed',
                value=1,
                verbose_name='Dismissed'
            ),
        ]

    def _get_fake_model_class(self):
        """
        Returns a newly created FakeModelClass in order to test patching in isolation
        for each patching test. Otherwise once applied patches will last for further
        patching test cases, too.
        :return:
        """
        class FakeModel(object):
            state = 0
        return FakeModel

    def test_basics(self):
        """
        Tests get_choices, get_list and get_dict.
        :return:
        """
        mychoicer = choicer.Choicer(self.CHOICE_LIST)

        self.assertEquals(len(mychoicer.get_choices()), len(self.CHOICE_LIST))
        self.assertEquals(  len(mychoicer.get_list()), len(self.CHOICE_LIST))
        self.assertEquals(len(mychoicer.get_dict()), len(self.CHOICE_LIST))

    def test_get_by(self):
        """
        Tests the get_by_<name|value> functions.
        :return:
        """
        mychoicer = choicer.Choicer(self.CHOICE_LIST)

        self.assertTrue(
            mychoicer.get_by_name('approved') == mychoicer.get_by_value(0) == self.CHOICE_LIST[0]
        )

    def test_malformed_choice_definition_exceptions(self):
        """
        Tests that a MalformedChoiceDefinition is raised in case choicer is initialized with
        a malformed choice.
        :return:
        """
        try:
            choicer.Choicer([
                dict(name='approved', value=0, verbose_name='Approved'),
                dict(name='dismissed')
            ])
        except exceptions.MalformedChoiceDefinition as e:
            exception_list = e.errors
            self.assertTrue('choices[1]' in exception_list[0].keys())

    def test_choice_does_not_exist_exceptions(self):
        """
        Tests that an exception is raised if a choice is accessed that
        does not exist.
        :return:
        """
        mychoicer = choicer.Choicer(self.CHOICE_LIST)

        self.assertRaises(exceptions.ChoiceDoesNotExist, mychoicer.get_by_name, 'xyz')
        self.assertRaises(exceptions.ChoiceDoesNotExist, mychoicer.get_by_value, 'xyz')

    def test_out_of_sync_exception(self):
        """
        Tests that the ChoicesOutOfSyncError is raised in case the choice-storing field
        provide a value which not represented in the choices data structure.
        :return:
        """

        mychoicer = choicer.Choicer(self.CHOICE_LIST)

        @mychoicer.apply(field_name='state')
        class MyModel(object):
            state = 1337

        obj = MyModel()
        self.assertRaises(exceptions.ChoicesOutOfSyncError, obj.get_state)

    def test_separate_patching(self):
        """
        Test the manual/separate patching.
        :return:
        """

        model_class = self._get_fake_model_class()
        mychoicer = choicer.Choicer(self.CHOICE_LIST)

        mychoicer.patch_choice_getter(model_class, 'state')
        mychoicer.patch_getters(model_class, 'state')
        mychoicer.patch_setters(model_class, 'state')
        mychoicer.patch_choicer(model_class, 'STATE_CHOICER')

        self._assert_patches(model_class())

    def test_patch_all(self):
        """
        Tests the patch method which in under the hood calls all manual patch
        api functions subsequently, so we can apply the same asserting.
        :return:
        """

        model_class = self._get_fake_model_class()
        mychoicer = choicer.Choicer(self.CHOICE_LIST)
        mychoicer.patch(
            model_class=model_class,
            field_name='state',
            attr='STATE_CHOICER'
        )
        self._assert_patches(model_class())

    def test_decorator(self):
        """
        Tests the decorator way of patching.
        :return:
        """
        mychoicer = choicer.Choicer(self.CHOICE_LIST)

        @mychoicer.apply(field_name='state')
        class MyModel(object):
            state = 0

        self._assert_patches(MyModel())

    def _assert_patches(self, fakemodel_obj):
        """
        Asserts that the passed fakemodel_obj was patched succesfully.
        :param fakemodel_obj:
        :return:
        """
        # check that getters have been patched
        self.assertTrue(
            hasattr(fakemodel_obj, 'is_state_approved') and
            hasattr(fakemodel_obj, 'is_state_dismissed')
        )
        # check that setters have been patched
        self.assertTrue(
            hasattr(fakemodel_obj, 'set_state_approved') and
            hasattr(fakemodel_obj, 'set_state_dismissed')
        )
        # check that the choicer itself has been pacthed
        self.assertTrue(
            hasattr(fakemodel_obj, 'STATE_CHOICER')
        )

        # check that setter is working
        fakemodel_obj.set_state_dismissed()
        self.assertEquals(
            fakemodel_obj.state,
            fakemodel_obj.STATE_CHOICER.get_by_name('dismissed')['value']
        )

        # check that getter is working
        self.assertEquals(
            fakemodel_obj.is_state_dismissed(),
            fakemodel_obj.STATE_CHOICER.get_by_name('dismissed')['value']
        )








