# -*- coding: utf-8 -*-
"""Heuristics for Vedic mantras.

The Taittirīya Saṃhitā and related texts contain two kinds of mantras:

* **Ṛk**-s, which are metrical (usually three or four pāda-s of 8, 11 or 12
  syllables), and
* **Yajuṣ**-s, which are prose formulas.

The functions here are deliberately conservative: they only recognise
unambiguous metrical ṛk-s.  A one-line text is *not* called a ṛk even when its
syllable count happens to be 8, 11 or 12, because many Yajuṣ formulas have the
same length.
"""

import html

import regex

from chandas import syllabize


# Syllable counts of the common Vedic pāda-s (gāyatrī/anuṣṭubh, triṣṭubh,
# jagatī).  A few ṛk-s are printed as two half-verses, each containing two
# pāda-s; those half-verses have 21-24 syllables.
PADA_LENGTHS = (8, 11, 12)
HALF_VERSE_LENGTHS = (21, 22, 23, 24)

_VEDIC_ACCENTS = regex.compile(r"[\u1CD0-\u1CFF\u0951-\u0954]")
_COMMENT = regex.compile(r"\+\+\+.*?\+\+\+", flags=regex.DOTALL)
_BR = regex.compile(r"<br\s*/?>", flags=regex.IGNORECASE)
_TAG = regex.compile(r"<[^>]+>")
_DANDA_END = regex.compile(r"[।॥](?:\s*[०-९0-9]+)?\s*[।॥]?\s*$")
_PROSE_PUNCTUATION = regex.compile(r"[,;?]")
_DEVANAGARI = regex.compile(r"[\u0900-\u097F]")
# Two-line half-verses are more likely to be mistaken for prose, so require
# them to be free of these common prose markers.
_PROSE_MARKERS = regex.compile(
  r"(?:तस्मात्|भवति|भवन्ति|भवताम्|स्यात्|कुर्यात्|विद्यात्|ब्रूयात्|"
  r"जुहुयात्|दध्यात्|अवरुन्धे|विन्दते|आप्नोति|अश्नुते|नयति|चर्यते|"
  r"तिष्ठते|उदजयत्|उदजयन्|अकुर्वत|जुहोति|गृह्णाति|ददाति)"
)
_PROSE_LINE_END = regex.compile(
  r"(?:भवति|भवन्ति|भवेत्|स्यात्|जुहोति|निर्वपेत्|सम्पद्यन्ते|"
  r"स्पृणोति|गृह्णामि|प्रतितिष्ठति|समारोहति|पर्यावर्तते|दधाति|"
  r"गच्छति|अश्नुते|वृश्च्यते|आलभ्यते|गृह्यते|समर्धयन्ति|यतिषजति|"
  r"स्तुवते|जयति|व्याकरोत्|रश्नुते)\s*[।॥]?\s*$"
)
_STRONG_PROSE = regex.compile(r"(?:खलु|इत्याह|इत्य्\s*आह|ब्रवीद्|उवाच)")


def _clean_text(text):
  """Remove Markdown/HTML markup and Vedic accents from *text*."""
  text = html.unescape(text)
  text = _COMMENT.sub("", text)
  text = _BR.sub("\n", text)
  text = _TAG.sub(" ", text)
  text = text.replace("**", "").replace("~~", "")
  # In this corpus ``य्ँ``/``व्ँ`` stand for ``यं``/``वं``.
  text = regex.sub(r"्ँ", "ं", text)
  text = _VEDIC_ACCENTS.sub("", text)
  return text


def _get_lines(text):
  """Return the non-empty Devanagari lines of *text* after cleaning."""
  lines = []
  for line in _clean_text(text).splitlines():
    line = line.strip()
    line = regex.sub(r"^\s*>\s*", "", line)
    line = regex.sub(r"\[\s*[०-९0-9]+\s*\]", "", line)
    line = regex.sub(r"\(\s*[०-९0-9]+\s*\)", "", line)
    line = regex.sub(r"॥\s*[०-९0-9]+\s*॥", "", line)
    line = line.strip()
    if line and _DEVANAGARI.search(line):
      lines.append(line)
  return lines


def _syllable_count(line):
  """Return the number of syllables in *line*, or ``None`` on failure."""
  try:
    return len(syllabize.get_syllables(line))
  except Exception:
    return None


def _ends_with_danda(line):
  return bool(_DANDA_END.search(line))


def is_rk(text):
  """Return whether *text* looks like a metrical Vedic ṛk.

  A text is recognised as a ṛk when:

  * it has three or four lines, each scanning as a pāda of 8, 11 or 12
    syllables, or
  * it has two lines, each scanning as a half-verse of 21-24 syllables;

  and, in either case, the final line ends with a daṇḍa.  For two-line
  half-verses both lines must end with a daṇḍa.  In three- or four-line
  ṛk-s the earlier pāda-s are often separated only by line breaks, so an
  internal daṇḍa is not required.  Texts containing prose punctuation
  (comma, semicolon or question mark) or ending in a common prose verb are
  rejected.

  A single line is never considered a ṛk: an 8-, 11- or 12-syllable line is
  just as likely to be a Yajuṣ formula.

  :param text: Sanskrit text, possibly containing Markdown/HTML markup.
  :return: ``True`` if *text* is a ṛk, ``False`` otherwise.
  """
  lines = _get_lines(text)
  if len(lines) < 2 or len(lines) > 4:
    return False

  if any(_PROSE_PUNCTUATION.search(line) for line in lines):
    return False
  if any(_STRONG_PROSE.search(line) for line in lines):
    return False
  if any(_PROSE_LINE_END.search(line) for line in lines):
    return False

  counts = [_syllable_count(line) for line in lines]
  if any(count is None for count in counts):
    return False

  if len(lines) == 2:
    if _PROSE_MARKERS.search(" ".join(lines)):
      return False
    if not (all(count in HALF_VERSE_LENGTHS for count in counts)
            and abs(counts[0] - counts[1]) <= 2):
      return False
  else:
    if any(count not in PADA_LENGTHS for count in counts):
      return False

  if len(lines) == 2:
    if not all(_ends_with_danda(line) for line in lines):
      return False
  elif not _ends_with_danda(lines[-1]):
    return False

  return True
