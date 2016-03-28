from __future__ import absolute_import, print_function, unicode_literals

import unittest
from choicer.test import core_tests

def suite():
    return unittest.TestSuite([
        unittest.TestLoader().loadTestsFromTestCase(core_tests.ChoicerTests),
    ])


def run_all():
    return unittest.TextTestRunner(verbosity=2).run(suite())
