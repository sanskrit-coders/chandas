#!/usr/bin/env python3
"""
Script to upload the Sanskrit Metrical Poetry dataset to Hugging Face.
"""

import os
import json
import argparse
import logging
from huggingface_hub import HfApi, create_repo, upload_folder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def prepare_dataset_for_upload(dataset_path, output_dir):
    """
    Prepare the dataset for upload to Hugging Face.

    Args:
        dataset_path: Path to the dataset JSON file
        output_dir: Directory to save the prepared dataset
    """
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Load dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # Create a unified dataset structure for Hugging Face
    # This resolves the schema mismatch issue
    examples = dataset.get("examples", [])
    tasks = dataset.get("tasks", [])

    # Create a unified dataset file
    dataset_path = os.path.join(output_dir, "dataset.json")

    # Transform examples and tasks into a unified format
    unified_data = []

    # Add examples with a type field
    for example in examples:
        item = example.copy()
        item["data_type"] = "example"
        unified_data.append(item)

    # Add tasks with a type field
    for task in tasks:
        item = task.copy()
        item["data_type"] = "task"
        # Ensure all items have the same fields (add empty ones if needed)
        if "text" not in item:
            item["text"] = ""
        if "pattern" not in item and "meter_pattern" in item:
            item["pattern"] = item["meter_pattern"]
            del item["meter_pattern"]
        if "source" not in item:
            item["source"] = "Generated"
        unified_data.append(item)

    # Save unified dataset
    with open(dataset_path, 'w', encoding='utf-8') as f:
        json.dump({"data": unified_data}, f, ensure_ascii=False, indent=2)

    # Create dataset card
    create_dataset_card(output_dir)

    logger.info(f"Dataset prepared for upload in {output_dir}")


def create_dataset_card(output_dir):
    """
    Create a dataset card (README.md) for the Hugging Face dataset.

    Args:
        output_dir: Directory to save the dataset card
    """
    readme_path = os.path.join(output_dir, "README.md")

    # Create dataset card content with YAML metadata
    dataset_card = """
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
  "text": "धर्मो रक्षति रक्षितः\\nसत्यं वदति सर्वदा।\\nज्ञानं ददाति विनयं\\nविद्या ददाति पात्रताम्॥",
  "meter": "अनुष्टुभ्",
  "topic": "ज्ञानम्",
  "source": "Traditional",
  "pattern": "LGGLGGLG\\nLGGLGGLG\\nLGGLGGLG\\nLGGLGGLG",
  "identified_meters": "{'exact': {'अनुष्टुभ्'}, 'partial': set()}",
  "syllable_info": "{'syllables': ['ध', 'र्मो', 'र', 'क्ष', 'ति', 'र', 'क्षि', 'तः', '\\n', 'स', 'त्यं', 'व', 'द', 'ति', 'स', 'र्व', 'दा', '।', '\\n', 'ज्ञा', 'नं', 'द', 'दा', 'ति', 'वि', 'न', 'यं', '\\n', 'वि', 'द्या', 'द', 'दा', 'ति', 'पा', 'त्र', 'ताम्', '॥'], 'weights': ['L', 'G', 'G', 'L', 'G', 'G', 'L', 'G', '\\n', 'L', 'G', 'G', 'L', 'G', 'G', 'L', 'G', '।', '\\n', 'L', 'G', 'G', 'L', 'G', 'G', 'L', 'G', '\\n', 'L', 'G', 'G', 'L', 'G', 'G', 'L', 'G', '॥']}"
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
  howpublished = {\\url{https://github.com/sanskrit-coders/chandas}}
}
```

### Contributions

Thanks to the Sanskrit Coders community for their contributions to this dataset.
"""

    # Write dataset card to file
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(dataset_card)

    logger.info(f"Created dataset card at {readme_path}")


def upload_to_huggingface(dataset_dir, repo_name, token=None):
    """
    Upload the dataset to Hugging Face.

    Args:
        dataset_dir: Directory containing the prepared dataset
        repo_name: Name of the Hugging Face repository
        token: Hugging Face API token
    """
    try:
        # Initialize Hugging Face API
        api = HfApi()

        # Create repository if it doesn't exist
        create_repo(
            repo_id=repo_name,
            repo_type="dataset",
            token=token,
            private=False,
            exist_ok=True
        )

        # Upload dataset
        api.upload_folder(
            folder_path=dataset_dir,
            repo_id=repo_name,
            repo_type="dataset",
            token=token,
            commit_message="Upload Sanskrit Metrical Poetry dataset"
        )

        logger.info(f"Dataset uploaded to https://huggingface.co/datasets/{repo_name}")
        logger.info(f"View your dataset at: https://huggingface.co/datasets/{repo_name}")
        logger.info(
            f"To use this dataset in code: from datasets import load_dataset\ndataset = load_dataset('{repo_name}')")
    except Exception as e:
        logger.error(f"Error uploading dataset to Hugging Face: {e}")
        logger.error(
            f"If you're trying to upload to an organization namespace, make sure you have the right permissions.")
        logger.error(
            f"You can try uploading to your personal namespace instead: --repo-name YOUR_USERNAME/sanskrit-metrical-poetry")


def main():
    """Parse command-line arguments and run the upload process."""
    parser = argparse.ArgumentParser(
        description="Upload Sanskrit Metrical Poetry dataset to Hugging Face")
    parser.add_argument(
        "--dataset-path",
        type=str,
        default="output/sanskrit_metrical_poetry_dataset.json",
        help="Path to the dataset JSON file")
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/huggingface_dataset",
        help="Directory to save the prepared dataset")
    parser.add_argument(
        "--repo-name",
        type=str,
        default="sanskrit-coders/sanskrit-metrical-poetry",
        help="Name of the Hugging Face repository")
    parser.add_argument(
        "--token",
        type=str,
        help="Hugging Face API token")

    args = parser.parse_args()

    # Prepare dataset for upload
    prepare_dataset_for_upload(args.dataset_path, args.output_dir)

    # Upload to Hugging Face
    if args.token:
        upload_to_huggingface(args.output_dir, args.repo_name, args.token)
    else:
        logger.warning("No Hugging Face token provided. Dataset not uploaded.")
        logger.info(f"To upload the dataset, run this script with --token YOUR_HF_TOKEN")
        logger.info(f"You can obtain a token from https://huggingface.co/settings/tokens")


if __name__ == "__main__":
    main()
