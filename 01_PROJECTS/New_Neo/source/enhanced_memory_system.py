"""
ENHANCED MEMORY SYSTEM

Advanced memory management with modern AI techniques including:
- Attention mechanisms for memory retrieval
- Memory consolidation during rest periods
- Episodic, semantic, and procedural memory separation
- Forgetting curves and memory importance weighting
- Cross-modal memory associations
"""

import time
import json
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import math


class MemoryType(Enum):
    """Types of memory in the enhanced system."""
    EPISODIC = "EPISODIC"  # Personal experiences and events
    SEMANTIC = "SEMANTIC"  # Facts and general knowledge
    PROCEDURAL = "PROCEDURAL"  # Skills and how-to knowledge
    WORKING = "WORKING"  # Temporary active memory
    LONG_TERM = "LONG_TERM"  # Consolidated permanent memory


class MemoryImportance(Enum):
    """Importance levels for memory items."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    TRIVIAL = "TRIVIAL"


@dataclass
class MemoryItem:
    """A single memory item with enhanced metadata."""
    id: str
    memory_type: str
    content: Any
    importance: str
    timestamp: str
    last_accessed: str
    access_count: int
    emotional_valence: float  # -1.0 to 1.0
    arousal: float  # 0.0 to 1.0
    associations: List[str]  # IDs of related memories
    retrieval_strength: float
    decay_rate: float
    context: Dict
    
    def to_dict(self):
        return asdict(self)


@dataclass
class MemoryConsolidation:
    """Memory consolidation process metadata."""
    session_id: str
    start_time: str
    end_time: str
    memories_consolidated: int
    associations_formed: int
    strength_increase: float
    sleep_cycles: int
    
    def to_dict(self):
        return asdict(self)


class AttentionMechanism:
    """Attention mechanism for memory retrieval."""
    
    def __init__(self):
        self.attention_weights = {}
        self.context_window = 5
        self.focus_history = []
    
    def calculate_attention(self, query: Dict, memories: List[MemoryItem]) -> List[Tuple[float, MemoryItem]]:
        """
        Calculate attention scores for memories based on query.
        Uses similarity and context-aware weighting.
        """
        scored_memories = []
        
        for memory in memories:
            # Content similarity (simplified)
            content_score = self._calculate_similarity(query, memory.context)
            
            # Recency bias
            recency_score = self._calculate_recency(memory.timestamp)
            
            # Importance weighting
            importance_weights = {
                MemoryImportance.CRITICAL.value: 1.0,
                MemoryImportance.HIGH.value: 0.8,
                MemoryImportance.MEDIUM.value: 0.6,
                MemoryImportance.LOW.value: 0.4,
                MemoryImportance.TRIVIAL.value: 0.2
            }
            importance_score = importance_weights.get(memory.importance, 0.5)
            
            # Retrieval strength
            strength_score = memory.retrieval_strength
            
            # Combined attention score
            attention_score = (content_score * 0.4 + 
                              recency_score * 0.2 + 
                              importance_score * 0.2 + 
                              strength_score * 0.2)
            
            scored_memories.append((attention_score, memory))
        
        # Sort by attention score
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        return scored_memories
    
    def _calculate_similarity(self, query: Dict, context: Dict) -> float:
        """Calculate similarity between query and memory context."""
        # Simple overlap-based similarity
        query_keys = set(query.keys())
        context_keys = set(context.keys())
        
        if not query_keys or not context_keys:
            return 0.0
        
        overlap = query_keys & context_keys
        return len(overlap) / max(len(query_keys), len(context_keys))
    
    def _calculate_recency(self, timestamp: str) -> float:
        """Calculate recency score - more recent memories get higher scores."""
        try:
            mem_time = datetime.fromisoformat(timestamp)
            age = (datetime.now() - mem_time).total_seconds()
            
            # Exponential decay for recency
            return math.exp(-age / 86400)  # 24-hour half-life
        except:
            return 0.5


class EnhancedMemorySystem:
    """
    Enhanced memory system with attention mechanisms, consolidation,
    and modern memory management techniques.
    """
    
    def __init__(self, storage_path="enhanced_memory.json"):
        self.storage_path = storage_path
        self.memories: Dict[str, MemoryItem] = {}
        self.memory_index: Dict[MemoryType, List[str]] = {
            MemoryType.EPISODIC: [],
            MemoryType.SEMANTIC: [],
            MemoryType.PROCEDURAL: [],
            MemoryType.WORKING: [],
            MemoryType.LONG_TERM: []
        }
        self.attention = AttentionMechanism()
        self.consolidation_history: List[MemoryConsolidation] = []
        self.forgetting_curve_alpha = 0.5  # Controls forgetting rate
        self.consolidation_threshold = 0.7  # Strength threshold for consolidation
        self.max_working_memory = 7  # Miller's magical number
        self.load_memory()
    
    def generate_memory_id(self, content: Any, memory_type: MemoryType) -> str:
        """Generate unique memory ID."""
        content_str = str(content)
        signature = f"{memory_type.value}:{content_str}:{datetime.now().isoformat()}"
        return hashlib.md5(signature.encode()).hexdigest()[:16]
    
    def store_memory(self, content: Any, memory_type: MemoryType, 
                    importance: MemoryImportance = MemoryImportance.MEDIUM,
                    emotional_valence: float = 0.0,
                    arousal: float = 0.5,
                    context: Optional[Dict] = None) -> str:
        """
        Store a new memory with enhanced metadata.
        """
        memory_id = self.generate_memory_id(content, memory_type)
        
        memory = MemoryItem(
            id=memory_id,
            memory_type=memory_type.value,
            content=content,
            importance=importance.value,
            timestamp=datetime.now().isoformat(),
            last_accessed=datetime.now().isoformat(),
            access_count=0,
            emotional_valence=emotional_valence,
            arousal=arousal,
            associations=[],
            retrieval_strength=1.0,
            decay_rate=self._calculate_decay_rate(importance),
            context=context or {}
        )
        
        self.memories[memory_id] = memory
        self.memory_index[memory_type].append(memory_id)
        
        # If working memory is full, transfer oldest to long-term
        if memory_type == MemoryType.WORKING:
            if len(self.memory_index[MemoryType.WORKING]) > self.max_working_memory:
                self._consolidate_working_memory()
        
        self.save_memory()
        return memory_id
    
    def _calculate_decay_rate(self, importance: MemoryImportance) -> float:
        """Calculate decay rate based on importance."""
        importance_decay = {
            MemoryImportance.CRITICAL: 0.01,
            MemoryImportance.HIGH: 0.05,
            MemoryImportance.MEDIUM: 0.1,
            MemoryImportance.LOW: 0.2,
            MemoryImportance.TRIVIAL: 0.5
        }
        return importance_decay.get(importance, 0.1)
    
    def retrieve_memory(self, query: Dict, memory_type: Optional[MemoryType] = None,
                       top_k: int = 5) -> List[MemoryItem]:
        """
        Retrieve memories using attention mechanism.
        """
        # Filter by memory type if specified
        if memory_type:
            candidate_ids = self.memory_index.get(memory_type, [])
            candidate_memories = [self.memories[mid] for mid in candidate_ids 
                                 if mid in self.memories]
        else:
            candidate_memories = list(self.memories.values())
        
        # Use attention mechanism to score and rank
        scored_memories = self.attention.calculate_attention(query, candidate_memories)
        
        # Update access metadata
        retrieved_memories = []
        for score, memory in scored_memories[:top_k]:
            memory.last_accessed = datetime.now().isoformat()
            memory.access_count += 1
            memory.retrieval_strength = min(1.0, memory.retrieval_strength + 0.1)
            retrieved_memories.append(memory)
        
        self.save_memory()
        return retrieved_memories
    
    def associate_memories(self, memory_id_1: str, memory_id_2: str, strength: float = 0.5):
        """
        Create association between two memories.
        """
        if memory_id_1 in self.memories and memory_id_2 in self.memories:
            if memory_id_2 not in self.memories[memory_id_1].associations:
                self.memories[memory_id_1].associations.append(memory_id_2)
            if memory_id_1 not in self.memories[memory_id_2].associations:
                self.memories[memory_id_2].associations.append(memory_id_1)
            self.save_memory()
    
    def _consolidate_working_memory(self):
        """Consolidate working memory to long-term storage."""
        working_ids = self.memory_index[MemoryType.WORKING]
        
        # Move oldest working memory to long-term
        if working_ids:
            oldest_id = working_ids[0]
            if oldest_id in self.memories:
                memory = self.memories[oldest_id]
                
                # Check if memory meets consolidation threshold
                if memory.retrieval_strength >= self.consolidation_threshold:
                    # Move to long-term
                    self.memory_index[MemoryType.WORKING].remove(oldest_id)
                    memory.memory_type = MemoryType.LONG_TERM.value
                    memory.decay_rate *= 0.5  # Slower decay in long-term
                    self.memory_index[MemoryType.LONG_TERM].append(oldest_id)
                else:
                    # Forget weak memories
                    del self.memories[oldest_id]
                    self.memory_index[MemoryType.WORKING].remove(oldest_id)
    
    def consolidate_memories(self, sleep_cycles: int = 3) -> MemoryConsolidation:
        """
        Perform memory consolidation (simulating sleep).
        Strengthens important memories and forms associations.
        """
        session_id = hashlib.md5(str(datetime.now().isoformat()).encode()).hexdigest()[:8]
        start_time = datetime.now().isoformat()
        
        memories_consolidated = 0
        associations_formed = 0
        total_strength_increase = 0.0
        
        # Strengthen memories based on importance and access
        for memory_id, memory in self.memories.items():
            # Apply forgetting curve
            age = (datetime.now() - datetime.fromisoformat(memory.timestamp)).total_seconds()
            decay = math.exp(-self.forgetting_curve_alpha * age / 86400)
            memory.retrieval_strength *= decay
            
            # Strengthen based on access pattern
            if memory.access_count > 0:
                strength_boost = math.log(memory.access_count + 1) * 0.1
                memory.retrieval_strength = min(1.0, memory.retrieval_strength + strength_boost)
                total_strength_increase += strength_boost
                memories_consolidated += 1
            
            # Form associations between similar memories
            for other_id, other_memory in self.memories.items():
                if memory_id != other_id:
                    similarity = self._calculate_memory_similarity(memory, other_memory)
                    if similarity > 0.8 and other_id not in memory.associations:
                        self.associate_memories(memory_id, other_id, similarity)
                        associations_formed += 1
        
        end_time = datetime.now().isoformat()
        
        consolidation = MemoryConsolidation(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            memories_consolidated=memories_consolidated,
            associations_formed=associations_formed,
            strength_increase=total_strength_increase / max(1, memories_consolidated),
            sleep_cycles=sleep_cycles
        )
        
        self.consolidation_history.append(consolidation)
        self.save_memory()
        return consolidation
    
    def _calculate_memory_similarity(self, memory1: MemoryItem, memory2: MemoryItem) -> float:
        """Calculate similarity between two memories."""
        # Type similarity
        type_match = 1.0 if memory1.memory_type == memory2.memory_type else 0.0
        
        # Context similarity
        context_similarity = self.attention._calculate_similarity(
            memory1.context, memory2.context)
        
        # Temporal proximity
        try:
            time1 = datetime.fromisoformat(memory1.timestamp)
            time2 = datetime.fromisoformat(memory2.timestamp)
            time_diff = abs((time1 - time2).total_seconds())
            temporal_similarity = math.exp(-time_diff / 3600)  # 1-hour half-life
        except:
            temporal_similarity = 0.0
        
        return (type_match * 0.3 + context_similarity * 0.5 + temporal_similarity * 0.2)
    
    def forget_memories(self, threshold: float = 0.1):
        """
        Remove memories that have decayed below threshold.
        """
        to_remove = []
        
        for memory_id, memory in self.memories.items():
            if memory.retrieval_strength < threshold:
                # Don't remove critical memories
                if memory.importance != MemoryImportance.CRITICAL.value:
                    to_remove.append(memory_id)
        
        for memory_id in to_remove:
            # Remove from all indices
            memory_type = self.memories[memory_id].memory_type
            if memory_type in self.memory_index:
                self.memory_index[memory_type].remove(memory_id)
            del self.memories[memory_id]
        
        self.save_memory()
        return len(to_remove)
    
    def get_memory_statistics(self) -> Dict:
        """Get statistics about memory system."""
        stats = {
            'total_memories': len(self.memories),
            'by_type': {},
            'average_retrieval_strength': 0.0,
            'consolidation_sessions': len(self.consolidation_history),
            'total_associations': sum(len(m.associations) for m in self.memories.values())
        }
        
        for memory_type, ids in self.memory_index.items():
            stats['by_type'][memory_type.value] = len(ids)
        
        if self.memories:
            avg_strength = sum(m.retrieval_strength for m in self.memories.values()) / len(self.memories)
            stats['average_retrieval_strength'] = avg_strength
        
        return stats
    
    def save_memory(self):
        """Save memory system to disk."""
        data = {
            'memories': {mid: m.to_dict() for mid, m in self.memories.items()},
            'memory_index': {k.value: v for k, v in self.memory_index.items()},
            'consolidation_history': [asdict(c) for c in self.consolidation_history],
            'forgetting_curve_alpha': self.forgetting_curve_alpha,
            'consolidation_threshold': self.consolidation_threshold
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_memory(self):
        """Load memory system from disk."""
        if not os.path.exists(self.storage_path):
            return
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Reconstruct memory items
            for mid, m_data in data['memories'].items():
                self.memories[mid] = MemoryItem(**m_data)
            
            # Reconstruct index
            for type_str, ids in data['memory_index'].items():
                memory_type = MemoryType(type_str)
                self.memory_index[memory_type] = ids
            
            # Reconstruct consolidation history
            for c_data in data['consolidation_history']:
                self.consolidation_history.append(MemoryConsolidation(**c_data))
            
            # Load parameters
            self.forgetting_curve_alpha = data.get('forgetting_curve_alpha', 0.5)
            self.consolidation_threshold = data.get('consolidation_threshold', 0.7)
            
        except Exception as e:
            print(f"Error loading memory: {e}")


# Import os for file existence check
import os


def test_enhanced_memory():
    """Test the enhanced memory system."""
    memory_system = EnhancedMemorySystem("test_memory.json")
    
    # Store some memories
    memory_system.store_memory(
        "I learned about Python decorators today",
        MemoryType.EPISODIC,
        MemoryImportance.HIGH,
        emotional_valence=0.8,
        context={"topic": "programming", "language": "Python"}
    )
    
    memory_system.store_memory(
        "Decorators allow you to modify function behavior",
        MemoryType.SEMANTIC,
        MemoryImportance.HIGH,
        context={"topic": "programming", "concept": "decorators"}
    )
    
    memory_system.store_memory(
        "To create a decorator, use @symbol",
        MemoryType.PROCEDURAL,
        MemoryImportance.MEDIUM,
        context={"topic": "programming", "action": "create_decorator"}
    )
    
    # Retrieve memories
    query = {"topic": "programming"}
    results = memory_system.retrieve_memory(query, top_k=3)
    
    print("Retrieved memories:")
    for memory in results:
        print(f"  - {memory.content} (Strength: {memory.retrieval_strength:.2f})")
    
    # Consolidate
    consolidation = memory_system.consolidate_memories()
    print(f"\nConsolidation: {consolidation.memories_consolidated} memories consolidated")
    
    # Get statistics
    stats = memory_system.get_memory_statistics()
    print(f"\nStatistics: {stats}")
    
    # Cleanup
    import os
    if os.path.exists("test_memory.json"):
        os.remove("test_memory.json")


if __name__ == "__main__":
    test_enhanced_memory()