import re, sys
from math import log
from CorpusParser import TagCounter,START
from Word import Word

class Tagger:
    ''' Tags sentences after learning from the WSJ corpus '''

    def __init__(self, c=None):
        if c == None:
            self.tag_counter = TagCounter()
            self.tag_counter.parse_corpus()

        else:
            self.tag_counter = c
        self.tags = self.tag_counter.tags()
        self.guess_tags = False              # whether to use the WordClassifier POS guesser

    def tag_words(self, words):
        ''' Uses the Viterbi dynamic programming algorithm to determine the most
            likely tagging for a sentence '''
        tags = self.tags
        n = len(words)
        k = len(tags)
        p_w = self.tag_counter.p_word
        p_t = self.tag_counter.p_tag

        # initializing...
        # score[n][k] stores the sum of logs of probabilities of the tagging up to
        #   the n_th word, having tag tags[k]
        # backpointer[n][k] stores the index k' of the best tag, namely tags[k'],
        #   for the (n-1)th word
        def n_by_k(n, k):
            return [[0 for i in xrange(k)] for j in xrange(n)]
        score = n_by_k(n, k)
        backpointer = n_by_k(n, k)
        for i in xrange(k):
            score[0][i] = log(p_w(words[0].lower(), tags[i])) + log(p_t(tags[i], START.tag))

        # induction steps
        for word_i in xrange(1, n):
            word = words[word_i].lower()
            for tag_i in xrange(k):
                tag = tags[tag_i]
                # for a known word, only consider the tags that we have observed
                known = self.tag_counter.has_word(word)
                if known and not self.tag_counter.word_has_tag(word, tag):
                    score[word_i][tag_i] = -sys.maxint
                    continue

                # considering the best tagging up to word_i - 1, determine the best
                # tag for word_i
                max_score = None
                max_score_i = 0
                for prev_i in range(k):
                    temp_score = score[word_i-1][prev_i] + log(p_t(tag, tags[prev_i]))
                    if self.guess_tags and not known:
                        temp_score += \
                                self.tag_counter.log_p_unknown_word(words[word_i],tag,tags[prev_i])
                    if temp_score > max_score:
                        max_score = temp_score
                        max_score_i = prev_i

                score[word_i][tag_i] = max_score
                if not self.guess_tags or known:
                    score[word_i][tag_i] += log(p_w(word, tag))

                backpointer[word_i][tag_i] = max_score_i

        # backtrack for solution tags
        tagged_sentence = []
        best_i = score[n-1].index(max(score[n-1]))
        for i in xrange(n-1, -1, -1):
            tagged_sentence.insert(0, Word(words[i],tags[int(best_i)]))
            best_i = backpointer[i][best_i]
        
        return [START] + tagged_sentence

    def tag_sentence(self, sentence, descriptive=False):
        ''' Splits and tags a sentence '''
        words = Tagger.split_sentence(sentence)
        if words[-1] not in '.!?':
            words.append('.')
        tagged = self.tag_words(words)
        if descriptive:
            for i in xrange(len(tagged)):
                tagged[i].tag = repr(self.tag_counter.descriptive_tag(tagged[i].tag))
        return tagged

    @staticmethod
    def split_sentence(sentence):
        ''' Splits a sentence into words '''
        bad_contractions = ["n't"]
        s = sentence
        for b in bad_contractions:
            i = s.find(b)
            while i != -1:
                s= s[:i] + ' ' + s[i:]
                i = s.find(b, i+2)
        expr = re.compile("n\'t|\w+|\'{2}|`{2}|\'m|\'d|\'s|\'re|\'ve|\S")
        return [i for i in expr.findall(s)]
