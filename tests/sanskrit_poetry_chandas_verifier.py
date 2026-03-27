import os
import random
import json
import openai

import chandas
from chandas import identifier, syllabize
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

openai.api_key = os.getenv("OPENAI_API_KEY")

# Extended dataset for comprehensive testing
topics = [
    "शौर्य", "सौंदर्य", "भक्ति", "सत्य", "मित्रता", "प्रकृति",
    "विद्या", "धर्म", "शान्ति", "करुणा", "गुरु", "मातृभूमि"
]

meters = [
    "अनुष्टुप्", "वसन्ततिलका", "शार्दूलविक्रीडित",
    "मालिनी", "मन्दाक्रान्ता", "इन्द्रवज्रा"
]

METER_MAP = {
    "अनुष्टुप्": "Anuṣṭup",
    "वसन्ततिलका": "Vasantatilakā",
    "शार्दूलविक्रीडित": "Śārdūlavikrīḍita",
    "मालिनी": "Mālinī",
    "मन्दाक्रान्ता": "Mandākrāntā",
    "इन्द्रवज्रा": "Indravajrā",
}

def generate_prompt():
    topic = random.choice(topics)
    meter = random.choice(meters)
    return {
        "prompt": f"'{topic}' विषय पर एक संस्कृत श्लोक लिखिए जो '{meter}' छन्द में हो।",
        "topic": topic,
        "meter": meter
    }

def openai_generate(prompt):
    response = openai.chat.completions.create(  # Fixed API call
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=150,
    )
    return response.choices[0].message.content.strip()

def openai_thinking_generate(prompt):
    response = openai.chat.completions.create(  # Fixed API call
        model="o4-mini",
        messages=[{"role": "user", "content": prompt}],
        # temperature=0.4,
        # max_tokens=150,
    )
    return response.choices[0].message.content.strip()

# Function to check if a given shloka is in the specified meter
def is_meter_valid(shloka, meter):
    try:
        # Transliterate the shloka to ITRANS for meter checking
        shloka_itrans = transliterate(shloka, sanscript.DEVANAGARI, sanscript.ITRANS)
        # Get the meter identifier
        meter_identifier = identifier.MeterIdentifier()
        # Check if the shloka matches the specified meter
        return meter_identifier.is_meter(shloka_itrans, meter)
    except Exception as e:
        print(f"Error in checking meter: {e}")
        return False

def normalize_meter_name(devanagari_name):
    # Remove spaces and nukta for robust matching
    return METER_MAP.get(devanagari_name.strip().replace(" ", ""), devanagari_name)


def verify_meter(verse_lines, target_meter):
    """Verify if verse matches target meter using chandas library"""
    try:
        pattern_lines = chandas.to_pattern_lines(verse_lines)
        id_result = chandas.svat_identifier.IdentifyFromPatternLines(pattern_lines)
        all_matches = []
        for key in ['exact', 'partial', 'accidental']:
            if key in id_result:
                all_matches.extend(list(id_result[key]))
        # Normalize both target and predicted meter names
        target_norm = normalize_meter_name(target_meter).lower().replace(' ', '').replace('्', '')
        matched = False
        matched_meter = ''
        for meter in all_matches:
            meter_norm = meter.lower().replace(' ', '').replace('्', '')
            if target_norm in meter_norm:
                matched = True
                matched_meter = meter
                break
        if not matched and all_matches:
            matched_meter = all_matches[0]
        print(f"DEBUG: verse_lines={verse_lines}, all_matches={all_matches}, target_norm={target_norm}")
        return matched, matched_meter, id_result
    except Exception as e:
        return False, '', str(e)


def get_syllables(verse: str):
    """Get syllable breakdown"""
    try:
        return syllabize.get_syllables(verse)
    except Exception as e:
        return str(e)

def robust_semantic_grading(prompt, verse, target_meter):
    """Anti-reward hacking semantic evaluation"""
    grading_prompt = f"""
Grade this Sanskrit verse on a scale of 1-10 for each criterion:

Verse: {verse}
Expected Topic: {prompt.split("'")[1] if "'" in prompt else "N/A"} 
Expected Meter: {target_meter}

1. MEANING: Is this meaningful, grammatically correct Sanskrit? (1-10)
2. TOPIC_RELEVANCE: Does it genuinely address the given topic? (1-10) 
3. AUTHENTICITY: Does this sound like traditional Sanskrit poetry vs. word salad? (1-10)
4. COMPLETENESS: Is this a complete thought/verse? (1-10)

Format: MEANING:X TOPIC:X AUTHENTICITY:X COMPLETENESS:X
Then explain briefly in 2-3 sentences.
"""
    # return openai_generate(grading_prompt)
    return openai_thinking_generate(grading_prompt)


def generate_comprehensive_dataset(n=20):
    """Generate dataset for evaluation"""
    dataset = []
    for i in range(n):
        topic = random.choice(topics)
        meter = random.choice(meters)
        
        # Vary prompt complexity
        if i % 3 == 0:
            prompt = f"Write a Sanskrit verse about {topic} in {meter} meter with philosophical depth"
        else:
            prompt = f"'{topic}' विषय पर एक संस्कृत श्लोक लिखिए जो '{meter}' छन्द में हो।"
            
        dataset.append({
            "id": i,
            "topic": topic,
            "meter": meter, 
            "prompt": prompt,
            "difficulty": "basic" if i < n//2 else "advanced"
        })
    
    return dataset


