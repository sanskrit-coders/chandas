
---
language:
- sa
license: cc-by-sa-4.0
tags:
- sanskrit
- poetry
- meter
dataset_info:
  features:
    - name: text
      dtype: string
    - name: meter
      dtype: string
    - name: topic
      dtype: string
    - name: pattern
      dtype: string
    - name: source
      dtype: string
    - name: data_type
      dtype: string
---

# Sanskrit Metrical Poetry Dataset

This dataset contains examples and tasks for Sanskrit metrical poetry composition, designed to train models to generate metrically correct Sanskrit poetry.

## Dataset Description

### Dataset Summary

The Sanskrit Metrical Poetry dataset is designed for training models to compose Sanskrit poetry that adheres to specific metrical patterns (chandas). It contains examples of Sanskrit poems with their metrical analysis and tasks for poetry composition.

### Languages

The dataset is in Sanskrit (sa).

## Dataset Structure

The dataset contains two main components:

### Examples

Examples of Sanskrit poems with their metrical analysis:

```json
{
  "text": "धर्मो रक्षति रक्षितः\nसत्यं वदति सर्वदा।\nज्ञानं ददाति विनयं\nविद्या ददाति पात्रताम्॥",
  "meter": "अनुष्टुभ्",
  "topic": "ज्ञानम्",
  "source": "Traditional",
  "pattern": "LGGLGGLG\nLGGLGGLG\nLGGLGGLG\nLGGLGGLG",
  "identified_meters": "{'exact': {'अनुष्टुभ्'}, 'partial': set()}",
  "syllable_info": "{'syllables': ['ध', 'र्मो', 'र', 'क्ष', 'ति', 'र', 'क्षि', 'तः', '\n', 'स', 'त्यं', 'व', 'द', 'ति', 'स', 'र्व', 'दा', '।', '\n', 'ज्ञा', 'नं', 'द', 'दा', 'ति', 'वि', 'न', 'यं', '\n', 'वि', 'द्या', 'द', 'दा', 'ति', 'पा', 'त्र', 'ताम्', '॥'], 'weights': ['L', 'G', 'G', 'L', 'G', 'G', 'L', 'G', '\n', 'L', 'G', 'G', 'L', 'G', 'G', 'L', 'G', '।', '\n', 'L', 'G', 'G', 'L', 'G', 'G', 'L', 'G', '\n', 'L', 'G', 'G', 'L', 'G', 'G', 'L', 'G', '॥']}"
}
```

### Tasks

Tasks for Sanskrit metrical poetry composition:

```json
{
  "meter": "अनुष्टुभ्",
  "topic": "ज्ञानम्",
  "meter_info": {
    "description": "अनुष्टुभ् (Anuṣṭubh) is a common meter with 8 syllables per quarter (pāda).",
    "pattern": "LGGLGGLG"
  },
  "difficulty": "medium"
}
```

## Dataset Creation

### Source Data

The examples are sourced from traditional Sanskrit literature and poetry.

### Annotations

The dataset includes metrical analysis of each poem, including:
- Meter identification
- Syllable weights (laghu/guru)
- Pattern representation

## Additional Information

### Licensing Information

This dataset is released under the CC BY-SA 4.0 license.

### Citation Information

```
@misc{sanskrit-metrical-poetry,
  author = {Sanskrit Coders},
  title = {Sanskrit Metrical Poetry Dataset},
  year = {2025},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/sanskrit-coders/chandas}}
}
```

### Contributions

Thanks to the Sanskrit Coders community for their contributions to this dataset.
