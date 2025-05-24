#!/usr/bin/env python3
"""
Example of running a reinforcement learning algorithm with the Sanskrit Poetry
RL Environment.

This script demonstrates how to use the RL environment with a simple algorithm
for composing metrically correct Sanskrit poetry.
"""

import json
import logging
import os
import random
import time
from typing import Any, Dict, List

from rl_env.environment import SanskritPoetryEnv
from rl_env.meter_verifier import MeterVerifier

# Simple dataset class to replace the HF dataset dependency


class SimplePoetryDataset:
    """A simple dataset class for poetry tasks and examples."""

    def __init__(self, dataset_path=None):
        """Initialize the dataset."""
        self.dataset_path = dataset_path
        self.tasks = []
        self.examples = []

        if dataset_path and os.path.exists(dataset_path):
            self._load_data()

    def _load_data(self):
        """Load data from JSON file."""
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = data.get('tasks', [])
                self.examples = data.get('examples', [])
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")

    def sample_task(self):
        """Sample a random task from the dataset."""
        if not self.tasks:
            # Default task if no tasks are available
            return {
                'meter': random.choice(["अनुष्टुभ्", "वसन्ततिलका"]),
                'topic': random.choice(["प्रकृतिः", "ज्ञानम्"]),
                'difficulty': 'medium'
            }
        return random.choice(self.tasks)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set to DEBUG level for more detailed logs
logger.setLevel(logging.DEBUG)

# Sample poems for different meters (for demonstration)
SAMPLE_POEMS = {
    "अनुष्टुभ्": """
यदा यदा हि धर्मस्य
ग्लानिर्भवति भारत।
अभ्युत्थानमधर्मस्य
तदात्मानं सृजाम्यहम्॥
""".strip(),
    "वसन्ततिलका": """
यस्योदये प्रशमितं तम उल्वणं वै
लोकस्य यस्य च निमज्जति यत्र लोकः।
सूर्यं तमेव शरणं व्रज भूतनाथं
किं वा बहुप्रलपितैः शृणु तत्त्वमेतत्॥
""".strip(),
    "शार्दूलविक्रीडितम्": """
मातः पृथ्वि! पितः पवन! सुहृदापः! बान्धवाग्ने! सखे व्योमन्!
भ्रातः सूर्य! प्रणयिनि शशिन्! सर्वमेतत् प्रसादात्।
युष्माकं परिपालनेन विरतं कालेन जीवाम्यहं
युष्मासु प्रतिपादयामि नियतं देहं प्रसादीकुरुत॥
""".strip()
}


