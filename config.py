"""
Configuration and constants for ACDGE Cognitive Architecture Engine
Architectural Choice: Centralized configuration with environment-aware settings
to enable seamless deployment across development, staging, and production
"""
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
from loguru import logger
import json

@dataclass
class FirebaseConfig:
    """Firebase configuration with validation"""
    project_id: str
    credential_path: Optional[str] = None
    database_url: Optional[str] = None
    
    def __post_init__(self):
        if not self.project_id:
            raise ValueError("Firebase project_id is required")
        if self.credential_path and not Path(self.credential_path).exists():
            logger.warning(f"Firebase credential path {self.credential_path} not found")

@dataclass
class ModelConfig:
    """ML model configuration with type safety"""
    embedding_dimension: int = 768
    topic_model_components: int = 50
    cluster_algorithm: str = "dbscan"  # Options: dbscan, kmeans, hierarchical
    min_cluster_size: int = 5
    graph_node_threshold: int = 1000
    
    def validate(self):
        valid_algorithms = ["dbscan", "kmeans", "hierarchical"]
        if self.cluster_algorithm not in valid_algorithms:
            raise ValueError(f"Invalid cluster algorithm. Must be one of: {valid_algorithms}")

class ACDGEConfig:
    """Main configuration manager with singleton pattern"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ACDGEConfig, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize configuration with environment variables and defaults"""
        # Firebase configuration
        self.firebase = FirebaseConfig(
            project_id=os.getenv("FIREBASE_PROJECT_ID", "acdge-development"),
            credential_path=os.getenv("FIREBASE_CREDENTIAL_PATH"),
            database_url=os.getenv("FIREBASE_DATABASE_URL")
        )
        
        # Model configuration
        self.models = ModelConfig()
        self.models.validate()
        
        # Path configuration
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.models_dir = self.base_dir / "models"
        self.logs_dir = self.base_dir / "logs"
        
        # Create necessary directories
        for directory in [self.data_dir, self.models_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
        
        # Feature flags
        self.enable_real_time_updates = os.getenv("ENABLE_REAL_TIME_UPDATES", "false").lower() == "true"
        self.enable_cross_domain_analogies = os.getenv("ENABLE_CROSS_DOMAIN_ANALOGIES", "true").lower() == "true"
        
        logger.info(f"ACDGE Configuration initialized. Project: {self.firebase.project_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize configuration to dictionary"""
        return {
            "firebase": {
                "project_id": self.firebase.project_id,
                "has_credential": bool(self.firebase.credential_path)
            },
            "models": {
                "embedding_dimension": self.models.embedding_dimension,
                "topic_model_components": self.models.topic_model_components,
                "cluster_algorithm": self.models.cluster_algorithm
            },
            "paths": {
                "base_dir": str(self.base_dir),
                "data_dir": str(self.data_dir)
            }
        }

# Global configuration instance
config = ACDGEConfig()