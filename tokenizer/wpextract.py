#!/usr/bin/env python

# Extracts the textual content of posts from a wordpress export file.

import sys
import os
import os.path
import codecs
import re
import xml.etree.ElementTree as ET
from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

def extract_contents(export_file_name, destdir):
    TITLE_TAG = 'title'
    CONTENT_TAG = '{http://purl.org/rss/1.0/modules/content/}encoded'
    POST_TYPE_TAG = '{http://wordpress.org/export/1.2/}post_type'
    POST_ID_TAG = '{http://wordpress.org/export/1.2/}post_id'

    make_dir(destdir)

    count = 0
    tree = ET.parse(export_file_name)
    root = tree.getroot()
    for item in root.findall('./channel/item'):
        post_type = item.find(POST_TYPE_TAG).text
        content = item.find(CONTENT_TAG).text
        if post_type == 'post' and content is not None:
            postid = item.find(POST_ID_TAG).text
            f = codecs.open(os.path.join(destdir, str(postid)), 'w',
                            encoding='utf-8')
            f.write(item.find(TITLE_TAG).text)
            f.write('\n\n')
            f.write(format_content(content))

            count += 1
    
    print 'Processed %d posts' % count

def format_content(content):
    without_html_tags = strip_html_tags(content)
    formated = strip_wp_captions(without_html_tags)
    return formated

def strip_html_tags(text):
    parser = PlainTextFromHTMLParser(strip_code_tags=True)
    parser.feed('<html>' + text + '</html>')
    return parser.get_plain_text()

def strip_wp_captions(text):
    text2 = re.sub(r'^\[caption [^\]]+\] *(.*)\[/caption\]$', '\\1', text,
                  flags=re.MULTILINE)
    return re.sub(r'^\[slideshare.*\]$', '', text2,
                  flags=re.MULTILINE)

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

class PlainTextFromHTMLParser(HTMLParser):

    PARAGRAPH_TAGS = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote']
    PARAGRAPH_END_TAGS = PARAGRAPH_TAGS + ['br', 'li']
    
    def __init__(self, strip_code_tags=False):
        HTMLParser.__init__(self)
        self.buffer = []
        self.strip_code_tags = strip_code_tags
        self.ignoring = False
    
    def handle_data(self, data):
        if not self.ignoring:
            self.buffer.append(data)

    def handle_starttag(self, tag, attrs):
        if tag == 'code' and self.strip_code_tags:
           self.ignoring = True 
        if not self.ignoring and tag in self.PARAGRAPH_TAGS:
            self.buffer.append('\n\n')

    def handle_endtag(self, tag):
        if tag == 'code' and self.strip_code_tags:
           self.ignoring = False
        if not self.ignoring and tag in self.PARAGRAPH_END_TAGS:
            self.buffer.append('\n\n')

    def handle_entityref(self, name):
        if not self.ignoring:
            c = unichr(name2codepoint[name])
            self.buffer.append(c)

    def handle_charref(self, name):
        if not self.ignoring:
            if name.startswith('x'):
                c = unichr(int(name[1:], 16))
            else:
                c = unichr(int(name))
            self.buffer.append(c)

    def get_plain_text(self):
        return ''.join(self.buffer)

if __name__ == '__main__':
    extract_contents(sys.argv[1], 'posts')
