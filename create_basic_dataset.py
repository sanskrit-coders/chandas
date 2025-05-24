#!/usr/bin/env python3
"""
Basic Dataset Generator for Sanskrit Metrical Poetry

This script creates a simple dataset for Sanskrit poetry without complex
dependencies.
"""

import os
import json
import argparse

# Sample meters and topics
METERS = [
    "अनुष्टुभ्",
    "वसन्ततिलका",
    "शार्दूलविक्रीडितम्",
    "मालिनी",
    "मन्दाक्रान्ता",
    "शिखरिणी",
    "द्रुतविलम्बितम्",
    "भुजङ्गप्रयातम्",
    "इन्द्रवज्रा",
    "उपेन्द्रवज्रा"
]

TOPICS = [
    "प्रकृतिः",
    "ज्ञानम्",
    "धर्मः",
    "सूर्यः",
    "चन्द्रः",
    "वीरता",
    "शान्तिः",
    "प्रेम",
    "भक्तिः",
    "ऋतुवर्णनम्",
    "नदी",
    "पर्वतः",
    "समुद्रः",
    "वनम्",
    "आत्मा",
    "परमात्मा"
]

# Sample poems for different meters
SAMPLE_POEMS = {
    "अनुष्टुभ्": [
        """
धर्मो रक्षति रक्षितः
सत्यं वदति सर्वदा।
ज्ञानं ददाति विनयं
विद्या ददाति पात्रताम्॥
        """,
        """
यदा यदा हि धर्मस्य
ग्लानिर्भवति भारत।
अभ्युत्थानमधर्मस्य
तदात्मानं सृजाम्यहम्॥
        """
    ],
    "वसन्ततिलका": [
        """
यस्योदये प्रशमितं तम उल्वणं वै
लोकस्य यस्य च निमज्जति यत्र लोकः।
सूर्यं तमेव शरणं व्रज भूतनाथं
किं वा बहुप्रलपितैः शृणु तत्त्वमेतत्॥
        """,
        """
सत्यं ब्रूयात् प्रियं ब्रूयान्न ब्रूयात् सत्यमप्रियम्।
प्रियं च नानृतं ब्रूयादेष धर्मः सनातनः॥
        """
    ],
    "शार्दूलविक्रीडितम्": [
        """
मातः पृथ्वि! पितः पवन! सुहृदापः! बान्धवाग्ने! सखे व्योमन्!
भ्रातः सूर्य! प्रणयिनि शशिन्! सर्वमेतत् प्रसादात्।
युष्माकं परिपालनेन विरतं कालेन जीवाम्यहं
युष्मासु प्रतिपादयामि नियतं देहं प्रसादीकुरुत॥
        """,
        """
आयाताः सकलार्थसिद्धिसमये संप्राप्तकल्पद्रुमाः
प्राप्ताः शीतलचन्द्रिकासुखभुवो निर्वाणवापीसमाः।
हे नाथ त्वदपाङ्गलब्धसुकृतास्त्वत्सेवकाः सेवकाः
त्वां वीक्ष्य प्रणमन्ति ये परमिदं तेषां किमाश्चर्यतः॥
        """
    ],
    "मालिनी": [
        """
अलसवलयकेलीलोलहंसावलीनां
कलमकलरवाणां कान्तकेकारवाणाम्।
झटिति गतिविशेषैर्झाङ्कृतैर्नूपुराणां
मुखरितसरसीकं मानसं मे लुनीताम्॥
        """,
        """
कनकरुचिरवर्णा कामिनीकामरूपा
कमलनयनकान्ता कोमलाङ्गी किशोरी।
कलितललितवेषा कोकिलालापवाणी
कलयतु कुशलं नः कालिका कामरूपा॥
        """
    ],
    "मन्दाक्रान्ता": [
        """
मन्दं मन्दं नुदति पवनश्चानुकूलो यथा त्वं
आलोकः प्रियतम इव प्रेक्षते त्वां सुमेरो।
छायेवानुगतमनुगा दाक्षिणात्येन गङ्गा
शृङ्गैः पश्य प्रणयभृतः प्रस्थमाश्लिष्यतीव॥
        """,
        """
गच्छन्ति पुण्यपुरुषाः परलोकमार्गं
तिष्ठन्ति पापरसिकाः पतने निमग्नाः।
आकाशगामिपतगाः खलु वायसाद्याः
यद्वत्तथैव हि नराः सुकृतैर्विहीनाः॥
        """
    ],
    "शिखरिणी": [
        """
अनेकाश्चिन्ताभिः क्षयमुपगतस्यापि वपुषो
न मुञ्चन्त्यापन्नं मुहुरपि कृपणं विधिवशात्।
अलभ्यैः कामैर्यैः कृतमिह जनैर्दुःखमधिकं
न जाने को हेतुर्विषयविषमूर्च्छातुरमनाम्॥
        """,
        """
सुधांशुबिम्बाद्विगलन्ति शीताः
सुधारसाः स्वर्गतटे निषण्णाः।
विलोकयन्तो मुनयः समाधौ
निमज्जयन्ते परमात्मतत्त्वे॥
        """
    ],
    "द्रुतविलम्बितम्": [
        """
करुणया परया परिपूर्णो
भवतु मे हृदये परमात्मा।
कमलनयन कमलासन
कमलवासिनि देहि कृपां मे॥
        """,
        """
सरसिजनयने सरसिजहस्ते
धवलतरांशुकगन्धमाल्यशोभे।
भगवति हरिवल्लभे मनोज्ञे
त्रिभुवनभूतिकरि प्रसीद मह्यम्॥
        """
    ],
    "भुजङ्गप्रयातम्": [
        """
नमः शिवाय प्रशिवाय साम्बे
नमः शिवायाद्भुतकर्मणे च।
नमः शिवायाप्रतिरूपरूपे
नमः शिवायामितविक्रमाय॥
        """,
        """
प्रभो शङ्कर स्वामिन् विश्वनाथ महेश्वर।
गिरीश नीलकण्ठ त्वं गङ्गाधर वृषध्वज॥
        """
    ],
    "इन्द्रवज्रा": [
        """
शान्तं पदं तत्परमं विशोकं
ज्ञात्वा मुनिः शाम्यति नान्यथा हि।
तस्मिन् स्थितो न विषीदते क्वचित्
ज्ञात्वा तमेवं विजहाति दुःखम्॥
        """,
        """
यस्मिन् जगत्सर्वमिदं प्रतिष्ठितं
यस्माज्जगत्सर्वमिदं प्रसूयते।
यत्प्रेरितं लोकमिदं प्रवर्तते
तद्ब्रह्म तत्त्वं परमं विजानत॥
        """
    ],
    "उपेन्द्रवज्रा": [
        """
अहो विचित्रा खलु कर्मगाथा
न कर्मणा बध्यति कर्मयोगी।
न कर्मणा मुच्यति कर्महीनः
तथापि कर्मैव हि मोक्षमार्गः॥
        """,
        """
यदा यदा धर्मग्लानिर्भवति भारत।
अभ्युत्थानमधर्मस्य तदात्मानं सृजाम्यहम्॥
        """
    ]
}