class SimpleRLAlgorithm:
    """
    A simple RL algorithm for Sanskrit poetry composition.

    This is a basic implementation that demonstrates how to interact with the
    environment. In a real scenario, you would use a more sophisticated
    algorithm like PPO, A2C, or DQN.
    """

    def __init__(self, env: SanskritPoetryEnv, dataset_path: str = None, max_steps: int = 10):
        """
        Initialize the algorithm.

        Args:
            env: The Sanskrit poetry RL environment
            dataset_path: Path to the dataset for learning from examples
            max_steps: Maximum number of steps per episode
        """
        self.env = env
        self.verifier = MeterVerifier()
        self.dataset_path = dataset_path
        self.dataset = SimplePoetryDataset(dataset_path)  # For tasks
        self.examples = {}
        self.max_steps = max_steps

        # Load examples from dataset
        if dataset_path:
            self._load_examples()

    def _load_examples(self):
        """Load examples from the dataset JSON file."""
        try:
            # Load the dataset file directly
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Access the 'examples' key from the loaded JSON
                if 'examples' in data:
                    for example in data['examples']:
                        meter = example.get("meter")
                        if meter not in self.examples:
                            self.examples[meter] = []
                        self.examples[meter].append(example)
                    logger.info(
                        f"Successfully loaded {len(data['examples'])} examples")
                else:
                    logger.warning("No 'examples' found in the dataset file.")
        except FileNotFoundError:
            logger.error(f"Dataset file not found: {self.dataset_path}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in dataset file: {self.dataset_path}")
        except Exception as e:
            logger.error(f"Error loading examples from dataset: {e}")

    def select_action(self, state: Dict[str, Any]) -> str:
        """
        Select an action (compose a poem) based on the current state.

        Args:
            state: Current state of the environment

        Returns:
            The composed poem as a string
        """
        meter = state["task"]["meter"]
        topic = state["task"]["topic"]
        meter_pattern = state["task"].get("meter_pattern", "")
        difficulty = state["task"].get("difficulty", "medium")

        logger.info(f"Composing a poem in {meter} meter about {topic}")
        logger.info(f"Pattern: {meter_pattern}, Difficulty: {difficulty}")

        # Strategy 1: Use an example from the dataset if available but modify it
        if meter in self.examples and self.examples[meter]:
            # Find examples with matching meter
            matching_examples = self.examples[meter]

            # Select a random example
            example = random.choice(matching_examples)
            base_poem = example["text"]

            # Strategy 1a: For 20% of the time, try to generate a new poem
            if random.random() < 0.2:
                return self._generate_new_poem(meter, topic, meter_pattern)

            # Strategy 1b: Modify the example slightly to create a new poem
            return self._modify_existing_poem(base_poem, topic)

        # Strategy 2: Use a sample poem if available
        if meter in SAMPLE_POEMS:
            base_poem = SAMPLE_POEMS[meter]
            return self._modify_existing_poem(base_poem, topic)

        # Strategy 3: Generate a simple placeholder poem
        return self._generate_new_poem(meter, topic, meter_pattern)

    def _modify_existing_poem(self, poem: str, topic: str) -> str:
        """
        Modify an existing poem to create a new one.

        Args:
            poem: The base poem to modify
            topic: The topic to incorporate

        Returns:
            A modified poem
        """
        # Split the poem into lines
        lines = poem.strip().split('\n')

        # Randomly select lines to modify (between 1-2 lines)
        num_lines_to_modify = min(len(lines), random.randint(1, 2))
        lines_to_modify = random.sample(range(len(lines)), num_lines_to_modify)

        # Sanskrit characters for replacement
        sanskrit_chars = (
            "अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"
        )

        for idx in lines_to_modify:
            # Simple modification: replace a few characters
            if len(lines[idx]) > 10:
                # Replace a random character in the middle of the line
                pos = random.randint(5, len(lines[idx]) - 5)
                replacement_char = random.choice(sanskrit_chars)
                lines[idx] = lines[idx][:pos] + replacement_char + lines[idx][pos + 1:]

        return '\n'.join(lines)

    def _generate_new_poem(self, meter: str, topic: str, pattern: str) -> str:
        """
        Generate a new poem based on meter and topic.

        Args:
            meter: The meter to use
            topic: The topic to incorporate
            pattern: The metrical pattern

        Returns:
            A new poem
        """
        # For now, this is a simple placeholder generator
        # In a real implementation, this would use more sophisticated NLP techniques

        # Common Sanskrit words for different topics
        topic_words = {
            "प्रकृतिः": ["वनम्", "नदी", "पर्वतः", "सूर्यः", "चन्द्रः", "आकाशः"],
            "धर्मः": ["सत्यम्", "अहिंसा", "दया", "क्षमा", "शान्तिः", "ज्ञानम्"],
            "ज्ञानम्": ["विद्या", "बुद्धिः", "मेधा", "प्रज्ञा", "धीः", "चेतना"],
            "भक्तिः": ["देवः", "ईश्वरः", "पूजा", "आराधना", "स्तुतिः", "प्रार्थना"],
            "प्रेम": ["स्नेहः", "अनुरागः", "प्रीतिः", "वात्सल्यम्", "मैत्री", "आसक्तिः"],
            "वीरता": ["शौर्यम्", "पराक्रमः", "साहसम्", "धैर्यम्", "बलम्", "तेजः"]
        }

        # Default words if topic not found
        default_words = ["जगत्", "लोकः", "जीवनम्", "कर्म", "धर्मः", "मोक्षः"]

        # Get words for the topic or use defaults
        words = topic_words.get(topic, default_words)

        # Generate poem based on meter
        if meter == "अनुष्टुभ्":
            return self._generate_anustubh(words)
        elif meter == "वसन्ततिलका":
            return self._generate_vasantatilaka(words)
        elif meter == "शार्दूलविक्रीडितम्":
            return self._generate_shardulvikridita(words)
        else:
            # Generic template for other meters
            return self._generate_generic_poem(meter, words)

    def _generate_anustubh(self, words: List[str]) -> str:
        """
        Generate a poem in Anustubh meter.
        """
        lines = [
            f"{random.choice(words)} {random.choice(words)} च {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}।",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}॥"
        ]
        return '\n'.join(lines)

    def _generate_vasantatilaka(self, words: List[str]) -> str:
        """
        Generate a poem in Vasantatilaka meter.
        """
        lines = [
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}।",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}॥"]
        return '\n'.join(lines)

    def _generate_shardulvikridita(self, words: List[str]) -> str:
        """
        Generate a poem in Shardulvikridita meter.
        """
        lines = [
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}।",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}॥"]
        return '\n'.join(lines)

    def _generate_generic_poem(self, meter: str, words: List[str]) -> str:
        """
        Generate a generic poem for any meter.
        """
        lines = [
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}।",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}॥"
        ]
        return '\n'.join(lines)

    def _modify_existing_poem(self, poem: str, topic: str) -> str:
        """
        Modify an existing poem to create a new one.

        Args:
            poem: The base poem to modify
            topic: The topic to incorporate

        Returns:
            A modified poem
        """
        # Split the poem into lines
        lines = poem.strip().split('\n')

        # Randomly select lines to modify (between 1-2 lines)
        num_lines_to_modify = min(len(lines), random.randint(1, 2))
        lines_to_modify = random.sample(range(len(lines)), num_lines_to_modify)

        # Sanskrit characters for replacement
        sanskrit_chars = (
            "अआइईउऊऋएऐओऔकखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह"
        )

        for idx in lines_to_modify:
            # Simple modification: replace a few characters
            if len(lines[idx]) > 10:
                # Replace a random character in the middle of the line
                pos = random.randint(5, len(lines[idx]) - 5)
                replacement_char = random.choice(sanskrit_chars)
                lines[idx] = lines[idx][:pos] + replacement_char + lines[idx][pos + 1:]

        return '\n'.join(lines)

    def _generate_new_poem(self, meter: str, topic: str, pattern: str) -> str:
        """
        Generate a new poem based on meter and topic.

        Args:
            meter: The meter to use
            topic: The topic to incorporate
            pattern: The metrical pattern

        Returns:
            A new poem
        """
        # For now, this is a simple placeholder generator
        # In a real implementation, this would use more sophisticated NLP techniques

        # Common Sanskrit words for different topics
        topic_words = {
            "प्रकृतिः": ["वनम्", "नदी", "पर्वतः", "सूर्यः", "चन्द्रः", "आकाशः"],
            "धर्मः": ["सत्यम्", "अहिंसा", "दया", "क्षमा", "शान्तिः", "ज्ञानम्"],
            "ज्ञानम्": ["विद्या", "बुद्धिः", "मेधा", "प्रज्ञा", "धीः", "चेतना"],
            "भक्तिः": ["देवः", "ईश्वरः", "पूजा", "आराधना", "स्तुतिः", "प्रार्थना"],
            "प्रेम": ["स्नेहः", "अनुरागः", "प्रीतिः", "वात्सल्यम्", "मैत्री", "आसक्तिः"],
            "वीरता": ["शौर्यम्", "पराक्रमः", "साहसम्", "धैर्यम्", "बलम्", "तेजः"]
        }

        # Default words if topic not found
        default_words = ["जगत्", "लोकः", "जीवनम्", "कर्म", "धर्मः", "मोक्षः"]

        # Get words for the topic or use defaults
        words = topic_words.get(topic, default_words)

        # Generate poem based on meter
        if meter == "अनुष्टुभ्":
            return self._generate_anustubh(words)
        elif meter == "वसन्ततिलका":
            return self._generate_vasantatilaka(words)
        elif meter == "शार्दूलविक्रीडितम्":
            return self._generate_shardulvikridita(words)
        else:
            # Generic template for other meters
            return self._generate_generic_poem(meter, words)

    def _generate_anustubh(self, words: List[str]) -> str:
        """
        Generate a poem in Anustubh meter.
        """
        lines = [
            f"{random.choice(words)} {random.choice(words)} च {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}।",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}॥"
        ]
        return '\n'.join(lines)

    def _generate_vasantatilaka(self, words: List[str]) -> str:
        """
        Generate a poem in Vasantatilaka meter.
        """
        lines = [
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}।",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}॥"]
        return '\n'.join(lines)

    def _generate_shardulvikridita(self, words: List[str]) -> str:
        """
        Generate a poem in Shardulvikridita meter.
        """
        lines = [
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}।",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)} {random.choice(words)}॥"]
        return '\n'.join(lines)

    def _generate_generic_poem(self, meter: str, words: List[str]) -> str:
        """
        Generate a generic poem for any meter.
        """
        lines = [
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}।",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}",
            f"{random.choice(words)} {random.choice(words)} {random.choice(words)}॥"
        ]
        return '\n'.join(lines)

    def train(self, num_episodes=10):
        """Train the algorithm for a specified number of episodes."""
        total_reward = 0
        episode_rewards = []
        episode_lengths = []
        generated_poems = []
        start_time = time.time()

        for episode in range(num_episodes):
            logger.info(f"Episode {episode+1}/{num_episodes}")

            # Reset environment
            state = self.env.reset()
            meter = state['task']['meter']
            topic = state['task']['topic']
            pattern = state['task'].get('pattern', '')
            difficulty = state['task'].get('difficulty', 'medium')
            logger.info(f"Task: Compose a poem in {meter} meter about {topic}")

            done = False
            episode_reward = 0
            episode_length = 0
            best_poem = ""
            best_reward = -float('inf')

            while not done and episode_length < self.max_steps:
                logger.info(f"Composing a poem in {meter} meter about {topic}")
                logger.info(f"Pattern: {pattern}, Difficulty: {difficulty}")

                # Select action
                action = self.select_action(state)
                logger.debug(f"Selected poem:\n{action}")

                try:
                    # Take step in environment
                    next_state, reward, done, info = self.env.step(action)

                    # Update statistics
                    episode_reward += reward
                    episode_length += 1

                    # Track best poem in this episode
                    if reward > best_reward:
                        best_reward = reward
                        best_poem = action

                    # Log step information
                    logger.info(f"Step {episode_length}, Reward: {reward}")
                    logger.info(f"Meter correct: {info.get('is_correct', False)}")
                    logger.info(f"Identified: {info.get('identified_meters', {})}")

                    # Provide feedback for learning
                    if info.get('is_correct', False):
                        logger.info(" Poem follows the correct meter!")
                        if reward > best_reward:
                            best_poem = action
                            best_reward = reward
                    else:
                        logger.info(" Poem does not follow the correct meter")

                    state = next_state

                    if done:
                        break

                except Exception as e:
                    # Handle errors gracefully
                    logger.warning(f"Error processing poem: {e}")
                    logger.warning(f"Problematic poem:\n{action}")

                    # Assign a low reward for poems that cause errors
                    reward = 0.0
                    episode_length += 1
                    episode_reward += reward
                    logger.info(
                        f"Step {episode_length}, Reward: {reward} (due to error)")

                    # Continue with the next attempt
                    continue

            # Log episode information
            logger.info(f"Episode {episode+1} finished with reward {episode_reward}")
            logger.info(f"Episode length: {episode_length}")

            # Save the best poem from this episode
            if best_poem:
                generated_poems.append({
                    "meter": meter,
                    "topic": topic,
                    "text": best_poem,
                    "reward": best_reward
                })

            # Update statistics
            total_reward += episode_reward
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)

        # Calculate statistics
        avg_reward = total_reward / num_episodes if num_episodes > 0 else 0
        avg_length = sum(episode_lengths) / num_episodes if num_episodes > 0 else 0

        # Calculate training time
        training_time = time.time() - start_time

        # Return statistics
        return {
            "average_reward": avg_reward,
            "average_episode_length": avg_length,
            "episode_rewards": episode_rewards,
            "episode_lengths": episode_lengths,
            "generated_poems": generated_poems[:5],  # Store up to 5 best poems
            "training_time": training_time
        }


