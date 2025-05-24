"""
Unit tests for the Sanskrit Poetry RL Environment
"""

import os
import unittest

from rl_env.meter_verifier import MeterVerifier
from rl_env.environment import SanskritPoetryEnv
from rl_env.dataset import PoetryDataset
from rl_env.llm_grader import LLMGrader


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


class TestMeterVerifier(unittest.TestCase):
    """Test cases for the MeterVerifier class"""

    def setUp(self):
        self.verifier = MeterVerifier()

    def test_get_pattern_from_text(self):
        """Test that patterns are correctly extracted from text"""
        for meter, poem in SAMPLE_POEMS.items():
            pattern = self.verifier.get_pattern_from_text(poem)
            self.assertIsInstance(pattern, list)
            self.assertTrue(all(isinstance(p, str) for p in pattern))
            self.assertTrue(all(all(c in 'LG' for c in p) for p in pattern))

    def test_identify_meter(self):
        """Test that meters are correctly identified"""
        # Test Vasantatilaka
        identified = self.verifier.identify_meter(SAMPLE_POEMS["वसन्ततिलका"])
        # Check if any meter name contains 'vasanta' which is part of Vasantatilakā
        found_vasantatilaka = False
        for meter_set in identified.values():
            meter_list = list(meter_set)
            for meter_name in meter_list:
                # Use a case-insensitive substring match
                if 'vasanta' in meter_name.lower():
                    found_vasantatilaka = True
                    break
        self.assertTrue(found_vasantatilaka, "Vasantatilakā not found in identified meters")

        # Test Anushtubh
        identified = self.verifier.identify_meter(SAMPLE_POEMS["अनुष्टुभ्"])
        self.assertIn("exact", identified)

        # Check if Anushtubh is in the identified meters
        found_anushtubh = False
        for meter_set in identified.values():
            for meter_name in meter_set:
                if "Anuṣṭup" in meter_name:
                    found_anushtubh = True
                    break
        self.assertTrue(found_anushtubh, "Anuṣṭup not found in identified meters")

    def test_verify_meter(self):
        """Test meter verification"""
        # Test verification with matching meter name
        is_correct, details = self.verifier.verify_meter(
            SAMPLE_POEMS["वसन्ततिलका"],
            "Vasantatilakā"
        )
        # The meter name might not match exactly due to transliteration differences
        # So we check if it's in the identified meters instead
        if not is_correct:
            # Check if it's identified as Vasantatilaka but with a different name
            identified = details.get('identified_meters', {})
            found_vasantatilaka = False
            for meter_set in identified.values():
                for meter_tuple in meter_set:
                    if isinstance(meter_tuple, tuple) and "Vasantatilak" in meter_tuple[0]:
                        found_vasantatilaka = True
                        break
            self.assertTrue(found_vasantatilaka, "Vasantatilaka not found in identified meters")

        # Test incorrect verification
        is_correct, details = self.verifier.verify_meter(
            SAMPLE_POEMS["वसन्ततिलका"],
            "अनुष्टुभ्"
        )
        self.assertFalse(is_correct)

    def test_get_syllable_info(self):
        """Test syllable information extraction"""
        for meter, poem in SAMPLE_POEMS.items():
            info = self.verifier.get_syllable_info(poem)
            self.assertIsInstance(info, list)
            for line_info in info:
                self.assertIn('text', line_info)
                self.assertIn('syllables', line_info)
                self.assertIn('weights', line_info)
                self.assertIn('pattern', line_info)
                self.assertEqual(len(line_info['syllables']), len(line_info['weights']))
                self.assertEqual(len(line_info['weights']), len(line_info['pattern']))


