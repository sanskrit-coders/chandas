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
# pāda-s; those half-verses have 15-16 (anuṣṭubh) or 20-24 (triṣṭubh/jagatī)
# written syllables, or 15-16 + 7-8 for two-line gāyatrī.
PADA_LENGTHS = (8, 11, 12)
HALF_VERSE_LENGTHS = (21, 22, 23, 24)

_VEDIC_ACCENTS = regex.compile(r"[\u1CD0-\u1CFF\u0951-\u0954\uA8E0-\uA8FF]")
_COMMENT = regex.compile(r"\+\+\+.*?\+\+\+", flags=regex.DOTALL)
_BR = regex.compile(r"<br\s*/?>", flags=regex.IGNORECASE)
_TAG = regex.compile(r"<[^>]+>")
_DANDA_END = regex.compile(r"[।॥](?:\s*[०-९0-9]+)?\s*[।॥]?\s*$")
_PROSE_PUNCTUATION = regex.compile(r"[,;?]|\s-\s|[\"“”](?!ति\s*[।॥])")
_DEVANAGARI = regex.compile(r"[\u0900-\u097F]")
# Two- and three-line passages are more likely to be mistaken for prose, so
# require them to be free of these common prose markers.
_PROSE_MARKERS = regex.compile(
  r"(?:(?<!\S)तस्मा[तद]्|भवति|भवन्ति|भवन्त्य्|भवताम्|"
  r"स्या[तद]्|कुर्या[तद]्|विद्या[तद]्|ब्रूया[तद]्|"
  r"जुहुया[तद]्|दध्या[तद]्|अवरुन्धे|विन्दते|आप्नोति|अश्नुते|नयति|चर्यते|"
  r"तिष्ठते|उदजयत्|उदजयन्|अकुर्वत|जुहोति|गृह्णाति|ददाति|"
  r"आलभते|आलभेत|निर्वपति|निर्वपेत्|यजते|यजेत|पशून्\s*आलभ|"
  r"कामो\s*येन|विदुस्\s*ते|अनुब्रूया[तद]्|अनु\s*ब्रूया[तद]्|यजे[तद]्|नमस्करोमि)"
)
_PROSE_LINE_END = regex.compile(
  r"(?:भवति|भवन्ति|भवतः|भवेत्|भवेयुः|स्यात्|स्यूः|जुहोति|जुह्वति|निर्वपेत्|निर्वपति|सम्पद्यन्ते|"
  r"स्पृणोति|गृह्णामि|गृह्णाति|प्रतितिष्ठति|समारोहति|समारोहयते|पर्यावर्तते|दधाति|"
  r"गच्छति|अश्नुते|वृश्च्यते|आलभ्यते|गृह्यते|समर्धयन्ति|यतिषजति|"
  r"स्तुवते|जयति|व्याकरोत्|रश्नुते|विन्दते|विन्दन्ते|अवरुन्धे|अवरुन्धते|"
  r"ब्रूयात्|विद्यात्|कुर्यात्|जुहुयात्|यजेत|आलभते|आलभेत|ददाति|"
  r"पचति|पच्यते|बध्नाति|मुञ्चति|छिनत्ति|भिनत्ति|जनयति|असृजत|असृजन्त|"
  r"अभवत्|अभवन्|अकरोत्|अकुर्वन्|अकुर्वत|अब्रवीत्|अब्रुवन्|अजयित्|"
  r"ष्ठापयति|स्थापयति|रोहति|रोहन्ति|आप्नोति|आप्नुवन्ति|उपाप्नोति|नाप्नुवन्|आप्यते|"
  r"अतिरिच्यते|अति\s*रिच्यते|प्रजायते|प्र\s*जायते|प्रजायन्ते|प्र\s*जायन्ते|"
  r"कल्पते|कल्पन्ते|सीदति|सीदन्ति|तिष्ठति|तिष्ठन्ति|शिष्यते|हन्यते|"
  r"(?<!\S)सूयते|म्रियते|म्रियन्ते|अन्वाहरति|क्रीणाति|हूयन्ते|ध्यायति|"
  r"पवयते|प्र\s*युञ्जते|परिषिञ्चति|युनक्ति|उपावर्तत|अवयजते|वपति)\s*[।॥]?\s*$"
)
_STRONG_PROSE = regex.compile(
  r"(?:खलु|(?<!\S)वाव(?!\S)|एतर्ह[ि्य]|[इि]त्याह|इत्य्\s*आह|[\"”\x27‘’]त्य्?\s*आह|"
  r"सोऽब्रवीत्|इत्यब्रवीत्|(?<!अथ)[अाऽ]ब्रवी[तद]्|उवाच|प्रायश्चित्ति|वरुद?्ध्यै|"
  r"व्यावृत्त्यै|[अाऽ]स्पर्धन्त|उपाधावन्|मन्यमानस्\s*स|चक्षत\s*इति|"
  r"(?<!\S)(?:एष|पशवो|असौ)\s+वै(?!\S)|तद्\s+अयम्\s+अग्निः|तस्य\s+प्राण\s+एव)"
)
# Sites where written sandhi / semivowel clusters commonly resolve into an
# extra metrical syllable in Vedic recitation (vyūha / kṣaipra / abhinihita).
_VYUHA = regex.compile(
  r"(?:्[यव]|(?<![अआइईउऊऋॠऌॡएऐओऔ])[यव][ुूृ]|ऽ|[ाीूृॄ][नण]ा[ंम्]|ज्ये|त्रे|श्रे|प्रे|द्वे)"
)