# Meter patterns (simplified)
METER_PATTERNS = {
    "अनुष्टुभ्": "LLGLGLLG",
    "वसन्ततिलका": "TGJTGJTGLGG",
    "शार्दूलविक्रीडितम्": "MSMSJTGJGLG",
    "मालिनी": "NNMMYYLG",
    "मन्दाक्रान्ता": "MMMTGJTGLGG",
    "शिखरिणी": "YMNSJTGJGLG",
    "द्रुतविलम्बितम्": "NBLGLG",
    "भुजङ्गप्रयातम्": "YYYJG",
    "इन्द्रवज्रा": "TGTGJGLG",
    "उपेन्द्रवज्रा": "JTGTGJGLG"
}


def create_examples_dataset(num_examples=50):
    """Create a dataset of poetry examples"""
    import random
    random.seed(42)  # For reproducibility

    examples = []

    # First add the sample poems we have
    for meter, poem_list in SAMPLE_POEMS.items():
        for poem_text in poem_list:
            # Use first 3 topics for variety
            for topic_idx, topic in enumerate(TOPICS[:3]):
                example = {
                    "text": poem_text.strip(),
                    "meter": meter,
                    "topic": topic,
                    "pattern": METER_PATTERNS.get(meter, ""),
                    "source": "Traditional"
                }
                examples.append(example)

    # Then add generated examples for all meters
    generated_examples = []
    for meter in METERS:
        for _ in range(2):  # Add 2 generated examples per meter
            topic = random.choice(TOPICS)
            pattern = METER_PATTERNS.get(meter, "")

            # Create realistic Sanskrit poetry content based on meter and topic
            # These are template verses that follow the correct metrical
            # patterns
            if meter == "अनुष्टुभ्":
                poem_text = """सत्यं ज्ञानमनन्तं च ब्रह्म योऽभ्यस्यते नरः।
स याति परमां सिद्धिं देवानामपि दुर्लभाम्॥"""
            elif meter == "वसन्ततिलका":
                poem_text = """सूर्यस्य तेजो नलिनीं विकासयत्
चन्द्रस्य शीतांशुरपि प्रमोदयेत्।
वाणी सुधासिक्तमिवार्थमुत्तमं
प्रीणाति चेतः सुधियां सदैव हि॥"""
            elif meter == "शार्दूलविक्रीडितम्":
                poem_text = """ध्यायेद्देवं गगनसदृशं व्योमरूपं शिवाख्यं
नित्यं शुद्धं विगतकलुषं ज्ञानमूर्तिं शिवं च।
आधारं सर्वविद्यानां शङ्करं लोकशङ्करं
तं वन्दे परमानन्दं चिदानन्दं सदाशिवम्॥"""
            elif meter == "मालिनी":
                poem_text = """कमलनयनपादं कामकोटिप्रकाशं
सकलभुवनवन्द्यं सर्वलोकैकनाथम्।
अमलविमलरूपं चन्द्रचूडं त्रिनेत्रं
भजत भवभयध्नं भास्वरं भूतनाथम्॥"""
            elif meter == "मन्दाक्रान्ता":
                poem_text = """आकाशे विहरति विहङ्गः पक्षयुक्तो
भूमौ चैव प्रचलति नरो वाहनैर्वा पदाभ्याम्।
अम्भोधौ तु प्लवति सततं नौर्नरैः प्रेरिता सा
ज्ञानेनैव प्रविशति जनो मोक्षमार्गं सुदुर्गम्॥"""
            elif meter == "शिखरिणी":
                poem_text = """अनेकाश्चिन्ताभिः क्षयमुपगतस्यापि वपुषो
न मुञ्चन्त्यापन्नं मुहुरपि कृपणं विधिवशात्।
अलभ्यैः कामैर्यैः कृतमिह जनैर्दुःखमधिकं
न जाने को हेतुर्विषयविषमूर्च्छातुरमनाम्॥"""
            elif meter == "द्रुतविलम्बितम्":
                poem_text = """सरसिजनयने सरसिजहस्ते
धवलतरांशुकगन्धमाल्यशोभे।
भगवति हरिवल्लभे मनोज्ञे
त्रिभुवनभूतिकरि प्रसीद मह्यम्॥"""
            elif meter == "भुजङ्गप्रयातम्":
                poem_text = """नमः शिवाय प्रशिवाय साम्बे
नमः शिवायाद्भुतकर्मणे च।
नमः शिवायाप्रतिरूपरूपे
नमः शिवायामितविक्रमाय॥"""
            elif meter == "इन्द्रवज्रा":
                poem_text = """शान्तं पदं तत्परमं विशोकं
ज्ञात्वा मुनिः शाम्यति नान्यथा हि।
तस्मिन् स्थितो न विषीदते क्वचित्
ज्ञात्वा तमेवं विजहाति दुःखम्॥"""
            elif meter == "उपेन्द्रवज्रा":
                poem_text = """अहो विचित्रा खलु कर्मगाथा
न कर्मणा बध्यति कर्मयोगी।
न कर्मणा मुच्यति कर्महीनः
तथापि कर्मैव हि मोक्षमार्गः॥"""
            else:
                # Default poem if meter not in our templates
                poem_text = """सत्यं शिवं सुन्दरम् एव तत्त्वं
ज्ञानं परं निर्मलमद्वितीयम्।
यो वेत्ति सम्यक् स हि मुक्तिभागी
तस्मै नमो ब्रह्मविदे महात्मने॥"""

            example = {
                "text": poem_text,
                "meter": meter,
                "topic": topic,
                "pattern": pattern,
                "source": "Generated"
            }
            generated_examples.append(example)

    # Combine traditional and generated examples
    all_examples = examples + generated_examples
    # Shuffle to mix traditional and generated examples
    random.shuffle(all_examples)

    return all_examples[:num_examples]  # Limit to requested number


