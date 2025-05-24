"""
Trainer Module for Sanskrit Poetry RL Environment

This module provides functionality to train models on the Sanskrit poetry
composition task using reinforcement learning.
"""

import os
import json
import logging
import random
from typing import Dict, List, Any, Optional, Callable

from .environment import SanskritPoetryEnv
from .llm_grader import LLMGrader

class SanskritPoetryTrainer:
    """
    Trainer for Sanskrit poetry composition models.
    
    This class provides methods to:
    1. Train models using the RL environment
    2. Evaluate model performance
    3. Generate and save training data
    """
    
    def __init__(self, env: Optional[SanskritPoetryEnv] = None, 
                 llm_grader: Optional[LLMGrader] = None,
                 model_generator: Optional[Callable] = None,
                 output_dir: str = "output"):
        """
        Initialize the trainer.
        
        Args:
            env: The RL environment
            llm_grader: The LLM grader for semantic evaluation
            model_generator: Function that generates poetry given a prompt
            output_dir: Directory to save outputs
        """
        self.env = env or SanskritPoetryEnv()
        self.llm_grader = llm_grader or LLMGrader()
        self.model_generator = model_generator
        self.output_dir = output_dir
        self.logger = logging.getLogger(__name__)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Training statistics
        self.stats = {
            "episodes": 0,
            "correct_meter": 0,
            "partial_meter": 0,
            "incorrect_meter": 0,
            "high_semantic_quality": 0,
            "medium_semantic_quality": 0,
            "low_semantic_quality": 0,
            "total_reward": 0,
            "average_reward": 0
        }
    
    def train(self, num_episodes: int = 100, use_semantic_reward: bool = True) -> Dict[str, Any]:
        """
        Train a model on the Sanskrit poetry composition task.
        
        Args:
            num_episodes: Number of episodes to train for
            use_semantic_reward: Whether to use semantic reward from LLM grader
            
        Returns:
            Training statistics
        """
        if not self.model_generator:
            self.logger.error("No model generator provided. Cannot train.")
            return self.stats
        
        # Reset statistics
        self.stats = {
            "episodes": 0,
            "correct_meter": 0,
            "partial_meter": 0,
            "incorrect_meter": 0,
            "high_semantic_quality": 0,
            "medium_semantic_quality": 0,
            "low_semantic_quality": 0,
            "total_reward": 0,
            "average_reward": 0,
            "examples": []
        }
        
        for episode in range(num_episodes):
            # Reset the environment
            state = self.env.reset()
            done = False
            episode_reward = 0
            
            while not done:
                # Generate action (Sanskrit poem) using the model
                prompt = self._create_prompt(state)
                action = self.model_generator(prompt)
                
                # Take a step in the environment
                next_state, reward, done, info = self.env.step(action)
                
                # If using semantic reward, adjust the reward
                if use_semantic_reward:
                    grading_result = self.llm_grader.grade_poem(
                        poem=action,
                        topic=state['task']['topic'],
                        meter=state['task']['meter']
                    )
                    semantic_reward = self.llm_grader.calculate_semantic_reward(grading_result)
                    
                    # Combine metrical and semantic rewards
                    # You can adjust the weights based on your priorities
                    combined_reward = 0.7 * reward + 0.3 * semantic_reward
                    reward = combined_reward
                    
                    # Update semantic quality statistics
                    if semantic_reward > 0.7:
                        self.stats["high_semantic_quality"] += 1
                    elif semantic_reward > 0.4:
                        self.stats["medium_semantic_quality"] += 1
                    else:
                        self.stats["low_semantic_quality"] += 1
                
                # Update episode reward
                episode_reward += reward
                
                # Update state
                state = next_state
            
            # Update statistics
            self.stats["episodes"] += 1
            self.stats["total_reward"] += episode_reward
            self.stats["average_reward"] = self.stats["total_reward"] / self.stats["episodes"]
            
            if info["is_correct"]:
                self.stats["correct_meter"] += 1
            elif info.get("meter_details", {}).get("is_partial_match", False):
                self.stats["partial_meter"] += 1
            else:
                self.stats["incorrect_meter"] += 1
            
            # Save example
            if len(self.stats["examples"]) < 10:  # Save up to 10 examples
                example = {
                    "task": state["task"],
                    "poem": action,
                    "reward": episode_reward,
                    "is_correct_meter": info["is_correct"],
                    "meter_details": info.get("meter_details", {})
                }
                if use_semantic_reward:
                    example["semantic_grading"] = grading_result
                
                self.stats["examples"].append(example)
            
            # Log progress
            if (episode + 1) % 10 == 0:
                self.logger.info(f"Episode {episode + 1}/{num_episodes}, Average Reward: {self.stats['average_reward']:.4f}")
        
        # Save statistics
        self._save_stats()
        
        return self.stats
    
    def evaluate(self, num_episodes: int = 20, use_semantic_reward: bool = True) -> Dict[str, Any]:
        """
        Evaluate a model on the Sanskrit poetry composition task.
        
        Args:
            num_episodes: Number of episodes to evaluate on
            use_semantic_reward: Whether to use semantic reward from LLM grader
            
        Returns:
            Evaluation statistics
        """
        # Similar to train, but without updating the model
        return self.train(num_episodes, use_semantic_reward)
    
    def generate_training_data(self, num_examples: int = 100, output_file: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate training data for supervised learning.
        
        Args:
            num_examples: Number of examples to generate
            output_file: File to save the examples to
            
        Returns:
            List of training examples
        """
        examples = []
        
        for _ in range(num_examples):
            # Reset the environment
            state = self.env.reset()
            
            # Create a prompt
            prompt = self._create_prompt(state)
            
            # Create an example
            example = {
                "prompt": prompt,
                "task": state["task"],
                "meter_info": state.get("meter_info", {})
            }
            
            examples.append(example)
        
        # Save examples if output file is provided
        if output_file:
            output_path = os.path.join(self.output_dir, output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({"examples": examples}, f, ensure_ascii=False, indent=2)
        
        return examples
    
    def _create_prompt(self, state: Dict[str, Any]) -> str:
        """
        Create a prompt for the model based on the current state.
        
        Args:
            state: The current state of the environment
            
        Returns:
            A prompt string
        """
        meter = state["task"]["meter"]
        topic = state["task"]["topic"]
        
        # Get meter information if available
        meter_info = state.get("meter_info", {})
        meter_pattern = meter_info.get("pattern", "")
        meter_description = meter_info.get("description", "")
        
        # Create the prompt
        prompt = f"Compose a Sanskrit poem in {meter} meter about {topic}."
        
        if meter_pattern:
            prompt += f" The metrical pattern is: {meter_pattern}"
        
        if meter_description:
            prompt += f" ({meter_description})"
        
        return prompt
    
    def _save_stats(self) -> None:
        """Save training statistics to a file."""
        stats_path = os.path.join(self.output_dir, "training_stats.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)
