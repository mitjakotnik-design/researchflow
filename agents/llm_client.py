"""LLM client wrapper for Gemini and Claude models."""

import os
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional, AsyncIterator

import structlog


logger = structlog.get_logger()


class LLMProvider(Enum):
    """LLM provider types."""
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    
    content: str
    model: str
    provider: LLMProvider
    
    # Token usage
    input_tokens: int = 0
    output_tokens: int = 0
    
    # Timing
    latency_ms: int = 0
    
    # Metadata
    finish_reason: str = ""
    raw_response: Optional[Any] = None


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, model: str, temperature: float = 0.7):
        self.model = model
        self.temperature = temperature
        self.log = structlog.get_logger().bind(llm_model=model)
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        json_mode: bool = False,
        stop_sequences: Optional[list[str]] = None
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> AsyncIterator[str]:
        """Stream a response from the LLM."""
        pass


class GeminiClient(BaseLLMClient):
    """Client for Google Gemini models."""
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        api_key: Optional[str] = None
    ):
        super().__init__(model, temperature)
        
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError(
                "google-generativeai not installed. "
                "Run: pip install google-generativeai"
            )
        
        self.genai = genai
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")
        
        genai.configure(api_key=api_key)
        
        self.client = genai.GenerativeModel(
            model_name=model,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            )
        )
        
        self.log.info("gemini_client_initialized", model=model)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        json_mode: bool = False,
        stop_sequences: Optional[list[str]] = None
    ) -> LLMResponse:
        """Generate a response using Gemini."""
        import time
        
        start_time = time.perf_counter()
        
        # Build content
        contents = []
        
        if system_prompt:
            contents.append({"role": "user", "parts": [system_prompt]})
            contents.append({"role": "model", "parts": ["Understood. I will follow these instructions."]})
        
        contents.append({"role": "user", "parts": [prompt]})
        
        # Configure generation
        generation_config = self.genai.types.GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=max_tokens,
            stop_sequences=stop_sequences,
        )
        
        if json_mode:
            generation_config.response_mime_type = "application/json"
        
        try:
            # Run in thread pool since Gemini SDK is sync
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.generate_content(
                    contents,
                    generation_config=generation_config
                )
            )
            
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            
            # Extract token counts if available
            input_tokens = 0
            output_tokens = 0
            if hasattr(response, "usage_metadata"):
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)
            
            content = response.text if hasattr(response, "text") else ""
            
            self.log.debug(
                "gemini_response",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms
            )
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider=LLMProvider.GEMINI,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                finish_reason=str(response.candidates[0].finish_reason) if response.candidates else "",
                raw_response=response
            )
            
        except Exception as e:
            self.log.error("gemini_error", error=str(e))
            raise
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> AsyncIterator[str]:
        """Stream a response using Gemini."""
        contents = []
        
        if system_prompt:
            contents.append({"role": "user", "parts": [system_prompt]})
            contents.append({"role": "model", "parts": ["Understood."]})
        
        contents.append({"role": "user", "parts": [prompt]})
        
        generation_config = self.genai.types.GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=max_tokens,
        )
        
        # Get streaming response
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.generate_content(
                contents,
                generation_config=generation_config,
                stream=True
            )
        )
        
        for chunk in response:
            if hasattr(chunk, "text"):
                yield chunk.text


