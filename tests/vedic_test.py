import pytest

from chandas.vedic import is_rk


RK_EXAMPLE = """साकञ्जा᳓नाँ सप्त᳓थमाहुरेकज᳓म् ।  
ष᳓डुद्यमा᳓ ऋ᳓षयो देवजा᳓ इ᳓ति ।  
ते᳓षामिष्टा᳓नि वि᳓हितानि धामशः᳓ ।  
स्थात्रे᳓ रेजन्ते वि᳓कृतानि रूपशः᳓ ।"""


@pytest.mark.parametrize("text", [
  RK_EXAMPLE,
  # Three pāda-s of eight syllables.
  "अग्निमीळे पुरोहितम् ।\nयज्ञस्य देवमृत्विजम् ।\nहोतारं रत्नधातमम् ॥",
  # Two half-verses of 22 syllables each.
  "वाममद्य सवितर्वाममु श्वो दिवेदिवे वाममस्मभ्यँ सावीः ।\nवामस्य हि क्षयस्य देव भूरेरया धिया वामभाजस्स्याम ।",
  # Three pāda-s; the first pāda has no daṇḍa of its own.
  "दिवा चित्तमᳵ कृण्वन्ति\nपर्जन्येनोदवाहेन ।\nपृथिवीय्ँ यद् व्युन्दन्ति ।",
])
def test_is_rk(text):
  assert is_rk(text)


@pytest.mark.parametrize("text", [
  # A single Yajuṣ formula, even though it has a Vedic accent.
  "वैश्वानरा᳓य र᳓थम् ।",
  # Prose with a comma.
  "अष्टाक्षरा गायत्री, गायत्रो ऽग्निः ।\nयावान् एवाग्निस् तम् आधत्ते ।",
  # Prose, not a half-verse.
  "श्रायन्तीयम् ब्रह्मसामम्भवति ।\nवारवन्तीयमग्निष्टोमसामम् ।",
  # Prose that happens to scan as two long lines.
  "नैतेषाम्पशूनाम्पुरोडाशा भवन्ति ग्रहपुरोडाशा ह्येते ।\nयुवँ सुराममश्विनेति सर्वदेवत्ये याज्यानुवाक्ये भवतः ।",
  # Prose whose lines end in finite verbs.
  "यत्सायन्धृतीर्जुहोति ।\nअश्वस्यैव यत्यै धृत्यै ।\nतस्मात्सायम्प्रजाः क्षेम्या भवन्ति ।",
  # More prose with finite verbs at line ends.
  "लोम छवीम् माँसम् अस्थि मज्जानम्\nतानि चात्मनस् स्पृणोति ।\nआदित्यस्य च सायुज्यङ् गच्छति ।",
  "अपाय्ँ यो द्रवणे रसः ।\nतम् अहम् अस्मा आमुष्यायणाय\nतेजसे ब्रह्मवर्चसाय गृह्णामि ।",
  # Prose with an explicit prose marker (खलु).
  "यज्ञमुखे यज्ञमुखे वै क्रियमाणे यज्ञँ रक्षाँसि जिघाँसन्ति ।\nएतर्हि खलु वा एतद् यज्ञमुखयं यर्ह्येनद् आहुतिरश्नुते ।",
])
def test_is_not_rk(text):
  assert not is_rk(text)
