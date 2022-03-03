import pytest
import logging
import json
import os

from indic_transliteration import sanscript

import chandas
from chandas import syllabize

# Remove all handlers associated with the root logger object.

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(asctime)s:%(module)s:%(filename)s:%(lineno)d %(message)s"
)

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), 'data', 'chandasIdTests.json')

test_data = {}
with open(TEST_DATA_PATH) as test_data_file:
    # noinspection PyRedeclaration
    test_data = json.loads(test_data_file.read())
# logging.info(test_data["tests"])


@pytest.mark.parametrize("test_case", [x for x in test_data["tests"] if 'exactMatches' in x] )
def test_svat_id(test_case):
    logging.debug(str(test_case))
    pattern_lines = chandas.to_pattern_lines(test_case["verse"].split("\n"))
    id_result = chandas.svat_identifier.IdentifyFromPatternLines(pattern_lines)
    assert 'exact' in id_result, id_result
    exact_matches = [sanscript.transliterate(metre.lower(), _from=sanscript.IAST, _to=sanscript.DEVANAGARI) for metre in id_result['exact'].keys()]
    assert exact_matches == test_case["exactMatches"], id_result