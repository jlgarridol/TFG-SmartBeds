from tests import transformersTest
import unittest

suites = transformersTest.launcher()
for suite in suites:
    unittest.TextTestRunner(verbosity=2).run(suite)