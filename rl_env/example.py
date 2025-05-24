"""
Example usage of the Sanskrit Poetry RL Environment

This script demonstrates how to use the RL environment for Sanskrit metrical
poetry composition with a simple example.
"""

import os
import logging
import json


from rl_env.environment import SanskritPoetryEnv
from rl_env.meter_verifier import MeterVerifier
from rl_env.dataset import PoetryDataset, generate_dataset
from rl_env.llm_grader import LLMGrader
from rl_env.trainer import SanskritPoetryTrainer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Sample poems for testing
SAMPLE_POEMS = {
    "अनुष्टुभ्": """
धर्मो रक्षति रक्षितः
सत्यं वदति सर्वदा।
ज्ञानं ददाति विनयं
विद्या ददाति पात्रताम्॥
    """,
    "वसन्ततिलका": """
यस्योदये प्रशमितं तम उल्वणं वै
लोकस्य यस्य च निमज्जति यत्र लोकः।
सूर्यं तमेव शरणं व्रज भूतनाथं
किं वा बहुप्रलपितैः शृणु तत्त्वमेतत्॥
    """,
    "शार्दूलविक्रीडितम्": """
मातः पृथ्वि! पितः पवन! सुहृदापः! बान्धवाग्ने! सखे व्योमन्!
भ्रातः सूर्य! प्रणयिनि शशिन्! सर्वमेतत् प्रसादात्।
युष्माकं परिपालनेन विरतं कालेन जीवाम्यहं
युष्मासु प्रतिपादयामि नियतं देहं प्रसादीकुरुत॥
    """
}


def mock_model_generator(prompt: str) -> str:
    """
    A mock model generator that returns a sample poem based on the prompt.

    Args:
        prompt: The prompt for poem generation

    Returns:
        A Sanskrit poem
    """
    # Extract meter from prompt
    for meter in SAMPLE_POEMS:
        if meter in prompt:
            return SAMPLE_POEMS[meter]

    # Default to Anushtubh if no meter is found
    return SAMPLE_POEMS["अनुष्टुभ्"]


def test_meter_verifier():
    """Test the meter verifier component."""
    logger.info("Testing Meter Verifier...")

    verifier = MeterVerifier()

    for meter, poem in SAMPLE_POEMS.items():
        logger.info(f"Testing meter: {meter}")

        # Get pattern from text
        pattern = verifier.get_pattern_from_text(poem)
        logger.info(f"Pattern: {pattern}")

        # Identify meter
        identified_meters = verifier.identify_meter(poem)
        logger.info(f"Identified meters: {identified_meters}")

        # Verify meter
        is_correct, details = verifier.verify_meter(poem, meter)
        logger.info(f"Is correct meter: {is_correct}")
        logger.info(f"Details: {json.dumps(details, ensure_ascii=False, indent=2)}")

        # Get syllable info
        syllable_info = verifier.get_syllable_info(poem)
        logger.info(f"Syllable info: {json.dumps(syllable_info, ensure_ascii=False, indent=2)}")

        logger.info("-" * 50)


def test_environment():
    """Test the RL environment."""
    logger.info("Testing RL Environment...")

    # Create environment
    env = SanskritPoetryEnv()

    # Reset environment
    state = env.reset()
    logger.info(f"Initial state: {json.dumps(state, ensure_ascii=False, indent=2)}")

    # Take a step
    action = mock_model_generator(state["task"]["meter"])
    next_state, reward, done, info = env.step(action)

    logger.info(f"Action: {action}")
    logger.info(f"Reward: {reward}")
    logger.info(f"Done: {done}")
    logger.info(f"Info: {json.dumps(info, ensure_ascii=False, indent=2)}")
    logger.info(f"Next state: {json.dumps(next_state, ensure_ascii=False, indent=2)}")

    # Render the environment
    env.render()

    logger.info("-" * 50)


def test_dataset():
    """Test the dataset component."""
    logger.info("Testing Dataset...")

    # Create dataset
    dataset = PoetryDataset()

    # Sample a task
    task = dataset.sample_task()
    logger.info(f"Sampled task: {json.dumps(task, ensure_ascii=False, indent=2)}")

    # Get all meters
    meters = dataset.get_all_meters()
    logger.info(f"All meters: {meters}")

    # Get all topics
    topics = dataset.get_all_topics()
    logger.info(f"All topics: {topics}")

    # Generate dataset
    output_path = "output/test_dataset.json"
    os.makedirs("output", exist_ok=True)
    generate_dataset(output_path, num_tasks=10)
    logger.info(f"Generated dataset saved to: {output_path}")

    logger.info("-" * 50)


def test_llm_grader():
    """Test the LLM grader component."""
    logger.info("Testing LLM Grader...")

    # Create grader
    grader = LLMGrader()

    # Grade a poem
    for meter, poem in SAMPLE_POEMS.items():
        logger.info(f"Grading poem in meter: {meter}")

        grading_result = grader.grade_poem(
            poem=poem,
            topic="ज्ञानम्",  # Knowledge
            meter=meter
        )

        logger.info(f"Grading result: {json.dumps(grading_result, ensure_ascii=False, indent=2)}")

        # Calculate semantic reward
        semantic_reward = grader.calculate_semantic_reward(grading_result)
        logger.info(f"Semantic reward: {semantic_reward}")

        logger.info("-" * 50)


def test_trainer():
    """Test the trainer component."""
    logger.info("Testing Trainer...")

    # Create environment
    env = SanskritPoetryEnv()

    # Create grader
    grader = LLMGrader()

    # Create trainer
    trainer = SanskritPoetryTrainer(
        env=env,
        llm_grader=grader,
        model_generator=mock_model_generator,
        output_dir="output"
    )

    # Train for a few episodes
    stats = trainer.train(num_episodes=5, use_semantic_reward=True)
    logger.info(f"Training stats: {json.dumps(stats, ensure_ascii=False, indent=2)}")

    # Generate training data
    examples = trainer.generate_training_data(num_examples=3, output_file="training_examples.json")
    logger.info(f"Generated {len(examples)} training examples")

    logger.info("-" * 50)


def main():
    """Run all tests."""
    logger.info("Starting tests for Sanskrit Poetry RL Environment")

    # Test components
    test_meter_verifier()
    test_environment()
    test_dataset()
    test_llm_grader()
    test_trainer()

    logger.info("All tests completed!")


if __name__ == "__main__":
    main()
