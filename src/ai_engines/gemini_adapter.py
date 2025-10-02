"""
Google Gemini AI Engine Adapter
Implements converSQL adapter interface for Google Gemini.
"""

import os
from typing import Any, Dict, Optional, Tuple, cast

from .base import AIEngineAdapter


class GeminiAdapter(AIEngineAdapter):
    """
    Google Gemini AI engine adapter.

    Supports Gemini Pro and other models through Google's Generative AI API.
    Requires GOOGLE_API_KEY environment variable.
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Gemini adapter.

        Args:
            config: Configuration dict with keys:
                - api_key: Google API key (default from env)
                - model: Model name (default 'gemini-1.5-pro')
                - max_tokens: Maximum response tokens
                - temperature: Temperature for generation (0.0-1.0)
        """
        self.client: Optional[Any] = None
        self.model: Optional[Any] = None
        self.api_key: Optional[str] = None
        self.max_output_tokens: int = 4000
        self.temperature: float = 0.0
        super().__init__(config)

    def _initialize(self) -> None:
        """Initialize Gemini client with Google Generative AI SDK."""
        # Get configuration
        self.api_key = self.config.get("api_key", os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY"))
        model_name = self.config.get("model", os.getenv("GEMINI_MODEL", "gemini-1.5-pro"))
        if not isinstance(model_name, str) or not model_name.strip():
            model_name = "gemini-1.5-pro"
        max_output_tokens = self.config.get("max_output_tokens", 4000)
        try:
            parsed_max_tokens = int(max_output_tokens)
            self.max_output_tokens = parsed_max_tokens if parsed_max_tokens > 0 else 4000
        except (TypeError, ValueError):
            self.max_output_tokens = 4000

        temperature_config = self.config.get("temperature", 0.0)
        try:
            parsed_temperature = float(temperature_config)
            self.temperature = parsed_temperature if 0.0 <= parsed_temperature <= 1.0 else 0.0
        except (TypeError, ValueError):
            self.temperature = 0.0

        if not self.api_key:
            return

        try:
            import importlib

            genai = cast(Any, importlib.import_module("google.generativeai"))

            # Configure API key
            genai.configure(api_key=self.api_key)

            # Initialize model with generation config
            generation_config: Dict[str, Any] = {
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens,
                "top_p": 0.95,
                "top_k": 40,
            }

            model_instance = cast(
                Any, genai.GenerativeModel(model_name=str(model_name), generation_config=cast(Any, generation_config))
            )
            self.model = model_instance

            # Optional: Test with minimal request to verify model initialization
            try:
                model_instance.generate_content("test")
                # If we get here, the model is working
            except Exception:
                # Keep model - might work for actual requests
                pass

        except ImportError:
            print("⚠️ google-generativeai package not installed.")
            print("   Run: pip install google-generativeai")
            self.model = None
        except Exception as e:
            print(f"⚠️ Gemini initialization failed: {e}")
            print("   Check GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
            self.model = None

    def is_available(self) -> bool:
        """Check if Gemini client is initialized and ready."""
        return self.model is not None and self.api_key is not None

    def generate_sql(self, prompt: str) -> Tuple[str, str]:
        """
        Generate SQL using Google Gemini.

        Args:
            prompt: Complete prompt with schema and question

        Returns:
            Tuple[str, str]: (sql_query, error_message)
        """
        if not self.is_available():
            return "", "Gemini not available. Check GOOGLE_API_KEY configuration."

        try:
            # Generate content
            model = self.model
            if model is None:
                return "", "Gemini not available. Check GOOGLE_API_KEY configuration."

            response = model.generate_content(prompt)

            # Extract text from response
            if response.text:
                raw_sql = response.text
                sql_query = self.clean_sql_response(raw_sql)

                # Validate response
                is_valid, validation_msg = self.validate_response(sql_query)
                if not is_valid:
                    return "", f"Invalid SQL generated: {validation_msg}"

                return sql_query, ""
            else:
                # Check for safety ratings that blocked the response
                if hasattr(response, "prompt_feedback"):
                    feedback = response.prompt_feedback
                    if hasattr(feedback, "block_reason"):
                        return "", f"Response blocked: {feedback.block_reason}"

                return "", "Gemini returned empty response"

        except Exception as e:
            error_msg = f"Gemini API error: {str(e)}"

            # Provide helpful error messages for common issues
            error_lower = str(e).lower()
            if "api key" in error_lower or "api_key" in error_lower:
                error_msg += "\nCheck GOOGLE_API_KEY or GEMINI_API_KEY environment variable"
            elif "quota" in error_lower or "rate limit" in error_lower:
                error_msg += "\nAPI quota exceeded or rate limited"
            elif "safety" in error_lower or "blocked" in error_lower:
                error_msg += "\nContent was blocked by safety filters"
            elif "model" in error_lower:
                error_msg += "\nModel may not be available or accessible"

            return "", error_msg

    @property
    def name(self) -> str:
        """Display name for this engine."""
        return "Google Gemini"

    @property
    def provider_id(self) -> str:
        """Unique provider identifier."""
        return "gemini"

    def get_model_info(self) -> Dict[str, Any]:
        """Get Gemini model configuration details."""
        model_name = self.model.model_name if self.model and hasattr(self.model, "model_name") else "gemini-1.5-pro"

        return {
            "provider": "Google Gemini",
            "model": model_name,
            "max_output_tokens": self.max_output_tokens,
            "temperature": self.temperature,
            "top_p": 0.95,
            "top_k": 40,
            "capabilities": [
                "SQL generation",
                "Natural language understanding",
                "Schema comprehension",
                "Multi-turn conversation",
                "Safety filtering",
            ],
        }

    def set_safety_settings(self, safety_settings: Dict[str, Any]) -> None:
        """
        Update safety settings for content generation.

        Args:
            safety_settings: Dictionary of safety settings
            Example:
                {
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_MEDIUM_AND_ABOVE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_MEDIUM_AND_ABOVE',
                }
        """
        model = self.model
        if model is None:
            print("⚠️ Cannot set safety settings: Model not initialized")
            return

        try:
            import importlib

            genai = cast(Any, importlib.import_module("google.generativeai"))

            # Reconstruct model with new safety settings
            generation_config: Dict[str, Any] = {
                "temperature": self.temperature,
                "max_output_tokens": self.max_output_tokens,
                "top_p": 0.95,
                "top_k": 40,
            }

            model_name = model.model_name if hasattr(model, "model_name") else "gemini-1.5-pro"

            self.model = cast(
                Any,
                genai.GenerativeModel(
                    model_name=str(model_name),
                    generation_config=cast(Any, generation_config),
                    safety_settings=safety_settings,
                ),
            )

        except Exception as e:
            print(f"⚠️ Failed to update safety settings: {e}")
