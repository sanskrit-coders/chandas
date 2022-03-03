from chandas import syllabize
from chandas.svat.data import metrical_data
from chandas.svat.identify import identifier

metrical_data.InitializeData()
svat_identifier = identifier.Identifier(metrical_data=metrical_data)

def to_pattern_lines(input_lines):
  pattern_lines = ["".join(syllabize.to_weight_list(line)) for line in input_lines]
  return pattern_lines
