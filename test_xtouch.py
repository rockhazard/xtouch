#!/usr/bin/env python3


import unittest
from unittest.mock import Mock
import xtouch


class TestXtouch(unittest.TestCase):

    def setUp(self):
        self._options = xtouch._options
        self.xtouch = xtouch
        self.match_args_output1 = {'prefix': 'str_', 'size': '5',
                                   'suffix': '_str', 'extension': 'tmp'}
        self.pattern = 'str_.5._str.tmp'

    # def tearDown(self):
    #     # cleanup operations: close/remove files, etc.
    #     pass

    def test_match_args(self):
        match = self.xtouch.match_args(self.pattern)
        self.assertEqual(match, self.match_args_output1, 'Not equal')

    # def test_random_word(self): # needs mock word file and wordList
    #     word = self.xtouch.random_word(self.mock)
    #     self.assertIn(word, wordList, '{} not in list'.format(word))

    def test_increment_filename(self):
        result_increment_filename = self.xtouch.increment_filename(
            zeros='5', count=20)
        self.assertEqual(result_increment_filename, '00020', 'Not equal')

    def test_gen_filename(self):
        self.testopts = self._options
        self.testopts['increment'] = True
        resul_gen_filename = self.xtouch.gen_filename(switch=self.testopts,
                                                      prefix='str_', size=5,
                                                      ext=3, suffix='_test',
                                                      count=1)
        self.assertEqual(resul_gen_filename,
                         'str_00001_test.001', 'Not equal')

    def test_gen_files_set(self):
        self.testopts = self._options
        self.testopts['increment'] = True
        match = self.match_args_output1
        result_gen_files_set = self.xtouch.gen_files_set(numberOfFiles=2,
                                                         zeros=2, default=False,
                                                         match=match, sep='_',
                                                         switch=self.testopts)
        self.assertEqual(result_gen_files_set,
                         {'str_00_str.tmp', 'str_01_str.tmp'}, 'Not equal')

    def test_file_factory(self):
        self.testopts = self._options
        self.testopts['increment'] = True
        self.testopts['pos_options'] = '--date=02/03/2017'
        mock_subprocess = Mock(name='ff_subprocess')
        self.xtouch.file_factory(pattern=self.pattern, switch=self.testopts,
                                 nFiles=101, cmd=mock_subprocess, default=False)
        mock_subprocess.run.assert_any_call(
            'touch --date=02/03/2017 str_00100_str.tmp', shell=True)

'''
ASSERTS:
self.assert - base assert allowing you to write your own assertions
self.assertEqual(a, b) - check a and b are equal
self.assertNotEqual(a, b) - check a and b are not equal
self.assertIn(a, b) - check that a is in the item b
self.assertNotIn(a, b) - check that a is not in the item b
self.assertFalse(a) - check that the value of a is False
self.assertTrue(a) - check the value of a is True
self.assertIsInstance(a, TYPE) - check that a is of type "TYPE"
self.assertRaises(ERROR, a, args) - check that when a is called with
    args that it raises ERROR
'''

if __name__ == "__main__":
    # call unittest module
    unittest.main()
