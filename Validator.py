''' Runs the cross-validation routines to test the accuracy of the Tagger '''
from Tagger import *
from CorpusParser import *
import sys

# approximate number of words in the corpus
TOTAL_WORDS = 553177.
folds = 10
chunk = 100 / folds
total_errs = 0
total_matches = 0

def percent_match(total_errs, total_matches):
    return 1.0 - (1.0*total_errs) / total_matches

def cross_validate(count_words):
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

        c = TagCounter()
        c.parse_corpus_range(train_range)
        if (count_words):
            c.only_words = count_words
            c.parse_corpus_range(test_range)
        t = Tagger(c)

        # file_validate is mapped across all files in test_range
        def file_validate(f):
            global total_errs, total_matches
            sentences = parse_file(f)
            for sent in sentences[:5]:
                words = []
                for word in sent[1:]: # sent[0] will always be START
                    words.append(word.chars)
                tagged = t.tag_words(words)
                matches = 0
                errs = 0
                for (actual_w, pred_w) in zip(sent, tagged):
                    if actual_w.tag != pred_w.tag:
                        errs += 1
                    else:
                        matches += 1
                total_errs += errs
                total_matches += matches
            #sys.stdout.write("\r%d%%" % ((total_errs+total_matches)*chunk*100./TOTAL_WORDS))
            #sys.stdout.flush()

        map_files(file_validate, test_range)
        print '%3d  %6d  %7d      %0.4f' %(i, total_errs, total_matches, percent_match(total_errs, total_matches))

        sum_err += percent_match(total_errs, total_matches)

    print 'cumulative averaged error:', (sum_err*1.0)/folds

if __name__ == '__main__':
    print 'Cross validating with some unknown words...'
    cross_validate(False)
    print '\nCross validating with NO unknown words...'
    cross_validate(True)
