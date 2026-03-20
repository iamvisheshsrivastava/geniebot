"""
LLM interface for GenieBot using Ollama
Handles communication with local LLM inference
"""

import requests
from typing import Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _extract_ollama_error(response: requests.Response) -> str:
    """Extract the most useful Ollama error text from a failed response."""
    try:
        payload = response.json()
        if isinstance(payload, dict):
            return str(payload.get("error") or payload.get("message") or "").strip()
    except Exception:
        pass

    text = (response.text or "").strip()
    return text[:500]


class OllamaLLM:
    """Interface to Ollama local LLM"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama2",
        timeout: int = 120
    ):
        """
        Initialize Ollama LLM
        
        Args:
            base_url: Ollama server base URL
            model: Model name (llama2, mistral, etc.)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        
        self._verify_connection()
    
    def _verify_connection(self) -> None:
        """Verify connection to Ollama server"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                logger.info(f"Connected to Ollama at {self.base_url}")
            else:
                logger.warning(f"Ollama connection returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Cannot connect to Ollama at {self.base_url}: {e}")
            logger.info("Make sure Ollama is running: ollama serve")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate text using Ollama
        
        Args:
            prompt: Input prompt
            system_prompt: Optional system instructions
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate
        
        Returns:
            Generated text
        """
        logger.debug(f"Generating with model: {self.model}")
        
        # Build full prompt with system instructions
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": temperature,
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                logger.debug(f"Generated {len(generated_text)} characters")
                return generated_text
            else:
                error_detail = _extract_ollama_error(response)
                logger.error(
                    f"Ollama error: {response.status_code}"
                    + (f" - {error_detail}" if error_detail else "")
                )
                if error_detail:
                    return f"Error: Ollama returned status {response.status_code}. {error_detail}"
                return f"Error: Received status {response.status_code} from Ollama"
        
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return "Error: Request timed out. Please try again."
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            return f"Error: Failed to connect to Ollama. Is it running?"
    
    def chat(
        self,
        messages: list,
        temperature: float = 0.7
    ) -> str:
        """
        Chat-style generation using Ollama
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
        
        Returns:
            Generated response
        """
        logger.debug("Chat generation")
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "temperature": temperature,
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                message = result.get("message", {})
                generated_text = message.get("content", "").strip()
                return generated_text
            else:
                error_detail = _extract_ollama_error(response)
                logger.error(
                    f"Chat error: {response.status_code}"
                    + (f" - {error_detail}" if error_detail else "")
                )
                if error_detail:
                    return f"Error: Ollama returned status {response.status_code}. {error_detail}"
                return f"Error: Ollama returned status {response.status_code}"
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Chat request failed: {e}")
            return "Error: Failed to communicate with Ollama"
    
    def is_available(self) -> bool:
        """Check if Ollama is available"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                models = [m.get("name", "") for m in data.get("models", [])]
                logger.debug(f"Available models: {models}")
                return models
            return []
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []
