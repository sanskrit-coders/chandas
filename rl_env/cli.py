#!/usr/bin/env python
"""
Command-line interface for the Sanskrit Poetry RL Environment

This script provides a simple command-line interface to interact with the
RL environment for Sanskrit metrical poetry composition.
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, Any, Optional

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

def verify_poem(args: argparse.Namespace) -> None:
    """
    Verify if a Sanskrit poem adheres to a specific meter.
    
    Args:
        args: Command-line arguments
    """
    verifier = MeterVerifier()
    
    # Read poem from file if provided
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            poem = f.read()
    else:
        poem = args.poem
    
    # Get pattern from text
    pattern = verifier.get_pattern_from_text(poem)
    print(f"Pattern: {pattern}")
    
    # Identify meter
    identified_meters = verifier.identify_meter(poem)
    print(f"Identified meters:")
    for match_type, meters in identified_meters.items():
        print(f"  {match_type}: {', '.join(meters)}")
    
    # Verify meter if expected meter is provided
    if args.meter:
        is_correct, details = verifier.verify_meter(poem, args.meter)
        print(f"Is correct meter ({args.meter}): {is_correct}")
    
    # Get syllable info
    syllable_info = verifier.get_syllable_info(poem)
    print(f"\nSyllable analysis:")
    for line_info in syllable_info:
        print(f"Line: {line_info['text']}")
        print(f"Syllables: {' '.join(line_info['syllables'])}")
        print(f"Weights: {' '.join(line_info['weights'])}")
        print(f"Pattern: {line_info['pattern']}")
        print()

def generate_dataset_cmd(args: argparse.Namespace) -> None:
    """
    Generate a dataset of poetry tasks.
    
    Args:
        args: Command-line arguments
    """
    output_path = args.output
    num_tasks = args.num_tasks
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Generate dataset
    generate_dataset(output_path, num_tasks)
    print(f"Generated dataset with {num_tasks} tasks saved to: {output_path}")

def test_environment(args: argparse.Namespace) -> None:
    """
    Test the RL environment with a sample poem.
    
    Args:
        args: Command-line arguments
    """
    # Create environment
    env = SanskritPoetryEnv()
    
    # Reset environment
    state = env.reset()
    print(f"Initial state: {json.dumps(state, ensure_ascii=False, indent=2)}")
    
    # Take a step
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            poem = f.read()
    elif args.poem:
        poem = args.poem
    else:
        poem = mock_model_generator(state["task"]["meter"])
    
    next_state, reward, done, info = env.step(poem)
    
    print(f"Action (poem):")
    print(poem)
    print(f"Reward: {reward}")
    print(f"Done: {done}")
    print(f"Info: {json.dumps(info, ensure_ascii=False, indent=2)}")
    
    # Render the environment
    env.render()

def train_model(args: argparse.Namespace) -> None:
    """
    Train a model on the Sanskrit poetry composition task.
    
    Args:
        args: Command-line arguments
    """
    # Create environment
    dataset_path = args.dataset if args.dataset else None
    env = SanskritPoetryEnv(dataset_path)
    
    # Create grader
    grader = LLMGrader()
    
    # Create trainer
    trainer = SanskritPoetryTrainer(
        env=env,
        llm_grader=grader,
        model_generator=mock_model_generator,
        output_dir=args.output_dir
    )
    
    # Train for specified number of episodes
    stats = trainer.train(num_episodes=args.num_episodes, use_semantic_reward=args.semantic_reward)
    print(f"Training stats: {json.dumps(stats, ensure_ascii=False, indent=2)}")
    
    # Generate training data if requested
    if args.generate_data:
        examples = trainer.generate_training_data(
            num_examples=args.num_examples,
            output_file="training_examples.json"
        )
        print(f"Generated {len(examples)} training examples")

def main() -> None:
    """Parse command-line arguments and run the appropriate command."""
    parser = argparse.ArgumentParser(description="Sanskrit Poetry RL Environment CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Verify poem command
    verify_parser = subparsers.add_parser("verify", help="Verify a Sanskrit poem")
    verify_parser.add_argument("--poem", type=str, help="Sanskrit poem text")
    verify_parser.add_argument("--file", type=str, help="File containing Sanskrit poem")
    verify_parser.add_argument("--meter", type=str, help="Expected meter name")
    
    # Generate dataset command
    dataset_parser = subparsers.add_parser("generate-dataset", help="Generate a dataset of poetry tasks")
    dataset_parser.add_argument("--output", type=str, default="output/dataset.json", help="Output file path")
    dataset_parser.add_argument("--num-tasks", type=int, default=100, help="Number of tasks to generate")
    
    # Test environment command
    test_parser = subparsers.add_parser("test", help="Test the RL environment")
    test_parser.add_argument("--poem", type=str, help="Sanskrit poem text")
    test_parser.add_argument("--file", type=str, help="File containing Sanskrit poem")
    
    # Train model command
    train_parser = subparsers.add_parser("train", help="Train a model on the poetry composition task")
    train_parser.add_argument("--dataset", type=str, help="Path to dataset file")
    train_parser.add_argument("--output-dir", type=str, default="output", help="Output directory")
    train_parser.add_argument("--num-episodes", type=int, default=10, help="Number of episodes to train for")
    train_parser.add_argument("--semantic-reward", action="store_true", help="Use semantic reward")
    train_parser.add_argument("--generate-data", action="store_true", help="Generate training data")
    train_parser.add_argument("--num-examples", type=int, default=100, help="Number of examples to generate")
    
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == "verify":
        verify_poem(args)
    elif args.command == "generate-dataset":
        generate_dataset_cmd(args)
    elif args.command == "test":
        test_environment(args)
    elif args.command == "train":
        train_model(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
