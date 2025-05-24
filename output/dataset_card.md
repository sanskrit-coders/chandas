
---
language:
- sa
license: cc-by-4.0
tags:
- sanskrit
- poetry
- metrical-poetry
- reinforcement-learning
dataset_info:
  features:
    - name: examples
      sequence: 
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
    - name: tasks
      sequence:
        - name: meter
          dtype: string
        - name: topic
          dtype: string
        - name: meter_pattern
          dtype: string
        - name: difficulty
          dtype: string
        - name: description
          dtype: string
---

# Sanskrit Metrical Poetry Dataset

This dataset contains examples and tasks for Sanskrit metrical poetry composition.
            