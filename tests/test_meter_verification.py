#!/usr/bin/env python3
"""
Test script to verify that the meter verification system correctly identifies
known poems with the right meter.
"""

import json
import logging
from rl_env.meter_verifier import MeterVerifier
from rl_env.environment import SanskritPoetryEnv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Set to DEBUG level for more detailed logs
logger.setLevel(logging.INFO)


def test_meter_verification():
    """Test meter verification with known poems from the dataset."""
    # Load the dataset
    dataset_path = "output/sanskrit_poetry_dataset.json"
    print(f"Loading dataset from {dataset_path}")
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            examples = data.get('examples', [])
            print(f"Loaded {len(examples)} examples from dataset")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        logger.error(f"Error loading dataset: {e}")
        return

    if not examples:
        print("No examples found in the dataset")
        logger.error("No examples found in the dataset")
        return

    # Initialize the meter verifier
    meter_verifier = MeterVerifier()

    # Initialize the environment (for reward calculation)
    env = SanskritPoetryEnv()

    # Test each example
    success_count = 0
    partial_count = 0
    failure_count = 0

    print(f"Testing {len(examples)} examples from the dataset")
    logger.info(f"Testing {len(examples)} examples from the dataset")

    # Limit to first 5 examples for brevity
    test_examples = examples[:5]
    print(f"Testing first {len(test_examples)} examples for brevity")

    for i, example in enumerate(test_examples):
        text = example.get('text', '')
        expected_meter = example.get('meter', '')
        source = example.get('source', 'Unknown')

        if not text or not expected_meter:
            print(f"Example {i} is missing text or meter")
            logger.warning(f"Example {i} is missing text or meter")
            continue

        print(f"\nExample {i+1}/{len(test_examples)}")
        print(f"Meter: {expected_meter}")
        print(f"Source: {source}")
        print(f"Text: {text[:50]}...")  # Show first 50 chars

        # Verify the meter
        is_correct, details = meter_verifier.verify_meter(text, expected_meter)

        # Calculate reward
        reward = env._calculate_reward(is_correct, details)

        # Log results
        print(f"Is correct: {is_correct}")
        print(f"Reward: {reward}")

        identified_meters = details.get('identified_meters', {})
        print(f"Identified meters: {identified_meters}")

        # Count results
        if is_correct:
            success_count += 1
            print("EXACT MATCH! ")
        elif reward >= 0.5:  # Partial match with expected meter
            partial_count += 1
            print("PARTIAL MATCH ")
        else:
            failure_count += 1
            print("NO MATCH ")

    # Log summary
    print("\n=== Summary ===")
    print(f"Total examples tested: {len(test_examples)}")
    print(f"Exact matches: {success_count} ({success_count/len(test_examples)*100:.1f}%)")
    print(f"Partial matches: {partial_count} ({partial_count/len(test_examples)*100:.1f}%)")
    print(f"Failed matches: {failure_count} ({failure_count/len(test_examples)*100:.1f}%)")

    logger.info("\n=== Summary ===")
    logger.info(f"Total examples tested: {len(test_examples)}")
    logger.info(f"Exact matches: {success_count} ({success_count/len(test_examples)*100:.1f}%)")
    logger.info(f"Partial matches: {partial_count} ({partial_count/len(test_examples)*100:.1f}%)")
    logger.info(f"Failed matches: {failure_count} ({failure_count/len(test_examples)*100:.1f}%)")

    return success_count, partial_count, failure_count


if __name__ == "__main__":
    test_meter_verification()
