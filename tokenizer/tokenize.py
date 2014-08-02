#!/usr/bin/env python

# Tokenize the text from stdin

import sys
import itertools
import string
import re
import codecs

SENTENCE_PUNCTUATION = ".?!"

class Token(object):
    def __init__(self, text):
        self.text = text
        self.is_paragraph_start = False
        self.is_sentence_end = False
    
    @staticmethod
    def deserialize(s):
        if not s:
            return Token('')
        
        fields = s.split(' ')
        attributes = fields[1:]
        token = Token(fields[0])
        token.is_paragraph_start = 'start_paragraph' in attributes
        token.is_sentence_end = 'end_sentence' in attributes
        return token
        
    def value(self):
        alnumvalue = ''.join([x for x in self.text.lower() if x.isalnum()])
        return alnumvalue if alnumvalue else self.text

    def _attributes_list(self):
        attributes = []
        if self.is_sentence_end:
            attributes.append('end_sentence')
        if self.is_paragraph_start:
            attributes.append('start_paragraph')
        return attributes

    def __str__(self):
        attrs = self._attributes_list()
        attrstring = ', ' + ', '.join(attrs) if attrs else ''
        return 'T(%s%s)' % (self.text, attrstring)

    def serialize(self):
        attrs = self._attributes_list()
        attrstring = ' ' + ' '.join(attrs) if attrs else ''
        return '%s%s' % (self.text, attrstring)

class ParagraphStartToken(Token):
    def __init__(self):
        Token.__init__(self, '')
        self.is_paragraph_start = True

class SentenceEndToken(Token):
    def __init__(self, text):
        Token.__init__(self, text)
        self.is_sentence_end = True

def main():
    stdout = codecs.getwriter('utf-8')(sys.stdout)
    lines = normalize_lines(codecs.getreader('utf-8')(sys.stdin))
    for t in tokenize(lines):
        stdout.write(t.serialize())
        stdout.write('\n')

def normalize_lines(lines):
    for line in lines:
        yield line.strip()

def tokenize(lines):
    return itertools.chain.from_iterable(paragraph_start_closure(lines))

def paragraph_start_closure(lines):
    prev_was_empty = True
    for line in lines:
        if not line:
            prev_was_empty = True
            continue
        
        if prev_was_empty:
            yield [ParagraphStartToken()]
        prev_was_empty = False

        yield tokenize_line(line)

def tokenize_line(line):
    if not line:
        return []

    # \xA0 is the non-breaking space
    words = (cleanup_word(x) for x in re.split(r'[\s\xA0]', line)
             if valid_word(x))
    return [word_to_token(x) for x in words]

def valid_word(word):
    return re.match(u'[:"\'\u2018\u2019\u201C\u201D]*$', word) is None
    
def cleanup_word(word):
    num_opening = word.count("(")
    num_closing = word.count(")")
    if num_opening != num_closing:
        return word.replace("(", "").replace(")", "")
    else:
        return word

def word_to_token(word):
    if word and word[-1] in SENTENCE_PUNCTUATION:
        return SentenceEndToken(word)
    else:
        return Token(word)

if __name__ == '__main__':
    main()
