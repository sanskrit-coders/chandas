import pytest
import logging
import json
import os

from chandas import syllabize


# Remove all handlers associated with the root logger object.

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(asctime)s:%(module)s:%(filename)s:%(lineno)d %(message)s"
)

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'syllabizationTests.json')

test_data = {}
with open(TEST_DATA_PATH) as test_data_file:
    # noinspection PyRedeclaration
    test_data = json.loads(test_data_file.read())
# logging.info(test_data["tests"])


def test_graphemes():
    assert syllabize.get_graphemes(u"बिक्रममेरोनामहो") == "बि क्र म मे रो ना म हो".split(" ")


@pytest.mark.parametrize("test_case", [x for x in test_data["syllableExtractionTests"] if "weightsString" in x])
def test_get_syllable_weight(test_case):
    logging.debug(str(test_case))
    assert syllabize.to_weight_list(test_case["phrase"]) == test_case["weightsString"].split(" ")


@pytest.mark.parametrize("test_case", test_data["syllableExtractionTests"])
def test_syllables(test_case):
    logging.debug(str(test_case))
    assert syllabize.get_syllables(test_case["phrase"]) == test_case["syllablesString"].split(" ")


@pytest.mark.parametrize("test_case", "म मत् श्री स्त्री".split(" "))
def test_has_vowel(test_case):
    assert syllabize.has_vowel(test_case)

@pytest.mark.parametrize("test_case", "त् श्र्".split(" "))
def test_not_has_vowel(test_case):
    assert not syllabize.has_vowel(test_case)

@pytest.mark.parametrize("test_case", "मत् तल् तल्ँ".split(" "))
def test_is_vyanjanAnta(test_case):
    assert syllabize.is_vyanjanaanta(test_case)


@pytest.mark.parametrize("test_case", "तँ".split(" "))
def test_not_is_vyanjanAnta(test_case):
    assert not syllabize.is_vyanjanaanta(test_case)


