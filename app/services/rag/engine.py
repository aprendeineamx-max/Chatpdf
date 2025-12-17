import logging
import os
from typing import Optional, List, Dict, Any

# Mock or Real dependencies
try:
    from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
except ImportError:
    VectorStoreIndex = None

class RAGService:
    def __init__(self):
        self.logger = logging.getLogger("rag_engine")
        self.logger.setLevel(logging.INFO)
        # Initialize basic index if needed
        # For now, we rely on the Agentic 'Live Read' mostly
        pass

    def query(self, query_text: str, pdf_id: str = "all", model: Optional[str] = None, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Standard Query.
        For Agentic actions, the Agent Logic in main.py handles the context injection.
        This service just needs to return the LLM response.
        """
        prompt = query_text
        
        used_provider = "unknown"
        used_model = model or "unknown"
        
        # Call LLM with routing
        try:
            response_text, used_provider, used_model = self._call_llm(prompt, model, provider)
        except Exception as e:
            print(f"CRITICAL LLM ERROR: {e}") # DEBUG
            response_text = f"LLM Integration Error: {e}"
            
        return {
            "answer": response_text, 
            "sources": [], 
            "metadata": {
                "provider": used_provider,
                "model": used_model
            }
        }

    async def query_swarm(self, query_text: str, pdf_id: str = "all", model: Optional[str] = None):
         return self.query(query_text, pdf_id, model)

    def _call_llm(self, prompt: str, model: Optional[str], provider: Optional[str] = None) -> (str, str, str):
        from app.core.config import settings
        
        model_id = (model or "").lower()
        provider_id = (provider or "").lower()
        
        # 1. EXPLICIT PROVIDER OVERRIDE (User Control)
        if "sambanova" in provider_id:
            if settings.SAMBANOVA_API_KEY:
                # Use default good model if none provided
                final_model = model_id if model_id else "Meta-Llama-3.3-70B-Instruct" 
                return self._call_sambanova(settings.SAMBANOVA_API_KEY, prompt, final_model), "Sambanova", final_model
            else:
                raise Exception("Sambanova selected but no API Key.")
                
        if "groq" in provider_id:
            if settings.GROQ_API_KEY:
                 final_model = model_id if model_id else "llama3-8b-8192"
                 return self._call_groq(settings.GROQ_API_KEY, prompt, final_model), "Groq", final_model
            else:
                 raise Exception("Groq selected but no API Key.")
                 
        if "google" in provider_id or "gemini" in provider_id:
             if settings.GOOGLE_API_KEY:
                  return self._call_gemini(settings.GOOGLE_API_KEY, prompt), "Gemini", "gemini-pro"


        # 2. AUTO-ROUTING (If provider is None or 'auto')
        
        # PRIORITY 1: Llama/DeepSeek Models
        if "llama" in model_id or "deepseek" in model_id:
            # Try Groq first 
            if settings.GROQ_API_KEY:
                try:
                    return self._call_groq(settings.GROQ_API_KEY, prompt, model_id), "Groq", model_id
                except Exception as e:
                    print(f"DEBUG: Groq failed ({e}). Checking Sambanova fallback...")
            
            # Fallback to Sambanova
            if settings.SAMBANOVA_API_KEY:
                 return self._call_sambanova(settings.SAMBANOVA_API_KEY, prompt, model_id), "Sambanova", model_id
            
            return "Error: Requested model failed and no working fallback (Sambanova) found.", "Error", model_id

        # PRIORITY 2: Gemini Models
        if "gemini" in model_id:
             if settings.GOOGLE_API_KEY:
                  return self._call_gemini(settings.GOOGLE_API_KEY, prompt), "Gemini", "gemini-pro"

        # PRIORITY 3: Smart Default (Universal Logic)
        if settings.GROQ_API_KEY:
            try:
                return self._call_groq(settings.GROQ_API_KEY, prompt, "llama3-8b-8192"), "Groq", "llama3-8b-8192"
            except Exception as e:
                print(f"DEBUG: Smart Default Groq failed ({e})...")
                
        if settings.SAMBANOVA_API_KEY:
             return self._call_sambanova(settings.SAMBANOVA_API_KEY, prompt, "Meta-Llama-3.3-70B-Instruct"), "Sambanova", "Meta-Llama-3.3-70B-Instruct"
             
        # Last resort: Gemini
        if settings.GOOGLE_API_KEY:
             return self._call_gemini(settings.GOOGLE_API_KEY, prompt), "Gemini", "gemini-pro"

        return "Error: No suitable API Key found for model execution.", "None", "None"

    def _call_gemini(self, key: str, prompt: str) -> str:
        import requests
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={key}"
        data = {"contents": [{"parts": [{"text": prompt}]}]}
        try:
            r = requests.post(url, json=data)
            r.raise_for_status()
            return r.json()['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            raise Exception(f"Gemini Error: {e}")

    def _call_groq(self, key: str, prompt: str, model_id: str = "llama3-8b-8192") -> str:
        import requests
        
        # Fallback if specific model is weird string
        final_model = model_id if "llama" in model_id else "llama3-8b-8192"
        
        # Mapping
        if "70b" in model_id:
            final_model = "llama-3.3-70b-versatile"
        elif "8b" in model_id:
            final_model = "llama3-8b-8192"
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "model": final_model
        }
        try:
            r = requests.post(url, headers=headers, json=data)
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content']
        except Exception as e:
            raise Exception(f"Groq Error: {e}")

    def _call_sambanova(self, key: str, prompt: str, model_id: str) -> str:
        import requests
        # Mapping
        final_model = "Meta-Llama-3.3-70B-Instruct" 
        if "8b" in model_id.lower():
             final_model = "Meta-Llama-3.1-8B-Instruct"
        elif "70b" in model_id.lower():
             final_model = "Meta-Llama-3.3-70B-Instruct"
             
        url = "https://api.sambanova.ai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "model": final_model
        }
        try:
            r = requests.post(url, headers=headers, json=data)
            r.raise_for_status()
            return r.json()['choices'][0]['message']['content']
        except Exception as e:
            raise Exception(f"Sambanova Error: {e}")

rag_service = RAGService()