class VertexAIClient(BaseLLMClient):
    """Client for Vertex AI Gemini models using Application Default Credentials."""
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        project: Optional[str] = None,
        location: str = "us-central1"
    ):
        super().__init__(model, temperature)
        
        try:
            import vertexai
            from vertexai.generative_models import GenerativeModel, GenerationConfig
        except ImportError:
            raise ImportError(
                "google-cloud-aiplatform not installed. "
                "Run: pip install google-cloud-aiplatform"
            )
        
        self.project = project or os.getenv("GCP_PROJECT")
        self.location = location
        
        if not self.project:
            raise ValueError("GCP_PROJECT not set")
        
        # Initialize Vertex AI with ADC
        vertexai.init(project=self.project, location=self.location)
        
        self.GenerationConfig = GenerationConfig
        self.client = GenerativeModel(model)
        
        self.log.info("vertex_ai_client_initialized", 
                      model=model, project=self.project, location=location)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        json_mode: bool = False,
        stop_sequences: Optional[list[str]] = None
    ) -> LLMResponse:
        """Generate a response using Vertex AI Gemini."""
        import time
        
        start_time = time.perf_counter()
        
        contents = []
        
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": system_prompt}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        generation_config = self.GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=max_tokens,
            stop_sequences=stop_sequences,
        )
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.generate_content(
                    contents,
                    generation_config=generation_config
                )
            )
            
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            
            input_tokens = 0
            output_tokens = 0
            if hasattr(response, "usage_metadata"):
                input_tokens = getattr(response.usage_metadata, "prompt_token_count", 0)
                output_tokens = getattr(response.usage_metadata, "candidates_token_count", 0)
            
            content = response.text if hasattr(response, "text") else ""
            
            self.log.debug(
                "vertex_ai_response",
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms
            )
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider=LLMProvider.GEMINI,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                finish_reason=str(response.candidates[0].finish_reason) if response.candidates else "",
                raw_response=response
            )
            
        except Exception as e:
            self.log.error("vertex_ai_error", error=str(e))
            raise
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> AsyncIterator[str]:
        """Stream a response using Vertex AI."""
        contents = []
        
        if system_prompt:
            contents.append({"role": "user", "parts": [{"text": system_prompt}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        
        contents.append({"role": "user", "parts": [{"text": prompt}]})
        
        generation_config = self.GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=max_tokens,
        )
        
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.client.generate_content(
                contents,
                generation_config=generation_config,
                stream=True
            )
        )
        
        for chunk in response:
            if hasattr(chunk, "text"):
                yield chunk.text


class AnthropicClient(BaseLLMClient):
    """Client for Anthropic Claude models."""
    
    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        temperature: float = 0.7,
        api_key: Optional[str] = None
    ):
        super().__init__(model, temperature)
        
        try:
            import anthropic
        except ImportError:
            raise ImportError(
                "anthropic not installed. Run: pip install anthropic"
            )
        
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
        
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.log.info("anthropic_client_initialized", model=model)
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096,
        json_mode: bool = False,
        stop_sequences: Optional[list[str]] = None
    ) -> LLMResponse:
        """Generate a response using Claude."""
        import time
        
        start_time = time.perf_counter()
        
        messages = [{"role": "user", "content": prompt}]
        
        # Add JSON instruction if needed
        actual_prompt = prompt
        if json_mode:
            actual_prompt = f"{prompt}\n\nRespond with valid JSON only."
            messages = [{"role": "user", "content": actual_prompt}]
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=self.temperature,
                system=system_prompt or "",
                messages=messages,
                stop_sequences=stop_sequences or []
            )
            
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            
            content = response.content[0].text if response.content else ""
            
            self.log.debug(
                "anthropic_response",
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                latency_ms=latency_ms
            )
            
            return LLMResponse(
                content=content,
                model=self.model,
                provider=LLMProvider.ANTHROPIC,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                latency_ms=latency_ms,
                finish_reason=response.stop_reason or "",
                raw_response=response
            )
            
        except Exception as e:
            self.log.error("anthropic_error", error=str(e))
            raise
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 4096
    ) -> AsyncIterator[str]:
        """Stream a response using Claude."""
        messages = [{"role": "user", "content": prompt}]
        
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=max_tokens,
            temperature=self.temperature,
            system=system_prompt or "",
            messages=messages
        ) as stream:
            async for text in stream.text_stream:
                yield text


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create(model_name: str, temperature: float = 0.7) -> BaseLLMClient:
        """Create appropriate LLM client based on model name."""
        
        if model_name.startswith("gemini"):
            # Check if we should use Vertex AI
            use_vertex_ai = os.getenv("USE_VERTEX_AI", "false").lower() == "true"
            
            if use_vertex_ai:
                return VertexAIClient(
                    model=model_name, 
                    temperature=temperature,
                    project=os.getenv("GCP_PROJECT"),
                    location=os.getenv("GCP_LOCATION", "us-central1")
                )
            else:
                return GeminiClient(model=model_name, temperature=temperature)
        
        elif model_name.startswith("claude"):
            return AnthropicClient(model=model_name, temperature=temperature)
        
        else:
            raise ValueError(f"Unknown model: {model_name}")
    
    @staticmethod
    def get_provider(model_name: str) -> LLMProvider:
        """Get provider for a model name."""
        if model_name.startswith("gemini"):
            return LLMProvider.GEMINI
        elif model_name.startswith("claude"):
            return LLMProvider.ANTHROPIC
        else:
            raise ValueError(f"Unknown model: {model_name}")
