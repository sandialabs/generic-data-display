import unittest

from generic_data_display.pipeline.utilities.type_wrapper import TypeWrapper


class TestTypeWrapper(unittest.TestCase):
    class SpecialType(TypeWrapper):
        def _omct_hints(self):
            return dict(thing=2)

    def test_string(self):
        test_uri = "file://test.image"
        new_uri = self.SpecialType(test_uri)

        # Check that string functions are still working
        self.assertEqual(test_uri, new_uri)
        self.assertEqual(test_uri[0], 'f')

        # Check type information
        self.assertTrue(isinstance(new_uri, str))
        self.assertTrue(isinstance(new_uri, self.SpecialType))
        self.assertTrue(isinstance(new_uri, TypeWrapper))

        # Check that OpenMCT hints are accessible
        self.assertEqual(new_uri._omct_hints(), dict(thing=2))

    def test_dict(self):
        test_dict = dict(alpha=True, beta=4)
        new_dict = self.SpecialType(test_dict)

        # Check comparison operator
        self.assertEqual(test_dict, new_dict)

        # Check access operator
        self.assertEqual(test_dict["beta"], 4)

        # Check type information
        self.assertTrue(isinstance(new_dict, dict))
        self.assertTrue(isinstance(new_dict, self.SpecialType))
        self.assertTrue(isinstance(new_dict, TypeWrapper))

        # Check that OpenMCT hints are accessible
        self.assertEqual(new_dict._omct_hints(), dict(thing=2))

    def test_array(self):
        test_array = [1,3,7,9]
        new_array = self.SpecialType(test_array)

        # Check comparison operator
        self.assertEqual(test_array, new_array)

        # Check access operator
        self.assertEqual(test_array[2], 7)

        # Check type information
        self.assertTrue(isinstance(new_array, list))
        self.assertTrue(isinstance(new_array, self.SpecialType))
        self.assertTrue(isinstance(new_array, TypeWrapper))

        # Check that OpenMCT hints are accessible
        self.assertEqual(new_array._omct_hints(), dict(thing=2))


if __name__ == '__main__':
    unittest.main()