def extract_verse_only(text):
    """
    Extract only the Sanskrit verse lines from the OpenAI output.
    Removes instructions, explanations, and non-Devanagari lines.
    Returns a list of padas (lines), split by danda.
    """
    import re
    lines = text.split('\n')
    verse_lines = []
    for line in lines:
        line = line.strip().replace('  ', '')
        if not line:
            continue
        if re.search(r'(श्लोक|छन्द|यह|हो सकता|प्रस्तुत|का वर्णन|रचित|यहाँ|होता है|है:|हैं:|है।|हैं।)', line):
            continue
        if len(re.findall(r'[\u0900-\u097F]', line)) > 0.5 * len(line):
            verse_lines.append(line)
    # Join and split by danda to get padas
    verse_text = ' '.join(verse_lines)
    padas = [p.strip() for p in re.split(r'[।॥]', verse_text) if p.strip()]
    return padas


def run_evaluation_pipeline(n=5):
    """Run complete evaluation pipeline"""
    results = []
    
    for i in range(n):
        print(f"\n--- Test {i+1}/{n} ---")
        
        prompt_data = generate_prompt()
        print(f"PROMPT: {prompt_data['prompt']}")
        
        # Generate verse
        verse_full = openai_generate(prompt_data["prompt"])
        print(f"VERSE: {verse_full}")

        # Extract only the verse
        verse_padas = extract_verse_only(verse_full)
        print(f"EXTRACTED VERSE: {verse_padas}")
        
        # Meter verification
        meter_match, predicted_meter, meter_details = verify_meter(verse_padas, prompt_data["meter"])
        print(f"Meter Match: {meter_match}")
        print(f"Predicted Meter: {predicted_meter}")
        
        # Semantic evaluation
        verse_str = ' '.join(verse_padas)
        semantic_score = robust_semantic_grading(prompt_data["prompt"], verse_str, prompt_data["meter"])
        print(f"Semantic Evaluation: {semantic_score}")
        
        # Syllable analysis
        syllables = get_syllables(verse_str)
        print(f"Syllables: {syllables}")
        
        # Store results
        result = {
            "id": i,
            "prompt": prompt_data["prompt"],
            "topic": prompt_data["topic"],
            "target_meter": prompt_data["meter"],
            "generated_verse": verse_str,
            "meter_match": meter_match,
            "predicted_meter": predicted_meter,
            "meter_details": meter_details,
            "semantic_evaluation": semantic_score,
            "syllables": syllables
        }
        results.append(result)
        
        print("="*80)
    
    return results

def save_results(results, filename="data/sanskrit_poetry_evaluation.json"):
    """Save results to JSON file"""

    # Check if file exists and load existing data
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f_read:
            try:
                existing = json.load(f_read)
            except Exception:
                existing = []
    else:
        existing = []

    # Append new results
    combined = existing + results

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, indent=2)
    print(f"Results appended and saved to {filename}")

def analyze_results(results):
    """Analyze evaluation results"""
    total = len(results)
    meter_matches = sum(1 for r in results if r['meter_match'])
    
    print(f"\n--- ANALYSIS ---")
    print(f"Total tests: {total}")
    print(f"Meter matches: {meter_matches}/{total} ({meter_matches/total*100:.1f}%)")
    
    # Analyze by meter type
    meter_stats = {}
    for result in results:
        meter = result['target_meter']
        if meter not in meter_stats:
            meter_stats[meter] = {'total': 0, 'matches': 0}
        meter_stats[meter]['total'] += 1
        if result['meter_match']:
            meter_stats[meter]['matches'] += 1
    
    print("\nMeter-wise performance:")
    for meter, stats in meter_stats.items():
        accuracy = stats['matches']/stats['total']*100 if stats['total'] > 0 else 0
        print(f"  {meter}: {stats['matches']}/{stats['total']} ({accuracy:.1f}%)")

# Main execution
if __name__ == "__main__":
    print("Sanskrit Poetry Verifier - Starting Evaluation")
    
    dataset = generate_comprehensive_dataset(n=20)
    print("Dataset generated for evaluation.")
    print("Sample dataset:", dataset[:5])  # Print first 5 samples for verification
    # Generate and save dataset
    if os.path.exists("data/sanskrit_dataset.json"):
        # Load existing data and append
        with open("data/sanskrit_dataset.json", 'r', encoding='utf-8') as f_read:
            existing_data = json.load(f_read)
        combined_data = existing_data + dataset
    else:
        combined_data = dataset

    with open("data/sanskrit_dataset.json", 'w', encoding='utf-8') as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=2)
    print("Dataset saved to data/sanskrit_dataset.json")  
    # Run evaluation pipeline
    results = run_evaluation_pipeline(n=5)
    
    # Save and analyze results
    save_results(results)
    analyze_results(results)
    
    print("\nEvaluation complete!")


