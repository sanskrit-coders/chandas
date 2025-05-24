"""
LLM Grader for Sanskrit Poetry

This module provides functionality to grade Sanskrit poetry using LLMs
to evaluate semantic quality and prevent reward hacking.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Tuple

class LLMGrader:
    """
    Uses LLMs to grade Sanskrit poetry based on semantic quality and adherence to topic.
    
    This helps prevent reward hacking where models might generate metrically correct
    but semantically meaningless text.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4"):
        """
        Initialize the LLM grader.
        
        Args:
            api_key: API key for the LLM service (if using OpenAI or similar)
            model: Model to use for grading
        """
        self.api_key = api_key
        self.model = model
        self.logger = logging.getLogger(__name__)
        
        # Prompt templates
        self.grading_prompt_template = """
        You are an expert in Sanskrit poetry and literature. Your task is to evaluate the quality of the following Sanskrit poem.
        
        Poem Topic: {topic}
        Expected Meter: {meter}
        
        Poem:
        {poem}
        
        Please evaluate the poem on the following criteria:
        1. Adherence to Topic (0-10): Does the poem address the given topic?
        2. Semantic Coherence (0-10): Is the poem semantically meaningful and coherent?
        3. Poetic Quality (0-10): Does the poem use poetic devices, imagery, and elegant language?
        4. Cultural Authenticity (0-10): Does the poem reflect Sanskrit poetic traditions and cultural elements?
        
        For each criterion, provide a score and a brief explanation. Then provide an overall score (0-10) and a summary of your evaluation.
        
        Format your response as a JSON object with the following structure:
        {{
            "topic_adherence": {{
                "score": <score>,
                "explanation": "<explanation>"
            }},
            "semantic_coherence": {{
                "score": <score>,
                "explanation": "<explanation>"
            }},
            "poetic_quality": {{
                "score": <score>,
                "explanation": "<explanation>"
            }},
            "cultural_authenticity": {{
                "score": <score>,
                "explanation": "<explanation>"
            }},
            "overall": {{
                "score": <score>,
                "explanation": "<explanation>"
            }}
        }}
        """
    
    def grade_poem(self, poem: str, topic: str, meter: str) -> Dict[str, Any]:
        """
        Grade a Sanskrit poem using an LLM.
        
        Args:
            poem: The Sanskrit poem text
            topic: The topic of the poem
            meter: The expected meter of the poem
            
        Returns:
            Dictionary with grading results
        """
        # If no API key is provided, return a mock grading result
        if not self.api_key:
            return self._mock_grading(poem, topic, meter)
        
        try:
            # Format the prompt
            prompt = self.grading_prompt_template.format(
                poem=poem,
                topic=topic,
                meter=meter
            )
            
            # Call the LLM API (implementation depends on the service used)
            response = self._call_llm_api(prompt)
            
            # Parse the response
            grading_result = json.loads(response)
            
            return grading_result
        
        except Exception as e:
            self.logger.error(f"Error grading poem: {e}")
            return self._mock_grading(poem, topic, meter)
    
    def _call_llm_api(self, prompt: str) -> str:
        """
        Call the LLM API to get a response.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            The LLM's response
        """
        # This is a placeholder. Implementation depends on the LLM service used.
        # For example, if using OpenAI:
        """
        import openai
        
        openai.api_key = self.api_key
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert in Sanskrit poetry and literature."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
        """
        
        # For now, return a mock response
        return json.dumps(self._mock_grading("", "", ""))
    
    def _mock_grading(self, poem: str, topic: str, meter: str) -> Dict[str, Any]:
        """
        Generate a mock grading result for testing.
        
        Args:
            poem: The Sanskrit poem text
            topic: The topic of the poem
            meter: The expected meter of the poem
            
        Returns:
            Dictionary with mock grading results
        """
        # This is a simplified mock grading
        # In a real implementation, you might want to do some basic analysis
        return {
            "topic_adherence": {
                "score": 7,
                "explanation": "The poem generally addresses the topic, but could be more focused."
            },
            "semantic_coherence": {
                "score": 8,
                "explanation": "The poem is semantically coherent and meaningful."
            },
            "poetic_quality": {
                "score": 7,
                "explanation": "The poem uses some poetic devices and imagery."
            },
            "cultural_authenticity": {
                "score": 8,
                "explanation": "The poem reflects Sanskrit poetic traditions."
            },
            "overall": {
                "score": 7.5,
                "explanation": "A good poem that addresses the topic and follows Sanskrit traditions."
            }
        }
    
    def calculate_semantic_reward(self, grading_result: Dict[str, Any]) -> float:
        """
        Calculate a reward based on the semantic quality of the poem.
        
        Args:
            grading_result: The grading result from grade_poem
            
        Returns:
            A reward value between 0 and 1
        """
        # Extract scores
        topic_score = grading_result["topic_adherence"]["score"] / 10.0
        semantic_score = grading_result["semantic_coherence"]["score"] / 10.0
        poetic_score = grading_result["poetic_quality"]["score"] / 10.0
        cultural_score = grading_result["cultural_authenticity"]["score"] / 10.0
        overall_score = grading_result["overall"]["score"] / 10.0
        
        # Calculate weighted average
        # You can adjust the weights based on what aspects you want to emphasize
        weights = {
            "topic": 0.3,
            "semantic": 0.3,
            "poetic": 0.2,
            "cultural": 0.1,
            "overall": 0.1
        }
        
        reward = (
            weights["topic"] * topic_score +
            weights["semantic"] * semantic_score +
            weights["poetic"] * poetic_score +
            weights["cultural"] * cultural_score +
            weights["overall"] * overall_score
        )
        
        return reward
