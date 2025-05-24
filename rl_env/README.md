# Sanskrit Metrical Poetry RL Environment

This package provides a reinforcement learning environment for training models to compose Sanskrit poetry that adheres to specific metrical patterns (chandas).

## Overview

Sanskrit poetry is metrical, with each meter (chandas) having specific syllabic constraints. Large Language Models (LLMs) often struggle to correctly follow these metrical patterns. This environment helps train models to generate metrically correct Sanskrit poetry by providing:

1. A meter verifier that checks if text adheres to specific metrical patterns
2. An RL environment with states, actions, and rewards
3. An LLM-based grader to evaluate semantic quality and prevent reward hacking
4. A dataset generator for poetry composition tasks
5. A trainer to facilitate model training
6. A simple RL algorithm implementation for demonstration

## Components

### Meter Verifier (`meter_verifier.py`)

The meter verifier uses the `chandas` package to analyze Sanskrit text and verify if it adheres to specific metrical patterns. It provides:

- Conversion of text to metrical patterns (sequences of laghu/guru syllables)
- Meter identification
- Detailed syllable analysis

### Environment (`environment.py`)

The RL environment provides:

- State space: Current poetry composition task (meter, topic)
- Action space: Generated Sanskrit text
- Reward function: Based on metrical correctness and semantic relevance
- Rendering: Visualization of the current state

### Scoring System

The scoring system evaluates generated Sanskrit poems based on multiple criteria:

#### Meter Correctness (Primary Score)
- **1.0 points**: Perfect match to the specified meter
- **0.5 points**: Partial match (some metrical patterns match)
- **0.1 points**: Basic Sanskrit text that doesn't match the meter
- **0.0 points**: Invalid Sanskrit text or errors in processing

#### Error Handling
- Poems that cause syllabization errors receive a score of 0.0
- The system continues training despite errors, allowing for robust learning

#### Training Statistics
- **Average Reward**: Mean reward across all episodes
- **Episode Length**: Number of attempts before finding a correct poem or reaching max steps
- **Best Poems**: Collection of highest-scoring poems for each meter/topic combination

The scoring system is designed to provide a clear gradient for learning, with the highest rewards reserved for poems that perfectly adhere to the specified metrical patterns while maintaining semantic coherence with the given topic.

### Dataset (`dataset.py`)

The dataset module manages poetry composition tasks, including:

- Loading tasks from JSON files
- Providing task selection mechanisms
- Supporting different difficulty levels
- A default dataset with common meters and topics
- Task sampling and filtering
- Dataset generation and saving

### RL Algorithm (`run_rl_algorithm.py`)

A simple reinforcement learning algorithm implementation that demonstrates how to interact with the environment:

- Loads examples from the dataset
- Implements multiple poem generation strategies
- Tracks training statistics and best-performing poems
- Provides detailed logging of the training process

### LLM Grader (`llm_grader.py`)

The LLM grader evaluates the semantic quality of generated poetry to prevent reward hacking. It provides:

- Evaluation of topic adherence, semantic coherence, poetic quality, and cultural authenticity
- Semantic reward calculation

### Trainer (`trainer.py`)

The trainer integrates all components and provides methods to:

- Train models using the RL environment
- Evaluate model performance
- Generate and save training data

## Usage

### Basic Example

```python
from rl_env.environment import SanskritPoetryEnv
from rl_env.meter_verifier import MeterVerifier
from rl_env.llm_grader import LLMGrader

# Create environment
env = SanskritPoetryEnv()

# Reset environment to get initial state
state = env.reset()
print(f"Task: Compose a poem in {state['task']['meter']} meter about {state['task']['topic']}")

# Generate a poem (replace with your model)
poem = "..."

# Take a step in the environment
next_state, reward, done, info = env.step(poem)
print(f"Reward: {reward}")
print(f"Is correct meter: {info['is_correct']}")

# Render the environment to see details
env.render()
```

### Using the Trainer

```python
from rl_env.trainer import SanskritPoetryTrainer

# Define your model generator function
def my_model_generator(prompt):
    # Use your model to generate a poem
    return "..."

# Create trainer
trainer = SanskritPoetryTrainer(
    model_generator=my_model_generator,
    output_dir="output"
)

# Train for 100 episodes
stats = trainer.train(num_episodes=100)
print(f"Training stats: {stats}")

# Generate training data
examples = trainer.generate_training_data(num_examples=100, output_file="training_data.json")
```

## Running the Example

To run the example script:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the example
python -m rl_env.example
```

## Extending the Environment

### Adding New Meters

To add new meters, update the `PoetryDataset._create_default_dataset` method in `dataset.py`.

### Customizing Rewards

To customize the reward function, modify the `_calculate_reward` method in `environment.py` and the `calculate_semantic_reward` method in `llm_grader.py`.

### Using Different LLMs

To use a different LLM for grading, implement the `_call_llm_api` method in `llm_grader.py`.

## Requirements

- Python 3.6+
- chandas package
- PyICU
- unicodecsv
- indic_transliteration