def _clean_text(text):
  """Remove Markdown/HTML markup and Vedic accents from *text*."""
  text = html.unescape(text)
  text = _COMMENT.sub("", text)
  text = _BR.sub("\n", text)
  text = _TAG.sub(" ", text)
  text = text.replace("**", "").replace("~~", "").replace("{", "").replace("}", "")
  text = _VEDIC_ACCENTS.sub("", text)
  # In Taittirīya orthography ``य्ँ``/``व्ँ``/``ल्ँ`` represent a nasalised
  # consonant coda (anunāsika) rather than an extra syllable.
  text = regex.sub(r"्ँ|ँ्", "्", text)
  # Strip stray nuktas, duplicate virāmas, and orphaned vowel signs/virāmas so
  # syllabization does not fail on minor OCR/encoding artifacts.
  text = regex.sub(r"\u093c", "", text)
  text = regex.sub(r"्+", "्", text)
  text = regex.sub(r"(?<![\u0915-\u0939\u0958-\u095F])[\u093E-\u094D\u0962\u0963]+", "", text)
  return text


def _get_lines(text):
  """Return the non-empty Devanagari lines of *text* after cleaning."""
  lines = []
  for line in _clean_text(text).splitlines():
    line = line.strip()
    line = regex.sub(r"^\s*>\s*", "", line)
    line = regex.sub(r"^-\s*", "", line)
    line = regex.sub(r"\[\s*[०-९0-9]+\s*\]", "", line)
    line = regex.sub(r"\(\s*[०-९0-9]+\s*\)", "", line)
    line = regex.sub(r"॥\s*[०-९0-9]+\s*॥", "॥", line)
    line = regex.sub(r"^[\"\x27“”‘’]+|[\"\x27“”‘’]+$", "", line).strip()
    if line and _DEVANAGARI.search(line):
      lines.append(line)
  if len(lines) >= 4 and regex.fullmatch(r"इति\s*[।॥]*", lines[-1]):
    lines.pop()
  return lines


def _syllable_count(line):
  """Return the number of syllables in *line*, or ``None`` on failure."""
  try:
    return len(syllabize.get_syllables(line))
  except Exception:
    return None


def _vyuha_count(line):
  """Return the number of potential metrical resolution (vyūha) sites in *line*."""
  return len(_VYUHA.findall(line))


def _ends_with_danda(line):
  return bool(_DANDA_END.search(line))


