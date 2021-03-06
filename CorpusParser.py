'''
Contains the Word class, functionality for parsing words, sentences, and files,
and a TagCounter class that can extract information from the WSJ corpus.
'''

import string
from WordClassifier import WordClassifier
from Word import Word
from numpy import log

class InvalidWordFormatError(Exception):
    def __init__(self, invalid_word):
        self.invalid_word = invalid_word
    def __str__(self):
        return repr(self.invalid_word)

def parse_word(word):
    ''' Parses a word-POS pair of the form "word/tag" and returns a word object '''
    parts = string.split(word, '/')
    if len(parts) > 2 and '\\' in parts[0]:
        while '\\' in parts[0]:
            # special case when a word includes '/'
            parts[0] = parts[0][:-1] + '/' + parts[1]
            del parts[1]
    elif len(parts) != 2:
        #raise InvalidWordFormatError(parts)
        pass
    return Word(parts[0], parts[1])

def parse_line(line):
    ''' Parses a line in the corpus, a series of word/POS pairs delimited by spaces
        Returns a list of Word objects '''
    parts = string.split(line)

    words = []
    for pair in parts:
        if pair == '[' or pair == ']':
            continue
        else:
            words.append(parse_word(pair))
    return words

START = Word('', 'START')
DELIMITER = '======================'

def parse_file(f):
    ''' Parses a .POS file from the corpus into a list of sentences.
        Each sentence is a list of Words, starting with START and finishing with
            a word w for which w.is_end() == True '''
    def new_sentence():
        return [START]

    sentences = []
    curr_sentence = []
    for line in f:
        if DELIMITER in line:
            if len(curr_sentence) > 0 and curr_sentence != [START]:
                sentences.append(curr_sentence)
            curr_sentence = new_sentence()
        else:
            curr_sentence += parse_line(line)
            if len(curr_sentence) > 0 and curr_sentence[-1].is_end():
                sentences.append(curr_sentence)
                curr_sentence = new_sentence()
    return sentences

def map_files(fun, file_range):
    for i in xrange(2, 13):
        folder = format(i, '02')
        for j in file_range:
            fname = format(i*100+j, '04')
            f = open('WSJ-2-12/'+folder+'/WSJ_'+fname+'.POS')
            fun(f)
            f.close()

class TagCounter:
    ''' This class stores the number of relative counts for (tag, tag)
        and (word, tag) pairs, and provides P(word | tag) and P(tag | tag) '''
    _delta = 1e-6
    def __init__(self, only_words=False):
        self.tag_tag_count = {}
        self.word_tag_count = {}
        self.tag_count = {}
        self.word_count = {}
        self.only_words = only_words
        self.tagset = None
        self.classifier = WordClassifier(self.tag_count, TagCounter._delta)

    def parse_file(self, f):
        ''' accepts a .POS file and updates the (tag,tag) and (word,tag) counts '''
        def add_count(word,tag,tag_prev):
            self.word_count[word.chars] = self.word_count.get(word.chars, 0) + 1
            self.tag_count[tag] = self.tag_count.get(tag, 0) + 1
            self.word_tag_count[(word.chars,tag)] = self.word_tag_count.get((word.chars,tag), 0) + 1
            if not self.only_words:
                self.tag_tag_count[(tag,tag_prev)] = self.tag_tag_count.get((tag,tag_prev), 0) + 1
                # when extracting features, we use the regular-case words
                self.classifier.add_feature_count(word.true_chars, tag)

        for sentence in parse_file(f):
            self.tag_count[START.tag] = self.tag_count.get(START.tag, 0) + 1
            i = 1
            while i < len(sentence):
                word = sentence[i]
                tag = sentence[i].tag
                tag_prev = sentence[i-1].tag

                # there is no instance of '|' appearing in both tag and tag_prev
                # in the entirety of the 250k word corpus
                if  '|' in tag:
                    for t in string.split(tag,'|'):
                        add_count(word,t,tag_prev)
                elif '|' in tag_prev:
                    for t in string.split(tag_prev, '|'):
                        add_count(word,tag,t)
                else:
                    add_count(word,tag,tag_prev)
                i += 1

    def p_word(self, word, tag):
        ''' P(word | tag), with small smoothing factor '''
        return (TagCounter._delta + self.word_tag_count.get((word,tag),0)) / \
                (TagCounter._delta + self.tag_count.get(tag, 0))

    def p_tag(self, tag, tag_prev):
        ''' P(tag1 | tag2), with small smoothing factor '''
        return (TagCounter._delta + self.tag_tag_count.get((tag,tag_prev),0)) / \
                (TagCounter._delta + self.tag_count.get(tag_prev, 0))

    def log_p_unknown_word(self, word, tag, tag_prev):
        ''' Uses Naive Bayes to guess the P(word | tag) '''
        return log(self.p_tag(tag, tag_prev)) + self.classifier.log_p_word(word, tag)

    def has_word(self, word):
        return word in self.word_count

    def word_has_tag(self, word, tag):
        return (word, tag) in self.word_tag_count

    def has_tag(self, tag):
        return tag in self.tag_count

    def word_tags(self, word):
        ''' get the known tags assigned to a specific word '''
        ret = {}
        for tag in self.tag_count.keys():
            if (word,tag) in self.word_tag_count:
                ret[tag] = self.word_tag_count[(word,tag)]
        return ret

    def tags(self):
        ''' Returns the sorted list of tags, excluding error tags with & '''
        ret = [i for i in self.tag_count.keys() if '&' not in i]
        list.sort(ret)
        return ret

    def tags_no_punc(self):
        ''' Returns only tags that pertain to words, not punctuation '''
        wtags = []
        for t in self.tag_count:
            if t not in string.punctuation + "''" + "``" and '&' not in t:
                wtags.append(t)
        return wtags

    def parse_corpus_range(self, fold_range):
        ''' parses all corpus files to collect count data '''
        map_files(self.parse_file, fold_range)

    def parse_corpus(self):
        ''' parse the entire corpus '''
        self.parse_corpus_range(range(100))

    def descriptive_tag(self, tag):
        ''' returns the description of the Penn Treebank tag '''
        self.parse_tagset()
        return self.tagset.get(tag, tag)

    def parse_tagset(self):
        ''' Gets the description of each tag from the tagset.txt description file'''
        if self.tagset:
            return

        self.tagset = {}
        def parse_tagset_line(line):
            s = line.split()
            self.tagset[s[0]] = line[len(s[0]):].strip()

        f = open('tagset.txt')
        for line in f:
            parse_tagset_line(line)
