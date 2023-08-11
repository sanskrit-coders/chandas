# -*- coding: utf-8 -*-
import logging

import regex

from indic_transliteration import sanscript


def get_graphemes(in_string):
  """ Split a devanAgarI and possibly other strings into graphemes.
  
  Example: assert syllabize.get_graphemes(u"बिक्रममेरोनामहो") == "बि क्र म मे रो ना म हो".split(" ")
  :param in_string: 
  :return: 
  """
  import icu
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
  dev_scheme = sanscript.SCHEMES[sanscript.DEVANAGARI]
  return bool(regex.findall("[%s%s]" % (dev_scheme.PATTERN_INDEPENDENT_VOWEL, dev_scheme.PATTERN_DEPENDENT_VOWEL), in_string, flags=regex.UNICODE) or regex.match(".*[%s](?=([^्]|$))" % (dev_scheme.PATTERN_VYANJANA), in_string, flags=regex.UNICODE))


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

  dev_scheme = sanscript.SCHEMES[sanscript.DEVANAGARI]
  cleaned_phrase  = in_string
  cleaned_phrase = regex.sub("[%s]" % dev_scheme.PATTERN_OM, "ओम्", cleaned_phrase)
  cleaned_phrase = regex.sub(r"([^%s%s%s%s%s%s])" % (dev_scheme.PATTERN_INDEPENDENT_VOWEL, dev_scheme.PATTERN_VYANJANA, dev_scheme.PATTERN_DEPENDENT_VOWEL, dev_scheme.PATTERN_YOGAVAAHA, dev_scheme.PATTERN_ACCENT, dev_scheme.PATTERN_CONSONANT_MODIFIER), "", cleaned_phrase, flags=regex.UNICODE)
  cleaned_phrase = cleaned_phrase.replace(" ", "")
  cleaned_phrase = regex.sub(r"(%s)([%s])" % (dev_scheme.PATTERN_VYANJANA_WITHOUT_VOWEL, dev_scheme.PATTERN_INDEPENDENT_VOWEL), lambda x: sanscript.SCHEMES[sanscript.DEVANAGARI].do_vyanjana_svara_join(x.group(1), x.group(2)), cleaned_phrase)
  syllables = []
  while len(cleaned_phrase) > 0:
    # possible vyanjanas without vowels + svara or vyanjana + possible vowel marks + possible yogavAhas + possible accents + possible vyanjanas without vowels
    match = regex.match((r"(%s)*[%s%s]़?[%s]*[%s]*[%s]*(%sँ?)*" % (dev_scheme.PATTERN_VYANJANA_WITHOUT_VOWEL,dev_scheme.PATTERN_INDEPENDENT_VOWEL, dev_scheme.PATTERN_VYANJANA, dev_scheme.PATTERN_DEPENDENT_VOWEL, dev_scheme.PATTERN_YOGAVAAHA, dev_scheme.PATTERN_ACCENT, dev_scheme.PATTERN_VYANJANA_WITHOUT_VOWEL, )), cleaned_phrase)
    if match is None:
      message = "No match! Input - %s Remaining - %s" % (in_string, cleaned_phrase)
      logging.fatal(message)
      raise ValueError(message)
    current_syllable = match.group(0)
    cleaned_phrase = cleaned_phrase.replace(match.group(0), "", 1)
    if len(current_syllable) > 0:
      syllables.append(current_syllable)
  return syllables


def get_syllable_weight(syllable):
  dev_scheme = sanscript.SCHEMES[sanscript.DEVANAGARI]
  if regex.findall(r"[%s%s%s]" % (dev_scheme.PATTERN_GURU_INDEPENDENT_VOWEL, dev_scheme.PATTERN_GURU_DEPENDENT_VOWEL, dev_scheme.PATTERN_GURU_YOGAVAAHA), syllable):
    return "G"
  elif regex.findall(r"[%s%s]़?[%s]*[%s]*[%s]*(%s)+" % (dev_scheme.PATTERN_INDEPENDENT_VOWEL, dev_scheme.PATTERN_VYANJANA, dev_scheme.PATTERN_DEPENDENT_VOWEL, dev_scheme.PATTERN_YOGAVAAHA, dev_scheme.PATTERN_ACCENT, dev_scheme.PATTERN_VYANJANA_WITHOUT_VOWEL, ), syllable):
    return "G"
  else:
    return "L"


def to_weight_list(line_in):
  syllables = get_syllables(line_in)
  return [get_syllable_weight(syllable) for syllable in syllables]
  