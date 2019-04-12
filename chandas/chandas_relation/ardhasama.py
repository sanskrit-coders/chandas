# -*- coding: utf-8 -*- 
import os
import sys

from chandas import chandas_relation

sys.path.append(os.path.abspath('..'))

import unicodecsv
import codecs

if __name__ == '__main__':
  data_file = u'data/Chandas छन्दः - अर्धसम.csv'
  out_file = u'data/ardhasama_prefix.csv'
  suffix_file_name = u'data/ardhasama_suffix.csv'
  
  with open(data_file, 'r') as csvfile, codecs.open(out_file, 'w', 'utf-8') as outfile, codecs.open(suffix_file_name, 'w', 'utf-8') as suffix_file:
    chandas_reader =  unicodecsv.reader(csvfile, encoding='utf-8')
    for chandas in chandas_reader:
      prefix = chandas_relation.get_common_prefix([chandas[3], chandas[5]])
      outfile.write(prefix + '\n')
      suffix = chandas_relation.get_common_suffix([chandas[3], chandas[5]])
      suffix_file.write(suffix + '\n')