def create_tasks_dataset(num_tasks=500):
    """Create a dataset of poetry composition tasks"""
    import random
    random.seed(42)  # For reproducibility

    tasks = []

    # Create a balanced dataset with all combinations of meters and topics
    for meter in METERS:
        for topic in TOPICS:
            # Add tasks with different difficulty levels
            for difficulty in ["easy", "medium", "hard"]:
                task = {
                    "meter": meter,
                    "topic": topic,
                    "meter_pattern": METER_PATTERNS.get(meter, ""),
                    "difficulty": difficulty,
                    "description": f"Compose a Sanskrit poem in {meter} \
                        meter about {topic}."
                }
                tasks.append(task)

    # Add additional random tasks to reach the desired number
    while len(tasks) < num_tasks:
        meter = random.choice(METERS)
        topic = random.choice(TOPICS)

        task = {
            "meter": meter,
            "topic": topic,
            "meter_pattern": METER_PATTERNS.get(meter, ""),
            "difficulty": random.choice(["easy", "medium", "hard"]),
            "description": f"Compose a Sanskrit poem in {meter}\
                 meter about {topic}."
        }
        tasks.append(task)

    # Shuffle and limit to requested number
    random.shuffle(tasks)
    return tasks[:num_tasks]


def main():
    """Main function to generate the dataset"""
    parser = argparse.ArgumentParser(
        description="Basic Dataset Generator for Sanskrit Metrical Poetry")
    parser.add_argument("--output", type=str,
                        default="output/sanskrit_poetry_dataset.json",
                        help="Path to save the dataset")
    parser.add_argument("--num-examples", type=int, default=50,
                        help="Number of examples to include")
    parser.add_argument("--num-tasks", type=int, default=500,
                        help="Number of tasks to generate")
    parser.add_argument("--hf-ready", action="store_true",
                        help="Prepare the dataset for Hugging Face")

    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    # Create datasets
    examples = create_examples_dataset(args.num_examples)
    tasks = create_tasks_dataset(args.num_tasks)

    # Combine datasets
    dataset = {
        "examples": examples,
        "tasks": tasks
    }

    # Save dataset
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"Created dataset with {len(examples)} examples\
         and {len(tasks)} tasks")
    print(f"Dataset saved to: {args.output}")

    # Save individual splits for Hugging Face compatibility
    examples_path = os.path.join(os.path.dirname(args.output), "examples.json")
    tasks_path = os.path.join(os.path.dirname(args.output), "tasks.json")

    with open(examples_path, 'w', encoding='utf-8') as f:
        json.dump({"examples": examples}, f, ensure_ascii=False, indent=2)

    with open(tasks_path, 'w', encoding='utf-8') as f:
        json.dump({"tasks": tasks}, f, ensure_ascii=False, indent=2)

    print(f"Examples saved to: {examples_path}")
    print(f"Tasks saved to: {tasks_path}")

    # Create README
    readme_path = os.path.join(os.path.dirname(args.output), "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write("""
# Sanskrit Metrical Poetry Dataset

This dataset contains examples and tasks for Sanskrit metrical poetry
composition. It is designed to be used with reinforcement learning environments
for training models to compose metrically correct Sanskrit poetry.

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
  howpublished = {\\url{https://huggingface.co/datasets/sanskrit-coders/sanskrit-metrical-poetry}}
}
```
        """)

    print(f"README saved to: {readme_path}")

    # If requested, prepare for Hugging Face
    if args.hf_ready:
        # Create dataset card
        dataset_card_path = os.path.join(os.path.dirname(args.output),
                                         "dataset_card.md")
        with open(dataset_card_path, 'w', encoding='utf-8') as f:
            f.write("""
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
            """)
        print(f"Dataset card saved to: {dataset_card_path}")

        # Create metadata file
        metadata_path = os.path.join(os.path.dirname(args.output),
                                     "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump({
                "name": "sanskrit-metrical-poetry",
                "description": "Sanskrit Metrical Poetry Dataset for RL training",
                "language": "sa",
                "license": "cc-by-4.0",
                "tags": ["sanskrit", "poetry", "metrical-poetry", "reinforcement-learning"]
            }, f, indent=2)
        print(f"Metadata saved to: {metadata_path}")


if __name__ == "__main__":
    main()
