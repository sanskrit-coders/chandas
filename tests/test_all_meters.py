#!/usr/bin/env python3
"""
Test script to verify all meters in the dataset with our improved normalization.
"""

import json
import logging
from rl_env.meter_verifier import MeterVerifier
from rl_env.environment import SanskritPoetryEnv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_all_meters():
    """Test all meters in the dataset with our improved normalization."""
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
        return

    if not examples:
        print("No examples found in the dataset")
        return

    # Initialize the meter verifier
    meter_verifier = MeterVerifier()
    
    # Initialize the environment (for reward calculation)
    env = SanskritPoetryEnv()
    
    # Group examples by meter
    meter_examples = {}
    for example in examples:
        meter = example.get('meter', '')
        if meter:
            if meter not in meter_examples:
                meter_examples[meter] = []
            meter_examples[meter].append(example)
    
    print(f"Found {len(meter_examples)} unique meters in the dataset")
    
    # Test each meter with its examples
    success_count = 0
    partial_count = 0
    failure_count = 0
    
    for meter, examples_list in meter_examples.items():
        print(f"\n{'='*50}")
        print(f"Testing meter: {meter}")
        
        # Normalize the meter name
        normalized_meter = meter_verifier.normalize_meter_name(meter)
        print(f"Normalized meter name: {normalized_meter}")
        
        # Test each example for this meter
        meter_success = 0
        meter_partial = 0
        meter_failure = 0
        
        for i, example in enumerate(examples_list):
            text = example.get('text', '')
            source = example.get('source', 'Unknown')
            
            # Verify the meter
            is_correct, details = meter_verifier.verify_meter(text, meter)
            
            # Calculate reward
            reward = env._calculate_reward(is_correct, details)
            
            # Count results
            if is_correct:
                meter_success += 1
                success_count += 1
            elif reward >= 0.5:  # Partial match with expected meter
                meter_partial += 1
                partial_count += 1
            else:
                meter_failure += 1
                failure_count += 1
        
        # Print summary for this meter
        total_examples = len(examples_list)
        print(f"Examples tested: {total_examples}")
        print(f"Exact matches: {meter_success} ({meter_success/total_examples*100:.1f}%)")
        print(f"Partial matches: {meter_partial} ({meter_partial/total_examples*100:.1f}%)")
        print(f"Failed matches: {meter_failure} ({meter_failure/total_examples*100:.1f}%)")
        
        # If there are failures, show details for the first failed example
        if meter_failure > 0:
            for example in examples_list:
                text = example.get('text', '')
                is_correct, details = meter_verifier.verify_meter(text, meter)
                if not is_correct:
                    print("\nExample of failed match:")
                    print(f"Text: {text[:50]}...")
                    identified_meters = details.get('identified_meters', {})
                    print(f"Identified meters: {identified_meters}")
                    
                    # Show normalized identified meters
                    exact_matches = set()
                    for item in identified_meters.get('exact', set()):
                        if isinstance(item, tuple):
                            meter_name = item[0]
                        else:
                            meter_name = item
                        exact_matches.add(meter_verifier.normalize_meter_name(meter_name))
                        
                    partial_matches = set()
                    for item in identified_meters.get('partial', set()):
                        if isinstance(item, tuple):
                            meter_name = item[0]
                        else:
                            meter_name = item
                        partial_matches.add(meter_verifier.normalize_meter_name(meter_name))
                    
                    print(f"Normalized exact matches: {exact_matches}")
                    print(f"Normalized partial matches: {partial_matches}")
                    break
    
    # Print overall summary
    total_examples = sum(len(examples_list) for examples_list in meter_examples.values())
    print(f"\n{'='*50}")
    print("Overall Summary")
    print(f"Total examples tested: {total_examples}")
    print(f"Exact matches: {success_count} ({success_count/total_examples*100:.1f}%)")
    print(f"Partial matches: {partial_count} ({partial_count/total_examples*100:.1f}%)")
    print(f"Failed matches: {failure_count} ({failure_count/total_examples*100:.1f}%)")

if __name__ == "__main__":
    test_all_meters()
