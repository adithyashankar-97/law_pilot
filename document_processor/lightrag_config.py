"""
LightRAG configuration using Google Gemini + Sentence Transformers for GST legal documents
Working configuration based on successful async test
"""

import os
import logging
import numpy as np
from typing import List
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from lightrag.utils import EmbeddingFunc
from lightrag import LightRAG
from lightrag.kg.shared_storage import initialize_pipeline_status

logger = logging.getLogger(__name__)

# Configuration - PUT YOUR API KEY HERE
GOOGLE_API_KEY = "AIzaSyC7PyJd1PWkVT9Wk95GphulPb_ztonEbQI"  # Replace with your actual key
GOOGLE_MODEL = "models/gemma-3-27b-it"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs) -> str:
    """Working Google Gemini LLM function based on successful test"""
    try:
        # Use built-in API key
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Combine prompts
        combined_prompt = ""
        if system_prompt:
            combined_prompt += f"{system_prompt}\n"
        
        for msg in (history_messages or []):
            combined_prompt += f"{msg['role']}: {msg['content']}\n"
        
        combined_prompt += f"user: {prompt}"
        
        # Generate response
        model = genai.GenerativeModel(GOOGLE_MODEL)
        response = model.generate_content(combined_prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Google Gemini API error: {e}")
        raise


async def embedding_func(texts: List[str]) -> np.ndarray:
    """Working Sentence Transformers embedding function"""
    try:
        model = SentenceTransformer(EMBEDDING_MODEL)
        embeddings = model.encode(texts, convert_to_numpy=True)
        return embeddings
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise


async def setup_legal_lightrag(working_dir: str = "./data/lightrag") -> LightRAG:
    """
    Setup LightRAG instance using the working async pattern
    
    Args:
        working_dir: Directory for LightRAG storage
        
    Returns:
        Initialized LightRAG instance
    """
    try:
        os.makedirs(working_dir, exist_ok=True)
        
        # Create LightRAG instance
        rag = LightRAG(
            working_dir=working_dir,
            llm_model_func=llm_model_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=384,
                max_token_size=8192,
                func=embedding_func
            ),
            enable_llm_cache=True,
            llm_model_name=GOOGLE_MODEL,
        )
        
        # Initialize storage
        await rag.initialize_storages()
        await initialize_pipeline_status()
        
        logger.info(f"✅ LightRAG initialized with {GOOGLE_MODEL} + {EMBEDDING_MODEL}")
        return rag
        
    except Exception as e:
        logger.error(f"❌ Failed to setup LightRAG: {e}")
        raise


def test_setup():
    """Simple test function"""
    try:
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(GOOGLE_MODEL)
        response = model.generate_content("Say hello")
        print(f"✅ Google AI test: {response.text}")
        
        model = SentenceTransformer(EMBEDDING_MODEL)
        embeddings = model.encode(["Test"])
        print(f"✅ Embeddings test: {embeddings.shape[1]} dimensions")
        
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing LightRAG configuration...")
    success = test_setup()
    if success:
        print("🎉 Configuration ready!")
    else:
        print("❌ Configuration needs fixing")