''' Runs the cross-validation routines to test the accuracy of the Tagger '''

from Tagger import Tagger
from CorpusParser import TagCounter, map_files, parse_file
import sys, time

#TOTAL_WORDS = 553177. # approximate number of words in the corpus
folds = 10
chunk = 100 / folds
total_errs = 0
total_matches = 0

# Size of test determines how many sentences in each file are checked
SMALL = 1
MEDIUM = 5
LARGE = -1  # every file
size = LARGE

timing = True   # whether to print time of computations

def percent_match(total_errs, total_matches):
    return 1.0 - (1.0*total_errs) / total_matches

def cross_validate(count_words):
    ''' Runs cross validation on the Tagger, count_words = True iff the Tagger counts all the words,
        so P(word | tag) is known, but P(tag | prev_tag) is still only 90% known '''

    global total_errs, total_matches
    sum_err = 0
    print 'Fold    Err    Match    Frac_Match'

    # files in the corpus range from 0-100, so test and train ranges are slices of this
    # range, such that train_range and test_range together make range(0,100)
    for i in xrange(folds):
        train_range = range(0, chunk*i) + range(chunk*(i+1), 100)
        test_range = range(chunk*i, chunk*(i+1))
        total_errs = 0
        total_matches = 0

        tm = time.time()
        c = TagCounter()
        c.parse_corpus_range(train_range)
        if (count_words):
            c.only_words = count_words
            c.parse_corpus_range(test_range)
        t = Tagger(c)
        tm = time.time() - tm
        if timing:
            print tm,

        # file_validate is mapped across all files in test_range
        def file_validate(f):
            global total_errs, total_matches
            sentences = parse_file(f)
            for sent in sentences[:size]:
                words = []
                for word in sent[1:]: # sent[0] will always be START
                    words.append(word.true_chars)
                tagged = t.tag_words(words)
                matches = 0
                errs = 0
                for (actual_w, pred_w) in zip(sent, tagged):
                    if actual_w.tag != pred_w.tag:
                        #print actual_w, pred_w     # prints the mistagged pairs
                        errs += 1
                    else:
                        matches += 1
                total_errs += errs
                total_matches += matches

        tm = time.time()
        map_files(file_validate, test_range)
        tm = time.time() - tm
        if timing:
            print tm
        print '%3d  %6d  %7d      %0.4f' %(i, total_errs, total_matches, percent_match(total_errs, total_matches))
        print ''

        sum_err += percent_match(total_errs, total_matches)

    print 'cumulative averaged error:', (sum_err*1.0)/folds

if __name__ == '__main__':
    print 'Cross validating with some unknown words...'
    cross_validate(False)
    #print '\nCross validating with NO unknown words...'
    #cross_validate(True)
