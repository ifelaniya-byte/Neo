"""
LLM Client - External LLM Integration (Phase 1A)

Provides interface to external LLM APIs (OpenAI, Anthropic, or local models).
This is the foundation for adding general intelligence to the system.
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class LLMResponse:
    """Response from LLM API."""
    content: str
    model: str
    tokens_used: int
    cost_usd: float
    latency_ms: int
    finish_reason: str


class LLMClient:
    """
    Client for interacting with external LLM APIs.
    
    Supports:
    - OpenAI GPT models
    - Anthropic Claude models
    - Local models (via local API)
    - Cost tracking
    - Token budgeting
    """
    
    def __init__(self, provider: LLMProvider, api_key: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider (openai, anthropic, local)
            api_key: API key for the provider
            config: Additional configuration
        """
        self.provider = provider
        self.api_key = api_key or os.getenv(f"{provider.value.upper()}_API_KEY")
        self.config = config or {}
        
        # Cost tracking
        self.cost_per_1k_tokens = {
            LLMProvider.OPENAI: 0.002,  # GPT-4 approximate
            LLMProvider.ANTHROPIC: 0.003,  # Claude approximate
            LLMProvider.LOCAL: 0.0,  # Local is free
        }
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "total_latency_ms": 0.0,
        }
        
        # Initialize client based on provider
        self._init_client()
    
    def _init_client(self):
        """Initialize the specific client for the provider."""
        if self.provider == LLMProvider.OPENAI:
            try:
                import openai
                self.client = openai.OpenAI(api_key=self.api_key)
                self.model = self.config.get("model", "gpt-4")
            except ImportError:
                self.client = None
                print("Warning: openai package not installed")
        
        elif self.provider == LLMProvider.ANTHROPIC:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.model = self.config.get("model", "claude-3-opus-20240229")
            except ImportError:
                self.client = None
                print("Warning: anthropic package not installed")
        
        elif self.provider == LLMProvider.LOCAL:
            # For local models, we'd use a local inference server
            # For v0.1, we'll use a stub
            self.client = None
            self.model = self.config.get("model", "local-model")
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """
        Generate response from LLM.
        
        Args:
            prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            system_prompt: Optional system prompt
            
        Returns:
            LLMResponse with content and metadata
        """
        import time
        start_time = time.time()
        self.metrics["total_requests"] += 1
        
        # If no client available, return stub response
        if self.client is None:
            latency_ms = int((time.time() - start_time) * 1000)
            return LLMResponse(
                content=f"[LLM not available - {self.provider.value} client not initialized]",
                model=self.model,
                tokens_used=0,
                cost_usd=0.0,
                latency_ms=latency_ms,
                finish_reason="error"
            )
        
        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt or "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                
                content = response.choices[0].message.content
                tokens_used = response.usage.total_tokens
                cost_usd = (tokens_used / 1000) * self.cost_per_1k_tokens[self.provider]
                latency_ms = int((time.time() - start_time) * 1000)
                
                self.metrics["total_tokens"] += tokens_used
                self.metrics["total_cost_usd"] += cost_usd
                self.metrics["total_latency_ms"] += latency_ms
                
                return LLMResponse(
                    content=content,
                    model=self.model,
                    tokens_used=tokens_used,
                    cost_usd=cost_usd,
                    latency_ms=latency_ms,
                    finish_reason=response.choices[0].finish_reason
                )
            
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    system=system_prompt or "You are a helpful assistant.",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                content = response.content[0].text
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
                cost_usd = (tokens_used / 1000) * self.cost_per_1k_tokens[self.provider]
                latency_ms = int((time.time() - start_time) * 1000)
                
                self.metrics["total_tokens"] += tokens_used
                self.metrics["total_cost_usd"] += cost_usd
                self.metrics["total_latency_ms"] += latency_ms
                
                return LLMResponse(
                    content=content,
                    model=self.model,
                    tokens_used=tokens_used,
                    cost_usd=cost_usd,
                    latency_ms=latency_ms,
                    finish_reason="stop"
                )
        
        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            return LLMResponse(
                content=f"Error: {str(e)}",
                model=self.model,
                tokens_used=0,
                cost_usd=0.0,
                latency_ms=latency_ms,
                finish_reason="error"
            )
    
    def classify_intent(self, text: str) -> Dict[str, float]:
        """
        Classify intent using LLM.
        
        Args:
            text: Input text to classify
            
        Returns:
            Dictionary of intent classes with probabilities
        """
        prompt = f"""Classify the intent of this text. Return probabilities for each category:
- arithmetic: mathematical calculations
- knowledge: factual questions
- code: programming tasks
- planning: planning tasks
- unknown: unclear intent

Text: {text}

Return as JSON: {{"arithmetic": 0.0, "knowledge": 0.0, "code": 0.0, "planning": 0.0, "unknown": 0.0}}"""
        
        response = self.generate(prompt, max_tokens=200, temperature=0.3)
        
        # Parse JSON from response
        try:
            import json
            content = response.content.strip()
            # Extract JSON from response
            if "{" in content and "}" in content:
                start = content.index("{")
                end = content.rindex("}") + 1
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: uniform distribution
        return {"arithmetic": 0.2, "knowledge": 0.2, "code": 0.2, "planning": 0.2, "unknown": 0.2}
    
    def verify_reasoning(self, reasoning: str, question: str) -> bool:
        """
        Verify reasoning using LLM.
        
        Args:
            reasoning: The reasoning to verify
            question: The original question
            
        Returns:
            True if reasoning is sound, False otherwise
        """
        prompt = f"""Verify if this reasoning is sound for the question.

Question: {question}
Reasoning: {reasoning}

Respond with only "true" if the reasoning is sound, or "false" if it contains errors or hallucinations."""
        
        response = self.generate(prompt, max_tokens=10, temperature=0.1)
        
        return "true" in response.content.lower()
    
    def estimate_uncertainty(self, prediction: str, confidence: float) -> float:
        """
        Estimate uncertainty using LLM.
        
        Args:
            prediction: The prediction made
            confidence: Stated confidence level
            
        Returns:
            Adjusted uncertainty score (0-1)
        """
        prompt = f"""Estimate the actual uncertainty of this prediction.

Prediction: {prediction}
Stated confidence: {confidence}

Respond with a number between 0 and 1 representing the true uncertainty (0 = certain, 1 = completely uncertain)."""
        
        response = self.generate(prompt, max_tokens=10, temperature=0.1)
        
        try:
            uncertainty = float(response.content.strip())
            return max(0.0, min(1.0, uncertainty))
        except:
            return 1.0 - confidence  # Fallback
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get LLM usage metrics."""
        return self.metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.metrics = {
            "total_requests": 0,
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "total_latency_ms": 0.0,
        }
