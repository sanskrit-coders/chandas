"""
Dataset Module for Sanskrit Poetry RL Environment

This module provides functionality to create, load, and manage datasets
of Sanskrit poetry composition tasks.
"""

import os
import json
import random
from typing import Dict, List, Any, Optional

class PoetryDataset:
    """
    Dataset for Sanskrit poetry composition tasks.
    
    Each task consists of:
    - A meter (chandas) to use
    - A topic to write about
    - Optional additional constraints
    """
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize the dataset.
        
        Args:
            dataset_path: Path to the dataset JSON file
        """
        self.tasks = []
        
        if dataset_path and os.path.exists(dataset_path):
            self.load_dataset(dataset_path)
        else:
            # Create a default dataset if none is provided
            self._create_default_dataset()
    
    def load_dataset(self, dataset_path: str) -> None:
        """
        Load a dataset from a JSON file.
        
        Args:
            dataset_path: Path to the dataset JSON file
        """
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = data.get('tasks', [])
        except Exception as e:
            print(f"Error loading dataset: {e}")
            self._create_default_dataset()
    
    def save_dataset(self, dataset_path: str) -> None:
        """
        Save the dataset to a JSON file.
        
        Args:
            dataset_path: Path to save the dataset
        """
        try:
            with open(dataset_path, 'w', encoding='utf-8') as f:
                json.dump({'tasks': self.tasks}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving dataset: {e}")
    
    def _create_default_dataset(self) -> None:
        """Create a default dataset with common meters and topics."""
        # Common Sanskrit meters
        meters = [
            {
                "name": "अनुष्टुभ्",
                "description": "8 syllables per quarter (pada)",
                "pattern": "LLGLLGLG"  # Simplified pattern, actual can vary
            },
            {
                "name": "वसन्ततिलका",
                "description": "14 syllables per line",
                "pattern": "LGLGGLLGLGLGG"
            },
            {
                "name": "शार्दूलविक्रीडितम्",
                "description": "19 syllables per line",
                "pattern": "GGGLGLGLLLGGLGLGLG"
            },
            {
                "name": "मन्दाक्रान्ता",
                "description": "17 syllables per line",
                "pattern": "GGGGLLLLLLGLGLGG"
            },
            {
                "name": "शिखरिणी",
                "description": "17 syllables per line",
                "pattern": "LGGLLLLGLGLGLGG"
            },
            {
                "name": "मालिनी",
                "description": "15 syllables per line",
                "pattern": "LLLLGGGGLLGLGG"
            },
            {
                "name": "इन्द्रवज्रा",
                "description": "11 syllables per line",
                "pattern": "LGLGGLLGLG"
            }
        ]
        
        # Common topics for Sanskrit poetry
        topics = [
            "प्रकृतिः",  # Nature
            "प्रेम",     # Love
            "ईश्वरः",    # God/Divine
            "वीरता",     # Heroism
            "ज्ञानम्",    # Knowledge/Wisdom
            "ऋतुवर्णनम्",  # Seasons
            "सूर्यः",     # Sun
            "चन्द्रः",    # Moon
            "नदी",       # River
            "पर्वतः",     # Mountain
            "समुद्रः",    # Ocean
            "वनम्",      # Forest
            "राजा",      # King
            "युद्धम्",    # War
            "शान्तिः"     # Peace
        ]
        
        # Generate tasks by combining meters and topics
        self.tasks = []
        for meter in meters:
            for topic in topics:
                task = {
                    "meter": meter["name"],
                    "meter_info": {
                        "description": meter["description"],
                        "pattern": meter["pattern"]
                    },
                    "topic": topic,
                    "difficulty": random.choice(["easy", "medium", "hard"])
                }
                self.tasks.append(task)
    
    def sample_task(self) -> Dict[str, Any]:
        """
        Sample a random task from the dataset.
        
        Returns:
            A task dictionary
        """
        if not self.tasks:
            self._create_default_dataset()
        
        return random.choice(self.tasks)
    
    def filter_tasks(self, meter: Optional[str] = None, topic: Optional[str] = None, 
                    difficulty: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Filter tasks based on criteria.
        
        Args:
            meter: Filter by meter name
            topic: Filter by topic
            difficulty: Filter by difficulty level
            
        Returns:
            List of filtered tasks
        """
        filtered_tasks = self.tasks
        
        if meter:
            filtered_tasks = [t for t in filtered_tasks if t["meter"] == meter]
        
        if topic:
            filtered_tasks = [t for t in filtered_tasks if t["topic"] == topic]
        
        if difficulty:
            filtered_tasks = [t for t in filtered_tasks if t.get("difficulty") == difficulty]
        
        return filtered_tasks
    
    def add_task(self, task: Dict[str, Any]) -> None:
        """
        Add a new task to the dataset.
        
        Args:
            task: Task dictionary
        """
        self.tasks.append(task)
    
    def get_all_meters(self) -> List[str]:
        """
        Get a list of all meters in the dataset.
        
        Returns:
            List of meter names
        """
        return list(set(task["meter"] for task in self.tasks))
    
    def get_all_topics(self) -> List[str]:
        """
        Get a list of all topics in the dataset.
        
        Returns:
            List of topics
        """
        return list(set(task["topic"] for task in self.tasks))


def generate_dataset(output_path: str, num_tasks: int = 100) -> None:
    """
    Generate a dataset of poetry tasks and save it to a file.
    
    Args:
        output_path: Path to save the dataset
        num_tasks: Number of tasks to generate
    """
    dataset = PoetryDataset()
    
    # Ensure we have enough tasks
    while len(dataset.tasks) < num_tasks:
        dataset._create_default_dataset()
    
    # Trim to the requested number
    dataset.tasks = dataset.tasks[:num_tasks]
    
    # Save the dataset
    dataset.save_dataset(output_path)
