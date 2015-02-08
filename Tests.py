import unittest
from CorpusParser import *

class TestWordParsing(unittest.TestCase):
    def test_parse_word(self):
        self.assertEqual(parse_word('in/IN'), Word('in', 'IN'))
        self.assertEqual(parse_word('Invest\/Net/NNP'), Word('Invest/Net', 'NNP'))
        self.assertEqual(parse_word('pianist\/bassoonist\/composer/NN'), Word('pianist/bassoonist/composer', 'NN'))
        #self.assertEqual(parse_word('male/JJ|NN'), [Word('male', 'JJ'), Word('male', 'NN')])
        #self.assertEqual(parse_word('S*/NNP&P/NN'), Word('Invest/Net', 'NNP'))
        #self.assertRaises(InvalidWordFormatError, parse_word, 'in')
        #self.assertRaises(InvalidWordFormatError, parse_word, 'in/IN/NO')

    def test_parse_line(self):
        self.assertEqual(parse_line("[ The/DT Misanthrope/NN ]"),
                [Word('the', 'DT'), Word('misanthrope', 'NN')])

    def test_parse_file(self):
        # note, tags generated from http://textanalysisonline.com/nltk-stanford-postagger
        # tagset is https://www.ling.upenn.edu/courses/Fall_2003/ling001/penn_treebank_pos.html
        sentences = parse_file(open('test_file.POS'))
        self.assertEquals(4, len(sentences))
        for sentence in sentences:
            self.assertEquals(sentence[0], START)
            self.assertTrue(sentence[-1].is_end())

    def test_tag_counter(self):
        c = TagCounter()
        c.parse_file(open('test_file.POS'))
        self.assertEqual(c.p_word('tests', 'VBZ'), 1./2)

if __name__ == '__main__':
    unittest.main()
