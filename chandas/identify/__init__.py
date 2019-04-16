import logging

from chandas import syllabize
from chandas.identify import pattern


def to_pattern_lines(input_lines):
    logging.info('Got input:\n%s', input_lines)
    pattern_lines = ["".join(syllabize.to_weight_list(line)) for line in input_lines]
    return pattern_lines


