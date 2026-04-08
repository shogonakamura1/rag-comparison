import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    gemini_api_key: str
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k: int = 5
    chroma_persist_dir: str = "./chroma_db"
    collection_name: str = "claude_docs"


def load_config() -> Config:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env file")
    return Config(gemini_api_key=api_key)
