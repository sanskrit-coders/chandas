# -*- coding: utf-8 -*-
from __future__ import unicode_literals
# from PyICU import BreakIterator
# To install pyicu:
# sudo apt-get install libicu-dev
# sudo easy_install pyicu
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

a = u"बिक्रम मेरो नाम हो"
print get_graphemes(a)