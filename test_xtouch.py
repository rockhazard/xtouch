#!/usr/bin/env python3


import unittest
from unittest.mock import Mock, mock_open, patch
import xtouch


class TestXtouch(unittest.TestCase):

    def setUp(self):
        self._options = xtouch._options
        self.match_args_output1 = {'prefix': 'str_', 'size': '5',
                                   'suffix': '_str', 'extension': 'tmp'}
        self.pattern = 'str_.5._str.tmp'
        self.wordList = ['puns', 'premise', 'rustle', 'canine']

    def test_match_args(self):
        match = xtouch.match_args(self.pattern)
        self.assertEqual(match, self.match_args_output1, 'Not equal')

    @patch('builtins.open', mock_open(read_data='puns\npremise\nrustle\ncanine'))
    @patch('xtouch.Path')
    def test_random_word(self, m):
        word = xtouch.random_word()
        self.assertIn(word, self.wordList, '{} not in list'.format(word))
        print('Mock Path called: ', m.called)

    def test_increment_filename(self):
        result_increment_filename = xtouch.increment_filename(
            zeros='5', count=20)
        self.assertEqual(result_increment_filename, '00020', 'Not equal')

    def test_gen_filename(self):
        self.testopts = self._options
        self.testopts['increment'] = True
        resul_gen_filename = xtouch.gen_filename(switch=self.testopts,
                                                 prefix='str_', size=5,
                                                 ext=3, suffix='_test',
                                                 count=1)
        self.assertEqual(resul_gen_filename,
                         'str_00001_test.001', 'Not equal')

    def test_gen_files_set(self):
        self.testopts = self._options
        self.testopts['increment'] = True
        match = self.match_args_output1
        result_gen_files_set = xtouch.gen_files_set(numberOfFiles=2,
                                                    zeros=2, default=False,
                                                    match=match, sep='_',
                                                    switch=self.testopts)
        self.assertEqual(result_gen_files_set,
                         {'str_00_str.tmp', 'str_01_str.tmp'}, 'Not equal')

    def test_file_factory_call_count(self):
        self.testopts = self._options
        self.testopts['increment'] = True
        self.testopts['pos_options'] = '--date=02/03/2017'
        mock_subprocess = Mock(name='ff_subprocess')
        xtouch.file_factory(pattern=self.pattern, switch=self.testopts,
                            nFiles=101, cmd=mock_subprocess, default=False)
        self.assertEqual(mock_subprocess.run.call_count, 101, 'Not Equal')

    def test_file_factory_first_call(self):
        self.testopts = self._options
        self.testopts['increment'] = True
        self.testopts['pos_options'] = '--date=02/03/2017'
        mock_subprocess = Mock(name='ff_subprocess')
        xtouch.file_factory(pattern=self.pattern, switch=self.testopts,
                            nFiles=101, cmd=mock_subprocess, default=False)
        mock_subprocess.run.assert_any_call(
            'touch --date=02/03/2017 str_00000_str.tmp', shell=True)

    def test_file_factory_last_call(self):
        self.testopts = self._options
        self.testopts['increment'] = True
        self.testopts['pos_options'] = '--date=02/03/2017'
        mock_subprocess = Mock(name='ff_subprocess')
        xtouch.file_factory(pattern=self.pattern, switch=self.testopts,
                            nFiles=101, cmd=mock_subprocess, default=False)
        mock_subprocess.run.assert_any_call(
            'touch --date=02/03/2017 str_00100_str.tmp', shell=True)

    def test_file_factory_all_calls(self):
        self.testopts = self._options
        self.testopts['increment'] = True
        self.testopts['pos_options'] = '-m'
        mock_subprocess = Mock(name='ff_subprocess')
        xtouch.file_factory(pattern=self.pattern, switch=self.testopts,
                            nFiles=1, cmd=mock_subprocess, default=False)
        name, args, kwargs = mock_subprocess.run.mock_calls[0]
        results = []
        for name, args, kwargs in mock_subprocess.run.mock_calls:
            results.append(args)
        print(results)
        self.assertEqual(args, ('touch -m str_00000_str.tmp',), 'Not Equal')


if __name__ == "__main__":
    # call unittest module
    unittest.main()
