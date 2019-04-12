# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys, os
sys.path.append(os.path.abspath('..'))
from chandas import syllabize
import unicodecsv
import codecs

def count_mAtrAs(pattern_str):
  graphemes = syllabize.get_graphemes(pattern_str)
  mAtrA_count = 0
  for grapheme in graphemes:
    if grapheme == 'द':
      mAtrA_count = mAtrA_count + 1
    if grapheme == 'दा':
      mAtrA_count = mAtrA_count + 2
  return mAtrA_count

# def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))
def get_common_prefix(strings):
  b = zip(*map(lambda x:   syllabize.get_graphemes(x), strings))
  from itertools import takewhile
  prefix_tuples = takewhile(lambda x: x[0]*len(x) == "".join(x), b)
  result = " ".join(x[0] for x in prefix_tuples)
  return result

def _reverse(string):
  return string[::-1]

def get_common_suffix(strings):
  s = get_common_prefix(map(_reverse, strings))
  return _reverse(s)

if __name__ == '__main__':
  data_file = u'data/Chandas छन्दः - सम.csv'
  sama_file = u'data/sama_mAtrA.csv'
  
  with open(data_file, 'r') as csvfile, codecs.open(sama_file, 'w', 'utf-8') as outfile:
    chandas_reader =  unicodecsv.reader(csvfile, encoding='utf-8')
    for chandas in chandas_reader:
      mAtrA_count = count_mAtrAs(chandas[3])
      print(mAtrA_count)
      outfile.write('%d\n' % mAtrA_count)
