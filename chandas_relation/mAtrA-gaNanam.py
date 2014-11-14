# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import sys, os
sys.path.append(os.path.abspath('..'))
import util
import unicodecsv
import codecs
from itertools import takewhile, izip

def count_mAtrAs(pattern_str):
  graphemes = util.get_graphemes(pattern_str)
  mAtrA_count = 0
  for grapheme in graphemes:
    if grapheme == 'द':
      mAtrA_count = mAtrA_count + 1
    if grapheme == 'दा':
      mAtrA_count = mAtrA_count + 2
  return mAtrA_count

data_file = u'data/Chandas छन्दः - सम.csv'
sama_file = u'data/sama_mAtrA.csv'

with open(data_file, 'r') as csvfile, codecs.open(sama_file, 'w', 'utf-8') as outfile:
  chandas_reader =  unicodecsv.reader(csvfile, encoding='utf-8')
  for chandas in chandas_reader:
    mAtrA_count = count_mAtrAs(chandas[3])
    print(mAtrA_count)
    outfile.write('%d\n' % mAtrA_count)
