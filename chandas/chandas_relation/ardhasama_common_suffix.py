# -*- coding: utf-8 -*- 
import sys, os
sys.path.append(os.path.abspath('..'))
import util

import unicodecsv
import codecs
from itertools import takewhile, izip

# def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))
def get_common_prefix(strings):
  b = zip(*map(lambda(x):   util.get_graphemes(x), strings))
  prefix_tuples = takewhile(lambda(x): x[0]*len(x) == "".join(x), b)
  result = " ".join(x[0] for x in prefix_tuples)
  return result

def reverse(string):
  return string[::-1]

def get_common_suffix(strings):
  s = get_common_prefix(map(reverse, strings))
  return reverse(s)

data_file = u'data/Chandas छन्दः - अर्धसम.csv'
out_file = u'data/ardhasama_prefix.csv'
suffix_file_name = u'data/ardhasama_suffix.csv'

with open(data_file, 'r') as csvfile, codecs.open(out_file, 'w', 'utf-8') as outfile, codecs.open(suffix_file_name, 'w', 'utf-8') as suffix_file:
  chandas_reader =  unicodecsv.reader(csvfile, encoding='utf-8')
  for chandas in chandas_reader:
    prefix = get_common_prefix([chandas[3], chandas[5]])
    outfile.write(prefix + '\n')
    suffix = get_common_suffix([chandas[3], chandas[5]])
    suffix_file.write(suffix + '\n')
