# -*- coding: utf-8 -*-
import logging
import string
from itertools import takewhile

import icu
import regex

from indic_transliteration import sanscript

def get_graphemes(in_string):
  """ Split a devanAgarI and possibly other strings into graphemes.
  
  Example: assert syllabize.get_graphemes(u"बिक्रममेरोनामहो") == "बि क्र म मे रो ना म हो".split(" ")
  :param in_string: 
  :return: 
  """
  break_iterator = icu.BreakIterator.createCharacterInstance(icu.Locale())
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


def has_vowel(in_string):
  return bool(regex.fullmatch(".*[ऄ-औ ऺ-ऻ ा-ौ ॎ-ॏ ॲ-ॷ].*".replace(" ", ""), in_string, flags=regex.UNICODE) or regex.match(".*[क-हक़-य़ॸ-ॿ](?=([^्]|$))", in_string, flags=regex.UNICODE))


def begins_with_vowel(in_string):
  return bool(regex.fullmatch(r"[ऄ-औॲ-ॷ].*", in_string, flags=regex.UNICODE))


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
  cleaned_phrase = regex.sub(r"([क-हक़-य़ॸ-ॿ]्)([ऄ-औॠॡॲ-ॷ])", lambda x: sanscript.SCHEMES[sanscript.DEVANAGARI].do_vyanjana_svara_join(x.group(1), x.group(2)), cleaned_phrase)
  syllables = []
  while len(cleaned_phrase) > 0:
    # possible vyanjanas without vowels + svara or vyanjana + possible vowel marks + possible yogavAhas + possible accents + possible vyanjanas without vowels
    match = regex.match(r"([क-हक़-य़ॸ-ॿ]्)*[ऄ-हक़-ॡॲ-ॿ][ऺ-ॏॢ-ॣॕ-ॗ]*[ऀ-ः]*[ ꣠-ꣽ  ᳐-᳹]*([क-हक़-य़ॸ-ॿ]्ँ?)*", cleaned_phrase)
    current_syllable = match.group(0)
    cleaned_phrase = cleaned_phrase.replace(match.group(0), "", 1)
    if len(current_syllable) > 0:
      syllables.append(current_syllable)
  return syllables


def get_syllable_weight(syllable):
  if regex.search("[् आ ई ऊ ॠ ए ऐ ॠ ॡ औ ओ औ ॐ ऻ ा ी ू ॄ ॗॣ ॎ े ै ो ौ ॕ ं ः  ᳢-ᳬ ᳮ ᳯ ᳰ ᳱ ᳲ ᳳ ᳵ ᳶ]".replace(" ", ""), syllable, flags=regex.UNICODE):
    return "G"
  else:
    return "L"


def to_weight_list(line_in):
  syllables = get_syllables(line_in)
  return [get_syllable_weight(syllable) for syllable in syllables]
  