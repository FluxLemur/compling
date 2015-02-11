''' Runs the cross-validation routines to test the accuracy of the Tagger '''
from Tagger import *
from CorpusParser import *

# Some unknown words scenario
folds = 10
chunk = 100 / folds

total_errs = [0]
total_matches = [0]

for i in xrange(1):
    train_range = range(0, chunk*i) + range(chunk*(i+1), 100)
    test_range = range(chunk*i, chunk*(i+1))
    #print i, len(train_range), len(test_range)
    c = TagCounter()
    c.parse_corpus_range(train_range)
    #print sum(c.word_count.values())/553177.0
    t = Tagger(c)

    def file_validate(f):
        sentences = parse_file(f)
        for sent in sentences:
            words = []
            for word in sent[1:]: # sent[0] will always be START
                words.append(word.chars)
            tagged = t.tag_words(words)
            matches = 0
            errs = 0
            for (actual_w, pred_w) in zip(sent, tagged):
                if actual_w.tag != pred_w.tag:
                    #print actual_w, pred_w
                    errs += 1
                else:
                    matches += 1
            total_errs[0] += errs
            total_matches[0] += matches
        print total_errs, total_matches, (1.0 - (1.0*total_errs[0]) / total_matches[0])

    map_files(file_validate, test_range)
