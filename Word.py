import string

class Word:
    def __init__(self, chars, tag):
        self.chars = string.lower(chars)    # characters that make up the word
        self.true_chars = chars             # characters that make up the word
        self.tag = tag                      # POS tag for the word
    def __repr__(self):
        return self.true_chars + '/' + self.tag
    def __str__(self):
        return self.__repr__()
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.chars == other.chars and self.tag == other.tag)
    def is_end(self):
        return self.tag == '.' or self.tag == ')'

