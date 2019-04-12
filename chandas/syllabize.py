# -*- coding: utf-8 -*-
import logging

import PyICU


def get_graphemes(a):
  b = PyICU.BreakIterator.createCharacterInstance(PyICU.Locale())
  b.setText(a)
  i = 0
  graphemes = []
  for j in b:
    s = a[i:j]
    graphemes.append(s)
    i = j
  return graphemes



if __name__ == '__main__':
  a = u"बिक्रम मेरो नाम हो"
  logging.info(get_graphemes(a))