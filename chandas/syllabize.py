# -*- coding: utf-8 -*-
import logging
import string

import PyICU
import regex
from indic_transliteration import sanscript

def get_graphemes(in_string):
  """ Split a devanAgarI and possibly other strings into graphemes.
  
  Example: assert syllabize.get_graphemes(u"बिक्रममेरोनामहो") == "बि क् र म मे रो ना म हो".split(" ")
  :param in_string: 
  :return: 
  """
  break_iterator = PyICU.BreakIterator.createCharacterInstance(PyICU.Locale())
  break_iterator.setText(in_string)
  i = 0
  graphemes = []
  for j in break_iterator:
    s = in_string[i:j]
    graphemes.append(s)
    i = j
  return graphemes


def is_vyanjanaanta(in_string):
  return in_string.endswith("्") or in_string.endswith("य्ँ") or in_string.endswith("व्ँ") or in_string.endswith("ल्ँ")


def get_syllables(in_string):
  """ Split devanAgarI string into syllables. Ignores spaces and punctuation.
  
  syllabize.get_syllables(u"बिक्रममेरोनामहो") == "बिक् र म मे रो ना म हो".split(" ")
  :param in_string: 
  :return: 
  """
  # Cannot do \P{Letter} below as it does not match mAtra-s and virAma-s as of 2019.
  # ऀ-़ा-ॣॲ-ॿ
  cleaned_phrase = regex.sub(r"([^ऀ-़ ा-ॣ ॲ-ॿ  ꣠-ꣽ  ᳐-᳹])", "", in_string, flags=regex.UNICODE)
  cleaned_phrase = cleaned_phrase.replace("ॐ", "ओम्")
  cleaned_phrase = cleaned_phrase.replace(" ", "")
  graphemes = get_graphemes(cleaned_phrase)
  syllables = []
  while len(graphemes) > 0:
    current_syllable = graphemes.pop(0)
    if len(graphemes) > 0 and regex.match(r"[ ꣠-ꣽ  ᳐-᳹]", graphemes[0]):
      current_syllable = current_syllable  + graphemes.pop(0)
    while len(graphemes) > 0 and is_vyanjanaanta(graphemes[0]):
      current_syllable = current_syllable  + graphemes.pop(0)
    # Deal with grapheme list like 'सा', 'म्', 'अ', 'प', 'ह', 'त्', 'यै']
    if is_vyanjanaanta(current_syllable) and len(graphemes) > 0 and regex.match(r"[ऄ-औॲ-ॷ].*", graphemes[0]):
      vyanjana = current_syllable[-2:]
      graphemes[0] = sanscript.SCHEMES[sanscript.DEVANAGARI].do_vyanjana_svara_join(vyanjana, graphemes[0])
      current_syllable = current_syllable[:-2]
    syllables.append(current_syllable)
  return syllables

def get_maatraas(in_string):
  raise NotImplemented