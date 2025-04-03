from django.test import TestCase

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Basic sanity test to check that test framework is working
        This test doesn't use Selenium so it should always pass
        """
        self.assertEqual(1 + 1, 2)