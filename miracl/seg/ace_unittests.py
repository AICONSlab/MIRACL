import unittest
import argparse
from ace_parser import aceParser


# FIX: At this point the tests fail because not all arguments are provided.
# I should probably use the mock module to fix this...
class TestAceParser(unittest.TestCase):
    def setUp(self):
        self.parser = aceParser()

    def test_input_folder(self):
        args = self.parser.parsefn().parse_args(['-i', 'input_folder'])
        self.assertEqual(args.input_folder, 'input_folder')

    def test_model_type_unet(self):
        args = self.parser.parsefn().parse_args(['-m', 'unet'])
        self.assertEqual(args.model_type, 'unet')

    def test_model_type_unetr(self):
        args = self.parser.parsefn().parse_args(['-m', 'unetr'])
        self.assertEqual(args.model_type, 'unetr')

    def test_model_type_ensemble(self):
        args = self.parser.parsefn().parse_args(['-m', 'ensemble'])
        self.assertEqual(args.model_type, 'ensemble')

    def test_voxel_size(self):
        args = self.parser.parsefn().parse_args(['-s', '1', '2', '3'])
        self.assertEqual(args.voxel_size, [1, 2, 3])


if __name__ == '__main__':
    unittest.main()
