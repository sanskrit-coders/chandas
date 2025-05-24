
# Sanskrit Metrical Poetry Dataset

This dataset contains examples and tasks for Sanskrit metrical poetry composition. It is designed to be used with reinforcement learning environments for training models to compose metrically correct Sanskrit poetry.

## Dataset Structure

The dataset contains two splits:

- `examples`: Examples of Sanskrit poems with their metrical analysis
- `tasks`: Tasks for Sanskrit metrical poetry composition

### Examples

Each example contains:
- `text`: The Sanskrit poem text
- `meter`: The meter (chandas) of the poem
- `topic`: The topic of the poem
- `pattern`: The metrical pattern (sequence of laghu/guru syllables)
- `source`: The source of the poem (Traditional or Synthetic)

### Tasks

Each task contains:
- `meter`: The meter (chandas) to use
- `topic`: The topic to write about
- `meter_pattern`: The pattern of the meter
- `difficulty`: The difficulty level of the task (easy, medium, hard)
- `description`: A description of the task

## Meter Patterns

The meter patterns use the following notation:
- L: Laghu (light syllable)
- G: Guru (heavy syllable)
- T: Ta-gana (guru-guru-guru)
- J: Ja-gana (laghu-guru-guru)
- M: Ma-gana (guru-guru-laghu)
- N: Na-gana (guru-laghu-laghu)
- Y: Ya-gana (laghu-guru-laghu)
- S: Sa-gana (laghu-laghu-guru)
- B: Bha-gana (guru-laghu-guru)

## Usage

This dataset is designed to be used with the Sanskrit Poetry RL Environment.

```python
import json

# Load the dataset
with open('sanskrit_poetry_dataset.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

# Access examples
examples = dataset["examples"]

# Access tasks
tasks = dataset["tasks"]
```

## Citation

```
@misc{sanskrit-metrical-poetry,
  author = {Sanskrit Coders},
  title = {Sanskrit Metrical Poetry Dataset},
  year = {2025},
  publisher = {Hugging Face},
  howpublished = {\url{https://huggingface.co/datasets/sanskrit-coders/sanskrit-metrical-poetry}}
}
```
        