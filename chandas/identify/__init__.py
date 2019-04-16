import logging

from chandas import syllabize, metrical_data
from chandas.identify import pattern

metrical_data.initialize_data()
identifier = pattern.Identifier(metrical_data=metrical_data)

def to_pattern_lines(input_lines):
    logging.info('Got input:\n%s', input_lines)
    pattern_lines = ["".join(syllabize.to_weight_list(line)) for line in input_lines]
    return pattern_lines


