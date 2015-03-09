''' A Naive Bayes classifier for unkown POS tags '''
from nltk.stem.lancaster import LancasterStemmer
from Word import Word
from numpy import log
import string

class WordClassifier:
    def __init__(self, tag_count, smooth_delta):
        self.tag_count = tag_count
        self.feature_tag_count = {}
        self.smooth_delta = smooth_delta
        self.word_features = {}
        self.stemmer = LancasterStemmer()

    def get_features(self, word):
        ''' Feature extraction for a word '''
        if word in self.word_features:
            return self.word_features[word]

        # 0: bias term
        #features = ['0:']
        features = []

        # 1: whether first character is uppercase
        #if word[0] in string.uppercase:
        #    features.append('1:1st char upper')
        #else:
        #    features.append('1:1st char lower')

        # 2: stem of the word
        #features.append('2:'+self.stemmer.stem(word))

        # 3: ends in s
        #if word[-1] == 's':
        #    features.append('3:-s end')
        #else:
        #    features.append('3:no -s end')

        self.word_features[word] = features
        return features

    def p_feature(self, feature, tag):
        ''' returns P(feature | tag) '''
        return (self.smooth_delta + self.feature_tag_count.get((feature,tag),0)) / \
                (self.smooth_delta + self.tag_count.get(tag, 0))

    def log_p_word(self, word, tag):
        log_p = 0
        for f in self.get_features(word):
            log_p += log(self.p_feature(f,tag))
        return log_p

    def add_feature_count(self, word, tag):
        ''' Add (feature, tag) counts for all features of a given word '''
        for f in self.get_features(word):
            self.feature_tag_count[(f, tag)] = self.feature_tag_count.get((f, tag), 0) + 1