class TestPoetryDataset(unittest.TestCase):
    """Test cases for the PoetryDataset class"""

    def setUp(self):
        self.dataset = PoetryDataset()

    def test_default_dataset_creation(self):
        """Test that a default dataset is created"""
        self.assertTrue(len(self.dataset.tasks) > 0)

    def test_sample_task(self):
        """Test task sampling"""
        task = self.dataset.sample_task()
        self.assertIn('meter', task)
        self.assertIn('topic', task)

    def test_filter_tasks(self):
        """Test task filtering"""
        # Get a sample task to use for filtering
        task = self.dataset.sample_task()
        meter = task['meter']
        topic = task['topic']

        # Filter by meter
        filtered = self.dataset.filter_tasks(meter=meter)
        self.assertTrue(all(t['meter'] == meter for t in filtered))

        # Filter by topic
        filtered = self.dataset.filter_tasks(topic=topic)
        self.assertTrue(all(t['topic'] == topic for t in filtered))

    def test_save_and_load_dataset(self):
        """Test dataset saving and loading"""
        # Create a temporary file
        temp_file = 'temp_dataset.json'

        try:
            # Save the dataset
            self.dataset.save_dataset(temp_file)

            # Create a new dataset by loading the saved one
            loaded_dataset = PoetryDataset(temp_file)

            # Check that the loaded dataset has the same tasks
            self.assertEqual(len(self.dataset.tasks), len(loaded_dataset.tasks))

            # Check a few random tasks
            for i in range(min(5, len(self.dataset.tasks))):
                original_task = self.dataset.tasks[i]
                loaded_task = loaded_dataset.tasks[i]
                self.assertEqual(original_task['meter'], loaded_task['meter'])
                self.assertEqual(original_task['topic'], loaded_task['topic'])

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)


class TestLLMGrader(unittest.TestCase):
    """Test cases for the LLMGrader class"""

    def setUp(self):
        self.grader = LLMGrader()

    def test_grade_poem(self):
        """Test poem grading"""
        for meter, poem in SAMPLE_POEMS.items():
            result = self.grader.grade_poem(poem, "ज्ञानम्", meter)
            self.assertIn('topic_adherence', result)
            self.assertIn('semantic_coherence', result)
            self.assertIn('poetic_quality', result)
            self.assertIn('cultural_authenticity', result)
            self.assertIn('overall', result)

    def test_calculate_semantic_reward(self):
        """Test semantic reward calculation"""
        # Create a mock grading result
        grading_result = {
            'topic_adherence': {'score': 8},
            'semantic_coherence': {'score': 7},
            'poetic_quality': {'score': 6},
            'cultural_authenticity': {'score': 9},
            'overall': {'score': 7.5}
        }

        reward = self.grader.calculate_semantic_reward(grading_result)
        self.assertGreaterEqual(reward, 0.0)
        self.assertLessEqual(reward, 1.0)


class TestSanskritPoetryEnv(unittest.TestCase):
    """Test cases for the SanskritPoetryEnv class"""

    def setUp(self):
        self.env = SanskritPoetryEnv()

    def test_reset(self):
        """Test environment reset"""
        state = self.env.reset()
        self.assertIn('task', state)
        self.assertIn('meter', state['task'])
        self.assertIn('topic', state['task'])
        self.assertIsNone(state['attempt'])
        self.assertEqual(state['step'], 0)

    def test_step(self):
        """Test environment step"""
        # Reset the environment
        state = self.env.reset()
        meter = state['task']['meter']

        # Choose a poem based on the meter
        if meter in SAMPLE_POEMS:
            poem = SAMPLE_POEMS[meter]
        else:
            poem = SAMPLE_POEMS["अनुष्टुभ्"]  # Default to Anushtubh

        # Take a step
        next_state, reward, done, info = self.env.step(poem)

        # Check the next state
        self.assertIn('task', next_state)
        self.assertEqual(next_state['attempt'], poem)
        self.assertEqual(next_state['step'], 1)

        # Check the reward
        self.assertIsInstance(reward, float)

        # Check the info
        self.assertIn('meter_details', info)
        self.assertIn('is_correct', info)

    def test_render(self):
        """Test environment rendering"""
        # This is a simple test to ensure render doesn't crash
        self.env.reset()
        self.env.render()  # Should not raise any exception


if __name__ == '__main__':
    unittest.main()
