''' A Naive Bayes classifier for unkown POS tags 
    Provides the method P(word | tag) by the Naive Bayes approximation
    P(tag) * P(f_1 | tag) * P(f_2 | tag) ... for each word feature f_i
'''

from Word import Word
from numpy import log
import string

class WordClassifier:
    def __init__(self, tag_count, smooth_delta):
        self.tag_count = tag_count        # num. of occurances of a tag
        self.feature_tag_count = {}       # num. of (feature, tag) occurances
        self.smooth_delta = smooth_delta  # smoothing regularizer for getting probabilities
        self.word_features = {}           # cache the features calculated for a word

    def get_features(self, word):
        ''' Feature extraction for a word '''
        if word in self.word_features:
            return self.word_features[word]

        features = []

        # 1: whether first character is uppercase
        if word[0] in string.uppercase:
            features.append('1:1st char upper')
        else:
            features.append('1:1st char lower')

        # 2: ends in s
        if word[-1] == 's':
            features.append('3:-s end')
        else:
            features.append('3:no -s end')

        # 3: final letter
        features.append('4:' + word[-1])

        # 4: first letter
        features.append('5:' + word[0])

        # 5: word length
        features.append('6:' + str(len(word)))

        self.word_features[word] = features
        return features

    def p_feature(self, feature, tag):
        ''' returns P(feature | tag) = P(feature, tag) / P(tag) 
                                     = Count(feature, tag) / Count(tag)
        '''
        return (self.smooth_delta + self.feature_tag_count.get((feature,tag),0)) / \
                (self.smooth_delta + self.tag_count.get(tag, 0))

    def log_p_word(self, word, tag):
        ''' returns the log of P(word | tag), using Naive Bayes conditioning on the features '''
        log_p = 0
        for f in self.get_features(word):
            log_p += log(self.p_feature(f,tag))
        return log_p

    def add_feature_count(self, word, tag):
        ''' Add (feature, tag) counts for all features of a given word '''
        for f in self.get_features(word):
            self.feature_tag_count[(f, tag)] = self.feature_tag_count.get((f, tag), 0) + 1