def main():
    """Run the RL algorithm."""
    logger.info("Starting RL algorithm for Sanskrit poetry composition")

    # Create environment
    logger.info("Creating Sanskrit Poetry RL Environment")
    env = SanskritPoetryEnv()

    # Create algorithm
    dataset_path = "output/sanskrit_poetry_dataset.json"
    logger.info(f"Loading dataset from: {dataset_path}")
    algorithm = SimpleRLAlgorithm(env, dataset_path)

    # Log loaded examples
    example_count = sum(len(examples) for examples in algorithm.examples.values())
    logger.info(f"Loaded {example_count} examples for {len(algorithm.examples)} meters")
    for meter, examples in algorithm.examples.items():
        logger.info(f"  - {meter}: {len(examples)} examples")

    # Train algorithm
    logger.info("Starting training for 5 episodes")
    stats = algorithm.train(num_episodes=5)

    # Print statistics
    logger.info("Training completed!")
    logger.info(f"Average reward: {stats['average_reward']:.4f}")
    logger.info(f"Average episode length: {stats['average_episode_length']:.2f}")
    logger.info(f"Episode rewards: {stats['episode_rewards']}")
    logger.info(f"Training time: {stats['training_time']:.2f} seconds")

    # Print best generated poems
    if stats['generated_poems']:
        logger.info("\nBest generated poems:")
        for i, poem_data in enumerate(stats['generated_poems'], 1):
            logger.info(f"\nPoem {i}:")
            logger.info(f"Meter: {poem_data['meter']}")
            logger.info(f"Topic: {poem_data['topic']}")
            logger.info(f"Reward: {poem_data['reward']:.4f}")
            logger.info("Text:\n" + poem_data['text'])

    # Save statistics
    os.makedirs("output", exist_ok=True)
    with open("output/rl_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    logger.info("Statistics saved to output/rl_stats.json")


if __name__ == "__main__":
    main()
