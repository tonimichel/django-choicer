from __future__ import unicode_literals, print_function, absolute_import
import sys
import os
sys.path.append(
    os.path.join(os.path.dirname(__file__), '../..')
)
from choicer import test


#   This is the main test runner of ape.
#   Further test cases are placed within ape.test.
#   To add new test cases add them in their own module within
#   ape/test and register them in ape/test/__init__.py

if __name__ == '__main__':

    result = test.run_all()
    retval = 0 if result.wasSuccessful() else 1
    sys.exit(retval)
