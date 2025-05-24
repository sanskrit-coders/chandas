#!/usr/bin/env python3
"""
Test script to verify that the meter verification system correctly identifies
a known poem with its expected meter.
"""

import logging
from rl_env.meter_verifier import MeterVerifier
from rl_env.environment import SanskritPoetryEnv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Set to DEBUG level for more detailed logs
logger.setLevel(logging.INFO)

def normalize_meter_name(name):
    """
    Normalize meter names to handle script differences.
    Convert Devanagari to lowercase Latin transliteration for comparison.
    """
    # Map of Devanagari meter names to their Latin transliteration
    meter_map = {
        "अनुष्टुभ्": "anuṣṭup",
        "वसन्ततिलका": "vasantatilakā",
        "शार्दूलविक्रीडितम्": "śārdūlavikrīḍitam",
        "मन्दाक्रान्ता": "mandākrāntā",
        "शिखरिणी": "śikhariṇī",
        "मालिनी": "mālinī",
        "इन्द्रवज्रा": "indravajrā",
        "भुजङ्गप्रयातम्": "bhujańgaprayātam"
    }
    
    # If the name is in Devanagari, convert it
    if name in meter_map:
        return meter_map[name].lower()
    
    # Otherwise, just return the lowercase version
    return name.lower()

def test_with_known_poem():
    """Test meter verification with a known poem."""
    # Initialize the meter verifier
    meter_verifier = MeterVerifier()
    
    # Initialize the environment (for reward calculation)
    env = SanskritPoetryEnv()
    
    # Known poem in Mandākrāntā meter
    poem = """मन्दं मन्दं नुदति पवनश्चानुकूलो यथा त्वं
आलोकः प्रातरुदयगिरेरागतश्चाप्रतीपः।
आपाण्डुत्वं वदनमधुना संजहाति प्रियायाः
कल्याणी ते दिशतु विधिना दक्षिणा दिक् प्रयाणम्॥"""
    
    # Expected meter (both in Devanagari and Latin)
    expected_meter_dev = "मन्दाक्रान्ता"
    expected_meter_lat = "mandākrāntā"
    
    print(f"\nTesting known poem in {expected_meter_dev} meter")
    print(f"Poem: {poem[:50]}...")
    
    # Test with Devanagari meter name
    print("\n1. Testing with Devanagari meter name:")
    is_correct_dev, details_dev = meter_verifier.verify_meter(poem, expected_meter_dev)
    reward_dev = env._calculate_reward(is_correct_dev, details_dev)
    
    print(f"Is correct: {is_correct_dev}")
    print(f"Reward: {reward_dev}")
    print(f"Identified meters: {details_dev.get('identified_meters', {})}")
    
    # Test with Latin meter name
    print("\n2. Testing with Latin meter name:")
    is_correct_lat, details_lat = meter_verifier.verify_meter(poem, expected_meter_lat)
    reward_lat = env._calculate_reward(is_correct_lat, details_lat)
    
    print(f"Is correct: {is_correct_lat}")
    print(f"Reward: {reward_lat}")
    print(f"Identified meters: {details_lat.get('identified_meters', {})}")
    
    # Test with normalized meter name comparison
    print("\n3. Testing with normalized meter name comparison:")
    identified_meters = meter_verifier.identify_meter(poem)
    
    # Normalize the expected meter name
    normalized_expected = normalize_meter_name(expected_meter_dev)
    
    # Check if any of the identified meters match the normalized expected meter
    exact_matches = {normalize_meter_name(m) for m in identified_meters.get('exact', set())}
    partial_matches = {normalize_meter_name(m) for m in identified_meters.get('partial', set())}
    
    is_exact_match = normalized_expected in exact_matches
    is_partial_match = normalized_expected in partial_matches
    
    print(f"Normalized expected meter: {normalized_expected}")
    print(f"Normalized exact matches: {exact_matches}")
    print(f"Normalized partial matches: {partial_matches}")
    print(f"Is exact match: {is_exact_match}")
    print(f"Is partial match: {is_partial_match}")
    
    # Calculate reward based on normalized comparison
    if is_exact_match:
        reward = 1.0
        print("EXACT MATCH! ✓")
    elif is_partial_match:
        reward = 0.5
        print("PARTIAL MATCH ⚠")
    elif exact_matches:
        reward = 0.2
        print("DIFFERENT EXACT MATCH ⚠")
    elif partial_matches:
        reward = 0.1
        print("DIFFERENT PARTIAL MATCH ⚠")
    else:
        reward = 0.0
        print("NO MATCH ✗")
    
    print(f"Calculated reward: {reward}")

if __name__ == "__main__":
    test_with_known_poem()
