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
        fallback_models: Optional[list[str]] = None,
        timeout: int = 120
    ):
        """
        Initialize Ollama LLM
        
        Args:
            base_url: Ollama server base URL
            model: Model name (llama2, mistral, etc.)
            fallback_models: Ordered fallback model names
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.fallback_models = [m for m in (fallback_models or []) if m and m != model]
        self.timeout = timeout
        
        self._verify_connection()

    @staticmethod
    def _should_try_fallback(status_code: int, error_detail: str) -> bool:
        """Decide whether a failed generation should try fallback models."""
        text = (error_detail or "").lower()

        model_or_memory_issues = [
            "not found",
            "no such model",
            "unknown model",
            "out of memory",
            "insufficient memory",
            "requires more system memory",
            "timed out",
        ]

        if status_code == 404:
            return True

        return any(marker in text for marker in model_or_memory_issues)
    
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
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"

        models_to_try = [self.model] + [m for m in self.fallback_models if m != self.model]
        logger.debug(f"Generating with model chain: {models_to_try}")

        last_error = "Error: Failed to generate response"

        for index, model_name in enumerate(models_to_try):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": full_prompt,
                        "stream": False,
                        "temperature": temperature,
                    },
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    result = response.json()
                    generated_text = result.get("response", "").strip()
                    if model_name != self.model:
                        logger.warning(f"Switched active Ollama model to fallback: {model_name}")
                        self.model = model_name
                    logger.debug(f"Generated {len(generated_text)} characters")
                    return generated_text

                error_detail = _extract_ollama_error(response)
                logger.error(
                    f"Ollama error ({model_name}): {response.status_code}"
                    + (f" - {error_detail}" if error_detail else "")
                )

                if error_detail:
                    last_error = f"Error: Ollama returned status {response.status_code}. {error_detail}"
                else:
                    last_error = f"Error: Received status {response.status_code} from Ollama"

                has_next_model = index < len(models_to_try) - 1
                if has_next_model and self._should_try_fallback(response.status_code, error_detail):
                    logger.warning(f"Trying fallback model after failure on {model_name}")
                    continue

                return last_error

            except requests.exceptions.Timeout:
                logger.error(f"Ollama request timed out ({model_name})")
                last_error = "Error: Request timed out. Please try again."

                has_next_model = index < len(models_to_try) - 1
                if has_next_model:
                    logger.warning(f"Trying fallback model after timeout on {model_name}")
                    continue

                return last_error

            except requests.exceptions.RequestException as e:
                logger.error(f"Ollama request failed ({model_name}): {e}")
                return "Error: Failed to connect to Ollama. Is it running?"

        return last_error
    
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
        except requests.exceptions.RequestException:
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
