"""
Huggingface Dataset Generator for Sanskrit Metrical Poetry

This script generates and uploads a dataset to the Huggingface Hub
for Sanskrit metrical poetry composition.
"""

import os
import json
import logging
import argparse
from typing import Optional

import pandas as pd
from datasets import Dataset, DatasetDict

from rl_env.dataset import generate_dataset
from rl_env.meter_verifier import MeterVerifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample poems for different meters
SAMPLE_POEMS = {
    "अनुष्टुभ्": [
        {
            "text": """
धर्मो रक्षति रक्षितः
सत्यं वदति सर्वदा।
ज्ञानं ददाति विनयं
विद्या ददाति पात्रताम्॥
            """,
            "topic": "ज्ञानम्",
            "source": "Traditional"
        },
        {
            "text": """
यदा यदा हि धर्मस्य
ग्लानिर्भवति भारत।
अभ्युत्थानमधर्मस्य
तदात्मानं सृजाम्यहम्॥
            """,
            "topic": "धर्मः",
            "source": "भगवद्गीता"
        }
    ],
    "वसन्ततिलका": [
        {
            "text": """
यस्योदये प्रशमितं तम उल्वणं वै
लोकस्य यस्य च निमज्जति यत्र लोकः।
सूर्यं तमेव शरणं व्रज भूतनाथं
किं वा बहुप्रलपितैः शृणु तत्त्वमेतत्॥
            """,
            "topic": "सूर्यः",
            "source": "Traditional"
        }
    ],
    "शार्दूलविक्रीडितम्": [
        {
            "text": """
मातः पृथ्वि! पितः पवन! सुहृदापः! बान्धवाग्ने! सखे व्योमन्!
भ्रातः सूर्य! प्रणयिनि शशिन्! सर्वमेतत् प्रसादात्।
युष्माकं परिपालनेन विरतं कालेन जीवाम्यहं
युष्मासु प्रतिपादयामि नियतं देहं प्रसादीकुरुत॥
            """,
            "topic": "प्रकृतिः",
            "source": "Traditional"
        }
    ]
}


def create_examples_dataset(output_path: str, num_examples: int = 100) -> None:
    """
    Create a dataset of poetry examples with their metrical analysis.

    Args:
        output_path: Path to save the dataset
        num_examples: Number of examples to include (will use available examples)
    """
    verifier = MeterVerifier()
    examples = []

    # Process each sample poem
    for meter, poems in SAMPLE_POEMS.items():
        for poem_data in poems:
            poem = poem_data["text"].strip()
            topic = poem_data["topic"]
            source = poem_data["source"]

            # Get pattern from text
            pattern = verifier.get_pattern_from_text(poem)

            # Identify meter
            identified_meters = verifier.identify_meter(poem)

            # Get syllable info
            syllable_info = verifier.get_syllable_info(poem)

            # Create example
            example = {
                "text": poem,
                "meter": meter,
                "topic": topic,
                "source": source,
                "pattern": pattern,
                "identified_meters": identified_meters,
                "syllable_info": syllable_info
            }

            examples.append(example)

    # Save examples to file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"examples": examples}, f, ensure_ascii=False, indent=2)

    logger.info(f"Created examples dataset with {len(examples)} examples at {output_path}")


def create_tasks_dataset(output_path: str, num_tasks: int = 1000) -> None:
    """
    Create a dataset of poetry composition tasks.

    Args:
        output_path: Path to save the dataset
        num_tasks: Number of tasks to generate
    """
    # Generate dataset
    generate_dataset(output_path, num_tasks)
    logger.info(f"Created tasks dataset with {num_tasks} tasks at {output_path}")


def create_huggingface_dataset(examples_path: str, tasks_path: str, output_dir: str) -> Dataset:
    """
    Create a Huggingface dataset from examples and tasks.

    Args:
        examples_path: Path to examples dataset
        tasks_path: Path to tasks dataset
        output_dir: Directory to save the dataset

    Returns:
        Huggingface Dataset
    """
    # Load examples
    with open(examples_path, 'r', encoding='utf-8') as f:
        examples_data = json.load(f)["examples"]

    # Load tasks
    with open(tasks_path, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)["tasks"]

    # Convert to pandas DataFrames
    examples_df = pd.DataFrame(examples_data)
    tasks_df = pd.DataFrame(tasks_data)

    # Create Huggingface Datasets
    examples_dataset = Dataset.from_pandas(examples_df)
    tasks_dataset = Dataset.from_pandas(tasks_df)

    # Create DatasetDict
    dataset_dict = DatasetDict({
        "examples": examples_dataset,
        "tasks": tasks_dataset
    })

    # Save locally
    dataset_dict.save_to_disk(output_dir)
    logger.info(f"Created Huggingface dataset at {output_dir}")

    return dataset_dict