def is_rk(text):
  """Return whether *text* looks like a metrical Vedic ṛk.

  A text is recognised as a ṛk when:

  * it has three, four or five lines scanning as pāda-s of the 8-syllable
    family (gāyatrī, anuṣṭubh, paṅkti, allowing +/-1 syllable on at most one
    pāda for nicṛt/bhūrik/vyūha) or the 11/12-syllable family (triṣṭubh,
    jagatī, uṣṇih, allowing Vedic vyūha resolution), or
  * it has two lines scanning as half-verses of triṣṭubh/jagatī (20-24
    syllables each), anuṣṭubh (15-16 syllables each), or two-line gāyatrī
    (15-16 + 7-8 syllables);

  and, in either case, the lines carry appropriate daṇḍa punctuation.  For
  two-line half-verses both lines must end with a daṇḍa.  In multi-line ṛk-s
  the earlier pāda-s (or occasionally the final pāda) may be separated only by
  line breaks.  Texts containing prose punctuation or common Brāhmaṇa prose
  markers/verbs are rejected.

  A single line is never considered a ṛk: an 8-, 11- or 12-syllable line is
  just as likely to be a Yajuṣ formula.

  :param text: Sanskrit text, possibly containing Markdown/HTML markup.
  :return: ``True`` if *text* is a ṛk, ``False`` otherwise.
  """
  lines = _get_lines(text)
  if len(lines) < 2 or len(lines) > 5:
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
  vyuhas = [_vyuha_count(line) for line in lines]

  if len(lines) == 2:
    if not all(_ends_with_danda(line) for line in lines):
      return False
    if _PROSE_MARKERS.search(" ".join(lines)):
      return False
    c0, c1 = counts
    v0, v1 = vyuhas
    is_tristubh_jagati_hv = (
      20 <= c0 <= 24
      and 20 <= c1 <= 24
      and (
        abs(c0 - c1) <= 2
        or (min(c0, c1) == 20 and max(c0, c1) == 23 and (v0 >= 2 if c0 == 20 else v1 >= 2))
      )
      and (c0 >= 21 or v0 >= 1)
      and (c1 >= 21 or v1 >= 1)
    )
    is_anustubh_hv = (
      (c0 == 16 and c1 == 16)
      or (c0 == 16 and c1 == 15 and v1 >= 1)
      or (c0 == 15 and c1 == 16 and v0 >= 1)
    )
    is_gayatri_hv = (
      (c0 == 16 and c1 == 8)
      or (c0 == 15 and v0 >= 1 and c1 == 8)
      or (c0 == 16 and c1 == 7 and v1 >= 1)
    )
    if not (is_tristubh_jagati_hv or is_anustubh_hv or is_gayatri_hv):
      return False
  else:
    min_dandas = 2 if len(lines) == 4 else len(lines) - 1
    if not (_ends_with_danda(lines[-1]) or sum(_ends_with_danda(l) for l in lines) >= min_dandas):
      return False
    if len(lines) == 3 and _PROSE_MARKERS.search(" ".join(lines)):
      return False

    is_exact = len(lines) in (3, 4) and all(c in PADA_LENGTHS for c in counts)
    is_gayatri_family = (
      len(lines) in (3, 4, 5)
      and all(7 <= c <= 9 for c in counts)
      and sum(1 for c in counts if c == 8) >= len(lines) - 1
    )
    is_tristubh_4 = (
      len(lines) == 4
      and all(9 <= c <= 13 for c in counts)
      and sum(1 for c in counts if c in (11, 12)) >= 2
      and all(v >= 1 for c, v in zip(counts, vyuhas) if c == 9)
      and (
        sum(1 for c in counts if c in (11, 12)) >= 3
        or all(v >= 1 for c, v in zip(counts, vyuhas) if c == 10)
      )
    )
    is_tristubh_3 = (
      len(lines) == 3
      and sum(1 for c in counts if c == 11) == 2
      and all(10 <= c <= 11 and (c == 11 or v >= 1) for c, v in zip(counts, vyuhas))
    )
    if not (is_exact or is_gayatri_family or is_tristubh_4 or is_tristubh_3):
      return False

  return True
