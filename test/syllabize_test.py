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
    assert syllabize.get_graphemes(u"बिक्रममेरोनामहो") == "बि क् र म मे रो ना म हो".split(" ")


def test_is_vyanjanAnta():
    assert syllabize.is_vyanjanaanta("तल्")
    assert syllabize.is_vyanjanaanta("तल्ँ")
    assert not syllabize.is_vyanjanaanta("तँ")


@pytest.mark.parametrize("test_case", test_data["tests"])
def test_syllables(test_case):
    logging.debug(str(test_case))
    assert syllabize.get_syllables(test_case["phrase"]) == test_case["syllablesString"].split(" ")