def upload_to_huggingface(dataset_dir: str, repo_name: str, token: Optional[str] = None) -> None:
    """
    Upload a dataset to the Huggingface Hub.

    Args:
        dataset_dir: Directory containing the dataset
        repo_name: Name of the repository on Huggingface
        token: Huggingface API token
    """
    try:
        from datasets import load_from_disk
        from huggingface_hub import HfApi

        # Load the dataset
        dataset = load_from_disk(dataset_dir)

        # Create repository name
        if not repo_name.startswith("sanskrit-coders/"):
            repo_name = f"sanskrit-coders/{repo_name}"

        # Push to hub
        dataset.push_to_hub(
            repo_name,
            token=token,
            private=False,
            commit_message="Upload Sanskrit metrical poetry dataset"
        )

        logger.info(f"Uploaded dataset to Huggingface Hub: {repo_name}")

        # Add dataset card if API token is provided
        if token:
            api = HfApi(token=token)

            # Create dataset card content
            dataset_card = f"""
# Sanskrit Metrical Poetry Dataset

This dataset contains examples and tasks for Sanskrit metrical poetry composition.

## Dataset Structure

The dataset contains two splits:

- `examples`: Examples of Sanskrit poems with their metrical analysis
- `tasks`: Tasks for Sanskrit metrical poetry composition

### Examples

Each example contains:
- `text`: The Sanskrit poem text
- `meter`: The meter (chandas) of the poem
- `topic`: The topic of the poem
- `source`: The source of the poem
- `pattern`: The metrical pattern (sequence of laghu/guru syllables)
- `identified_meters`: Meters identified in the poem
- `syllable_info`: Detailed syllable analysis

### Tasks

Each task contains:
- `meter`: The meter (chandas) to use
- `topic`: The topic to write about
- `meter_info`: Information about the meter (description and pattern)
- `difficulty`: The difficulty level of the task

## Usage

This dataset is designed to be used with the Sanskrit Poetry RL Environment.

```python
from datasets import load_dataset

# Load the dataset
dataset = load_dataset("{repo_name}")

# Get examples
examples = dataset["examples"]

# Get tasks
tasks = dataset["tasks"]
```

## Citation

```
@misc{{sanskrit-metrical-poetry,
  author = {{Sanskrit Coders}},
  title = {{Sanskrit Metrical Poetry Dataset}},
  year = {{2025}},
  publisher = {{Hugging Face}},
  howpublished = {{\\url{{https://huggingface.co/datasets/{repo_name}}}}}
}}
```
            """

            # Write dataset card to file
            with open(os.path.join(dataset_dir, "README.md"), "w", encoding="utf-8") as f:
                f.write(dataset_card)

            # Push dataset card
            api.upload_file(
                path_or_fileobj=os.path.join(dataset_dir, "README.md"),
                path_in_repo="README.md",
                repo_id=repo_name,
                repo_type="dataset",
                commit_message="Add dataset card"
            )

            logger.info(f"Added dataset card to {repo_name}")

    except ImportError:
        logger.error(
            "Failed to import required packages. Please install them with: pip install huggingface_hub")
    except Exception as e:
        logger.error(f"Failed to upload dataset to Huggingface Hub: {e}")


def main():
    """Parse command-line arguments and run the appropriate command."""
    parser = argparse.ArgumentParser(
        description="Huggingface Dataset Generator for Sanskrit Metrical Poetry")
    parser.add_argument(
        "--examples-output",
        type=str,
        default="output/examples_dataset.json",
        help="Path to save examples dataset")
    parser.add_argument(
        "--tasks-output",
        type=str,
        default="output/tasks_dataset.json",
        help="Path to save tasks dataset")
    parser.add_argument("--hf-output", type=str, default="output/hf_dataset",
                        help="Directory to save Huggingface dataset")
    parser.add_argument("--num-examples", type=int, default=100,
                        help="Number of examples to include")
    parser.add_argument("--num-tasks", type=int, default=1000, help="Number of tasks to generate")
    parser.add_argument("--upload", action="store_true", help="Upload dataset to Huggingface Hub")
    parser.add_argument(
        "--repo-name",
        type=str,
        default="sanskrit-metrical-poetry",
        help="Repository name on Huggingface")
    parser.add_argument("--token", type=str, help="Huggingface API token")

    args = parser.parse_args()

    # Create output directories
    os.makedirs(os.path.dirname(args.examples_output), exist_ok=True)
    os.makedirs(os.path.dirname(args.tasks_output), exist_ok=True)
    os.makedirs(args.hf_output, exist_ok=True)

    # Create datasets
    create_examples_dataset(args.examples_output, args.num_examples)
    create_tasks_dataset(args.tasks_output, args.num_tasks)

    # Create Huggingface dataset
    dataset = create_huggingface_dataset(args.examples_output, args.tasks_output, args.hf_output)

    # Upload to Huggingface Hub if requested
    if args.upload:
        upload_to_huggingface(args.hf_output, args.repo_name, args.token)


if __name__ == "__main__":
    main()
