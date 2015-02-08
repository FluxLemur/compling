import string

class Word:
    def __init__(self, chars, tag):
        self.chars = string.lower(chars)    # characters that make up the word
        self.tag = tag                      # POS tag for the word
        for c in tag:
            if c in string.lowercase:
                raise Exception(chars + tag)
    def __repr__(self):
        return self.chars + '/' + self.tag
    def __str__(self):
        return self.__repr__()
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.chars == other.chars and self.tag == other.tag)
    def is_end(self):
        return self.tag == '.' or self.tag == ')'

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


class TagCounter:
    ''' This class stores the number of relative counts for (tag, tag)
        and (word, tag) pairs, and provides P(word | tag) and P(tag | tag) '''
    def __init__(self):
        self.tag_tag_count = {}
        self.word_tag_count = {}
        self.tag_count = {}
        self.word_count = {}

    def parse_file(self, f):
        ''' accepts a .POS file and updates the (tag,tag) and (word,tag) counts '''
        for sentence in parse_file(f):
            i = 1
            while i < len(sentence):
                word = sentence[i].chars
                tag = sentence[i].tag
                tag_prev = sentence[i-1].tag

                self.tag_count[tag] = self.tag_count.get(tag, 0) + 1
                self.word_count[word] = self.word_count.get(word, 0) + 1

                self.tag_tag_count[(tag,tag_prev)] = self.tag_tag_count.get((tag,tag_prev), 0) + 1
                self.word_tag_count[(word,tag)] = self.word_tag_count.get((word,tag), 0) + 1
                i += 1

    def p_word(self, word, tag):
        ''' P(word | tag) '''
        return self.word_tag_count.get((word,tag),0) / (1. * self.tag_count.get(tag, 1))

    def p_tag(self, tag, tag_prev):
        ''' P(tag1 | tag2) '''
        return self.tag_tag_count.get((tag,tag_prev),0) / (1. * self.tag_count.get(tag, 1))

    def word_tags(self, word):
        ret = {}
        for tag in self.tag_count.keys():
            if (word,tag) in self.word_tag_count:
                ret[tag] = self.word_tag_count[(word,tag)]
        return ret

    def tags(self):
        return self.tag_count.keys()

    def parse_corpus(self):
        ''' parses all corpus files to collect count data '''
        for i in xrange(2, 13):
            folder = format(i, '02')
            for j in xrange(100):
                fname = format(i*100+j, '04')
                f = open('WSJ-2-12/'+folder+'/WSJ_'+fname+'.POS')
                #print 'parsing ' + fname + '...'
                self.parse_file(f)
                f.close()
