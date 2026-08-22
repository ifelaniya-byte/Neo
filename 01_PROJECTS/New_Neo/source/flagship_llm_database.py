"""
PROJECT APEX: FLAGSHIP LLM BENCHMARK DATABASE
Comprehensive database of flagship LLM stats, weights, and performance metrics.
Enables micro-LLM to compare itself against 700B+ models.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import json

class ModelArchitecture(Enum):
    """Types of model architectures."""
    TRANSFORMER = "TRANSFORMER"
    DENSE_MIXER = "DENSE_MIXER"
    MIXTURE_OF_EXPERTS = "MIXTURE_OF_EXPERTS"
    STATE_SPACE = "STATE_SPACE"
    RECURRENT = "RECURRENT"
    HYBRID = "HYBRID"

class ModelSize(Enum):
    """Size categories of models."""
    NANO = "NANO"               # <1B parameters
    TINY = "TINY"               # 1-3B parameters
    SMALL = "SMALL"             # 3-7B parameters
    MEDIUM = "MEDIUM"           # 7-13B parameters
    LARGE = "LARGE"             # 13-70B parameters
    MASSIVE = "MASSIVE"         # 70-400B parameters
    FLAGSHIP = "FLAGSHIP"       # 400B+ parameters

class BenchmarkCategory(Enum):
    """Categories of benchmarks."""
    REASONING = "REASONING"
    CODING = "CODING"
    MATH = "MATH"
    LANGUAGE = "LANGUAGE"
    KNOWLEDGE = "KNOWLEDGE"
    MULTILINGUAL = "MULTILINGUAL"
    SAFETY = "SAFETY"
    EFFICIENCY = "EFFICIENCY"

@dataclass
class ModelWeights:
    """Weight and parameter information."""
    total_parameters: int
    trainable_parameters: int
    embedding_parameters: int
    attention_parameters: int
    feedforward_parameters: int
    moe_parameters: int  # If mixture of experts
    quantization_bits: int  # Current quantization level
    fp16_equivalent: int  # FP16 equivalent parameters
    effective_parameters: int  # After quantization/sparsification
    
    def to_dict(self):
        return self.__dict__

@dataclass
class ModelPerformance:
    """Performance metrics across benchmarks."""
    mmlu_score: float  # Massive Multitask Language Understanding
    mmlu_pro_score: float  # MMLU Pro
    human_eval_score: float  # Python coding
    math_score: float  # Mathematical reasoning
    gsm8k_score: float  # Grade school math
    hellaswag_score: float  # Common sense reasoning
    arc_challenge_score: float  # Science reasoning
    truthfulqa_score: float  # Truthfulness
    winogrande_score: float  # Commonsense reasoning
    gpt4_benchmark: float  # Overall GPT-4 benchmark score
    claude_benchmark: float  # Overall Claude benchmark score
    custom_benchmark: float  # Custom benchmark score
    
    def to_dict(self):
        return self.__dict__

@dataclass
class ModelEfficiency:
    """Efficiency metrics."""
    parameters_per_billion: float
    flops_per_token: float
    tokens_per_second: float
    memory_per_token: float  # GB per 1000 tokens
    training_cost_usd: float  # Estimated training cost
    training_flops: float  # Total training FLOPs
    inference_cost_per_1k_tokens: float  # USD
    carbon_footprint_kg: float  # CO2 equivalent
    
    def to_dict(self):
        return self.__dict__

@dataclass
class ModelCapabilities:
    """Capability descriptions."""
    context_window: int  # Maximum context length
    vision: bool  # Vision capabilities
    audio: bool  # Audio capabilities
    code_generation: bool  # Code generation
    tool_use: bool  # Tool use capabilities
    browsing: bool  # Web browsing
    function_calling: bool  # Function calling
    multilingual: int  # Number of languages supported
    safety_alignment: float  # Safety alignment score (0-1)
    reasoning_depth: str  # Shallow, Medium, Deep, Very Deep
    
    def to_dict(self):
        return self.__dict__

@dataclass
class FlagshipModel:
    """Complete flagship model information."""
    model_name: str
    model_id: str
    company: str
    release_date: str
    architecture: ModelArchitecture
    size: ModelSize
    weights: ModelWeights
    performance: ModelPerformance
    efficiency: ModelEfficiency
    capabilities: ModelCapabilities
    ranking: int  # Overall ranking (1 = best)
    category_rankings: Dict[str, int]  # Rankings by category
    
    def to_dict(self):
        return {
            'model_name': self.model_name,
            'model_id': self.model_id,
            'company': self.company,
            'release_date': self.release_date,
            'architecture': self.architecture.value,
            'size': self.size.value,
            'weights': self.weights.to_dict(),
            'performance': self.performance.to_dict(),
            'efficiency': self.efficiency.to_dict(),
            'capabilities': self.capabilities.to_dict(),
            'ranking': self.ranking,
            'category_rankings': self.category_rankings
        }

class FlagshipModelDatabase:
    """
    Database of flagship LLM models with comprehensive stats.
    Ranked from best to least across multiple dimensions.
    """
    
    def __init__(self):
        self.models = {}
        self.rankings = {}
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the database with flagship models."""
        
        # Claude 3.5 Sonnet (2024) - Current SOTA
        self.add_model(FlagshipModel(
            model_name="Claude 3.5 Sonnet",
            model_id="claude-3.5-sonnet",
            company="Anthropic",
            release_date="2024-06",
            architecture=ModelArchitecture.TRANSFORMER,
            size=ModelSize.FLAGSHIP,
            weights=ModelWeights(
                total_parameters=175_000_000_000,  # 175B estimated
                trainable_parameters=175_000_000_000,
                embedding_parameters=10_000_000_000,
                attention_parameters=80_000_000_000,
                feedforward_parameters=85_000_000_000,
                moe_parameters=0,
                quantization_bits=16,
                fp16_equivalent=175_000_000_000,
                effective_parameters=175_000_000_000
            ),
            performance=ModelPerformance(
                mmlu_score=88.7,
                mmlu_pro_score=87.2,
                human_eval_score=92.0,
                math_score=71.1,
                gsm8k_score=96.4,
                hellaswag_score=95.8,
                arc_challenge_score=89.8,
                truthfulqa_score=68.5,
                winogrande_score=93.2,
                gpt4_benchmark=96.0,
                claude_benchmark=97.5,
                custom_benchmark=95.0
            ),
            efficiency=ModelEfficiency(
                parameters_per_billion=175.0,
                flops_per_token=350.0,
                tokens_per_second=45.0,
                memory_per_token=2.5,
                training_cost_usd=100_000_000,
                training_flops=1.0e24,
                inference_cost_per_1k_tokens=0.015,
                carbon_footprint_kg=500.0
            ),
            capabilities=ModelCapabilities(
                context_window=200_000,
                vision=True,
                audio=False,
                code_generation=True,
                tool_use=True,
                browsing=True,
                function_calling=True,
                multilingual=100,
                safety_alignment=0.95,
                reasoning_depth="Very Deep"
            ),
            ranking=1,
            category_rankings={
                'reasoning': 1,
                'coding': 1,
                'math': 2,
                'language': 1,
                'safety': 1
            }
        ))
        
        # GPT-4 Turbo (2024)
        self.add_model(FlagshipModel(
            model_name="GPT-4 Turbo",
            model_id="gpt-4-turbo",
            company="OpenAI",
            release_date="2024-04",
            architecture=ModelArchitecture.TRANSFORMER,
            size=ModelSize.FLAGSHIP,
            weights=ModelWeights(
                total_parameters=1_700_000_000_000,  # 1.7T estimated
                trainable_parameters=1_700_000_000_000,
                embedding_parameters=100_000_000_000,
                attention_parameters=800_000_000_000,
                feedforward_parameters=800_000_000_000,
                moe_parameters=0,
                quantization_bits=16,
                fp16_equivalent=1_700_000_000_000,
                effective_parameters=1_700_000_000_000
            ),
            performance=ModelPerformance(
                mmlu_score=86.4,
                mmlu_pro_score=85.5,
                human_eval_score=90.2,
                math_score=68.4,
                gsm8k_score=92.0,
                hellaswag_score=95.1,
                arc_challenge_score=87.8,
                truthfulqa_score=59.0,
                winogrande_score=91.7,
                gpt4_benchmark=95.0,
                claude_benchmark=94.0,
                custom_benchmark=93.5
            ),
            efficiency=ModelEfficiency(
                parameters_per_billion=1700.0,
                flops_per_token=3400.0,
                tokens_per_second=30.0,
                memory_per_token=4.0,
                training_cost_usd=500_000_000,
                training_flops=5.0e24,
                inference_cost_per_1k_tokens=0.01,
                carbon_footprint_kg=2500.0
            ),
            capabilities=ModelCapabilities(
                context_window=128_000,
                vision=True,
                audio=True,
                code_generation=True,
                tool_use=True,
                browsing=True,
                function_calling=True,
                multilingual=50,
                safety_alignment=0.90,
                reasoning_depth="Very Deep"
            ),
            ranking=2,
            category_rankings={
                'reasoning': 2,
                'coding': 2,
                'math': 3,
                'language': 2,
                'safety': 2
            }
        ))
        
        # Gemini 1.5 Pro (2024)
        self.add_model(FlagshipModel(
            model_name="Gemini 1.5 Pro",
            model_id="gemini-1.5-pro",
            company="Google",
            release_date="2024-02",
            architecture=ModelArchitecture.TRANSFORMER,
            size=ModelSize.FLAGSHIP,
            weights=ModelWeights(
                total_parameters=1_500_000_000_000,  # 1.5T estimated
                trainable_parameters=1_500_000_000_000,
                embedding_parameters=80_000_000_000,
                attention_parameters=700_000_000_000,
                feedforward_parameters=720_000_000_000,
                moe_parameters=0,
                quantization_bits=16,
                fp16_equivalent=1_500_000_000_000,
                effective_parameters=1_500_000_000_000
            ),
            performance=ModelPerformance(
                mmlu_score=85.2,
                mmlu_pro_score=83.7,
                human_eval_score=88.5,
                math_score=65.8,
                gsm8k_score=91.5,
                hellaswag_score=94.5,
                arc_challenge_score=86.2,
                truthfulqa_score=62.0,
                winogrande_score=90.8,
                gpt4_benchmark=93.0,
                claude_benchmark=92.0,
                custom_benchmark=92.0
            ),
            efficiency=ModelEfficiency(
                parameters_per_billion=1500.0,
                flops_per_token=3000.0,
                tokens_per_second=35.0,
                memory_per_token=3.5,
                training_cost_usd=400_000_000,
                training_flops=4.0e24,
                inference_cost_per_1k_tokens=0.008,
                carbon_footprint_kg=2000.0
            ),
            capabilities=ModelCapabilities(
                context_window=1_000_000,  # 1M tokens
                vision=True,
                audio=True,
                code_generation=True,
                tool_use=True,
                browsing=True,
                function_calling=True,
                multilingual=100,
                safety_alignment=0.88,
                reasoning_depth="Very Deep"
            ),
            ranking=3,
            category_rankings={
                'reasoning': 3,
                'coding': 3,
                'math': 4,
                'language': 3,
                'safety': 3
            }
        ))
        
        # GLM-4 (2024)
        self.add_model(FlagshipModel(
            model_name="GLM-4",
            model_id="glm-4",
            company="Zhipu AI",
            release_date="2024-01",
            architecture=ModelArchitecture.TRANSFORMER,
            size=ModelSize.FLAGSHIP,
            weights=ModelWeights(
                total_parameters=1_800_000_000_000,  # 1.8T estimated
                trainable_parameters=1_800_000_000_000,
                embedding_parameters=90_000_000_000,
                attention_parameters=850_000_000_000,
                feedforward_parameters=860_000_000_000,
                moe_parameters=0,
                quantization_bits=16,
                fp16_equivalent=1_800_000_000_000,
                effective_parameters=1_800_000_000_000
            ),
            performance=ModelPerformance(
                mmlu_score=82.5,
                mmlu_pro_score=81.0,
                human_eval_score=85.0,
                math_score=62.5,
                gsm8k_score=89.0,
                hellaswag_score=93.0,
                arc_challenge_score=84.5,
                truthfulqa_score=58.0,
                winogrande_score=89.5,
                gpt4_benchmark=90.0,
                claude_benchmark=89.0,
                custom_benchmark=89.5
            ),
            efficiency=ModelEfficiency(
                parameters_per_billion=1800.0,
                flops_per_token=3600.0,
                tokens_per_second=32.0,
                memory_per_token=3.8,
                training_cost_usd=450_000_000,
                training_flops=4.5e24,
                inference_cost_per_1k_tokens=0.009,
                carbon_footprint_kg=2200.0
            ),
            capabilities=ModelCapabilities(
                context_window=128_000,
                vision=True,
                audio=False,
                code_generation=True,
                tool_use=True,
                browsing=True,
                function_calling=True,
                multilingual=50,
                safety_alignment=0.85,
                reasoning_depth="Deep"
            ),
            ranking=4,
            category_rankings={
                'reasoning': 4,
                'coding': 4,
                'math': 5,
                'language': 4,
                'safety': 4
            }
        ))
        
        # DeepSeek V2 (2024)
        self.add_model(FlagshipModel(
            model_name="DeepSeek V2",
            model_id="deepseek-v2",
            company="DeepSeek",
            release_date="2024-05",
            architecture=ModelArchitecture.MIXTURE_OF_EXPERTS,
            size=ModelSize.FLAGSHIP,
            weights=ModelWeights(
                total_parameters=236_000_000_000,  # 236B total
                trainable_parameters=21_000_000_000,  # 21B active
                embedding_parameters=8_000_000_000,
                attention_parameters=100_000_000_000,
                feedforward_parameters=128_000_000_000,
                moe_parameters=160_000_000_000,
                quantization_bits=16,
                fp16_equivalent=236_000_000_000,
                effective_parameters=21_000_000_000  # Active parameters
            ),
            performance=ModelPerformance(
                mmlu_score=81.0,
                mmlu_pro_score=79.5,
                human_eval_score=82.5,
                math_score=60.0,
                gsm8k_score=87.5,
                hellaswag_score=92.0,
                arc_challenge_score=82.0,
                truthfulqa_score=55.0,
                winogrande_score=88.0,
                gpt4_benchmark=88.0,
                claude_benchmark=87.0,
                custom_benchmark=87.5
            ),
            efficiency=ModelEfficiency(
                parameters_per_billion=236.0,
                flops_per_token=50.0,  # Lower due to MoE
                tokens_per_second=55.0,
                memory_per_token=1.5,
                training_cost_usd=50_000_000,
                training_flops=1.0e24,
                inference_cost_per_1k_tokens=0.003,
                carbon_footprint_kg=250.0
            ),
            capabilities=ModelCapabilities(
                context_window=128_000,
                vision=False,
                audio=False,
                code_generation=True,
                tool_use=True,
                browsing=False,
                function_calling=True,
                multilingual=30,
                safety_alignment=0.80,
                reasoning_depth="Deep"
            ),
            ranking=5,
            category_rankings={
                'reasoning': 5,
                'coding': 5,
                'math': 6,
                'language': 5,
                'safety': 5
            }
        ))
        
        # Llama 3.1 405B (2024)
        self.add_model(FlagshipModel(
            model_name="Llama 3.1 405B",
            model_id="llama-3.1-405b",
            company="Meta",
            release_date="2024-07",
            architecture=ModelArchitecture.TRANSFORMER,
            size=ModelSize.MASSIVE,
            weights=ModelWeights(
                total_parameters=405_000_000_000,
                trainable_parameters=405_000_000_000,
                embedding_parameters=20_000_000_000,
                attention_parameters=190_000_000_000,
                feedforward_parameters=195_000_000_000,
                moe_parameters=0,
                quantization_bits=16,
                fp16_equivalent=405_000_000_000,
                effective_parameters=405_000_000_000
            ),
            performance=ModelPerformance(
                mmlu_score=88.3,
                mmlu_pro_score=86.5,
                human_eval_score=89.0,
                math_score=68.5,
                gsm8k_score=93.5,
                hellaswag_score=95.0,
                arc_challenge_score=88.5,
                truthfulqa_score=60.0,
                winogrande_score=92.0,
                gpt4_benchmark=92.5,
                claude_benchmark=91.5,
                custom_benchmark=91.5
            ),
            efficiency=ModelEfficiency(
                parameters_per_billion=405.0,
                flops_per_token=810.0,
                tokens_per_second=25.0,
                memory_per_token=3.0,
                training_cost_usd=200_000_000,
                training_flops=2.0e24,
                inference_cost_per_1k_tokens=0.005,
                carbon_footprint_kg=1000.0
            ),
            capabilities=ModelCapabilities(
                context_window=128_000,
                vision=False,
                audio=False,
                code_generation=True,
                tool_use=True,
                browsing=True,
                function_calling=True,
                multilingual=8,
                safety_alignment=0.82,
                reasoning_depth="Very Deep"
            ),
            ranking=6,
            category_rankings={
                'reasoning': 6,
                'coding': 6,
                'math': 7,
                'language': 6,
                'safety': 6
            }
        ))
        
        # Mixtral 8x22B (2024)
        self.add_model(FlagshipModel(
            model_name="Mixtral 8x22B",
            model_id="mixtral-8x22b",
            company="Mistral AI",
            release_date="2024-04",
            architecture=ModelArchitecture.MIXTURE_OF_EXPERTS,
            size=ModelSize.LARGE,
            weights=ModelWeights(
                total_parameters=141_000_000_000,  # 141B total
                trainable_parameters=39_000_000_000,  # 39B active
                embedding_parameters=5_000_000_000,
                attention_parameters=60_000_000_000,
                feedforward_parameters=76_000_000_000,
                moe_parameters=96_000_000_000,
                quantization_bits=16,
                fp16_equivalent=141_000_000_000,
                effective_parameters=39_000_000_000
            ),
            performance=ModelPerformance(
                mmlu_score=81.2,
                mmlu_pro_score=79.8,
                human_eval_score=83.0,
                math_score=61.5,
                gsm8k_score=88.0,
                hellaswag_score=92.5,
                arc_challenge_score=83.0,
                truthfulqa_score=56.0,
                winogrande_score=89.0,
                gpt4_benchmark=89.0,
                claude_benchmark=88.0,
                custom_benchmark=88.5
            ),
            efficiency=ModelEfficiency(
                parameters_per_billion=141.0,
                flops_per_token=80.0,
                tokens_per_second=50.0,
                memory_per_token=2.0,
                training_cost_usd=80_000_000,
                training_flops=1.5e24,
                inference_cost_per_1k_tokens=0.004,
                carbon_footprint_kg=400.0
            ),
            capabilities=ModelCapabilities(
                context_window=32_000,
                vision=False,
                audio=False,
                code_generation=True,
                tool_use=True,
                browsing=False,
                function_calling=True,
                multilingual=30,
                safety_alignment=0.78,
                reasoning_depth="Deep"
            ),
            ranking=7,
            category_rankings={
                'reasoning': 7,
                'coding': 7,
                'math': 8,
                'language': 7,
                'safety': 7
            }
        ))
        
        # Qwen2.5 72B (2024)
        self.add_model(FlagshipModel(
            model_name="Qwen2.5 72B",
            model_id="qwen2.5-72b",
            company="Alibaba",
            release_date="2024-09",
            architecture=ModelArchitecture.TRANSFORMER,
            size=ModelSize.LARGE,
            weights=ModelWeights(
                total_parameters=72_000_000_000,
                trainable_parameters=72_000_000_000,
                embedding_parameters=4_000_000_000,
                attention_parameters=34_000_000_000,
                feedforward_parameters=34_000_000_000,
                moe_parameters=0,
                quantization_bits=16,
                fp16_equivalent=72_000_000_000,
                effective_parameters=72_000_000_000
            ),
            performance=ModelPerformance(
                mmlu_score=86.5,
                mmlu_pro_score=84.8,
                human_eval_score=86.0,
                math_score=67.0,
                gsm8k_score=92.0,
                hellaswag_score=94.0,
                arc_challenge_score=87.0,
                truthfulqa_score=59.0,
                winogrande_score=91.0,
                gpt4_benchmark=91.0,
                claude_benchmark=90.0,
                custom_benchmark=90.5
            ),
            efficiency=ModelEfficiency(
                parameters_per_billion=72.0,
                flops_per_token=144.0,
                tokens_per_second=40.0,
                memory_per_token=2.2,
                training_cost_usd=60_000_000,
                training_flops=8.0e23,
                inference_cost_per_1k_tokens=0.006,
                carbon_footprint_kg=300.0
            ),
            capabilities=ModelCapabilities(
                context_window=32_000,
                vision=False,
                audio=False,
                code_generation=True,
                tool_use=True,
                browsing=False,
                function_calling=True,
                multilingual=30,
                safety_alignment=0.80,
                reasoning_depth="Deep"
            ),
            ranking=8,
            category_rankings={
                'reasoning': 8,
                'coding': 8,
                'math': 9,
                'language': 8,
                'safety': 8
            }
        ))
        
        # Compute rank summaries
        self.calculate_rankings()
    
    def add_model(self, model: FlagshipModel):
        """Add a model to the database."""
        self.models[model.model_id] = model
    
    def calculate_rankings(self):
        """Calculate rankings based on overall performance."""
        models_list = list(self.models.values())
        
        # Sort by custom benchmark score (overall performance)
        models_list.sort(key=lambda m: m.performance.custom_benchmark, reverse=True)
        
        # Update rankings
        for rank, model in enumerate(models_list, 1):
            model.ranking = rank
    
    def get_model(self, model_id: str) -> Optional[FlagshipModel]:
        """Get a model by ID."""
        return self.models.get(model_id)
    
    def get_all_models(self) -> List[FlagshipModel]:
        """Get all models ranked by overall performance."""
        return sorted(self.models.values(), key=lambda m: m.ranking)
    
    def get_models_by_size(self, size: ModelSize) -> List[FlagshipModel]:
        """Get models filtered by size."""
        return [m for m in self.models.values() if m.size == size]
    
    def get_models_by_company(self, company: str) -> List[FlagshipModel]:
        """Get models filtered by company."""
        return [m for m in self.models.values() if m.company == company]
    
    def get_top_n_models(self, n: int) -> List[FlagshipModel]:
        """Get top N models by ranking."""
        return sorted(self.models.values(), key=lambda m: m.ranking)[:n]
    
    def get_ranking_summary(self) -> Dict:
        """Get summary of rankings."""
        return {
            'total_models': len(self.models),
            'top_model': self.get_top_n_models(1)[0].model_name if self.models else None,
            'companies': list(set(m.company for m in self.models.values())),
            'size_distribution': {
                size.value: len(self.get_models_by_size(size))
                for size in ModelSize
            }
        }
    
    def export_database(self, filepath: str):
        """Export database to JSON file."""
        data = {
            'models': [m.to_dict() for m in self.get_all_models()],
            'rankings': self.get_ranking_summary()
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)