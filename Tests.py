import unittest
from CorpusParser import *
from Tagger import *

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
        self.assertEqual(c.p_word('tests', 'VBZ'), (1. + TagCounter._delta)/2)

class TestTagger(unittest.TestCase):
    def test_split_sentence(self):
        s = ''
        self.assertEquals([], Tagger.split_sentence(s))
        s = 'Simple.'
        self.assertEquals(['simple', '.'], Tagger.split_sentence(s))
        s = 'A bit complex'
        self.assertEquals(['a', 'bit', 'complex'], Tagger.split_sentence(s))
        s = 'This (test) line, really is: #cool!'
        self.assertEquals(['this', '(', 'test', ')', 'line', ',', 'really', 'is', ':', '#', 'cool', '!'], Tagger.split_sentence(s))
        s = "quotes ``should work''"
        self.assertEquals(['quotes', '``', 'should', 'work', "''"], Tagger.split_sentence(s))

        # dealing with contractions and apostrophes
        s = "I'd, I'm" 
        self.assertEquals(["i","'d",',',"i","'m", ], Tagger.split_sentence(s))
        s = "``Leo's'' aren't"
        self.assertEquals(["``","leo","'s","''","are","n't"], Tagger.split_sentence(s))
        s = "we're we've"
        self.assertEquals(["we","'re","we","'ve", ], Tagger.split_sentence(s))
        
        # inentionally unhandled
        s = "The '70s were rock'n"

if __name__ == '__main__':
    unittest.main()
