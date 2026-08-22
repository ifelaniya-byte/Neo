"""
ENHANCED RESEARCH INTEGRATION WITH AI-POWERED DISCOVERY

Advanced research system with:
- AI-powered knowledge extraction
- Semantic search and retrieval
- Automatic insight generation
- Cross-source knowledge synthesis
- Intelligent query expansion
- Research quality assessment
- Knowledge graph integration
"""

import json
import random
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict
import math


class SourceType(Enum):
    """Types of research sources."""
    DOCUMENTATION = "DOCUMENTATION"
    CODE_REPOSITORY = "CODE_REPOSITORY"
    ACADEMIC_PAPER = "ACADEMIC_PAPER"
    FORUM_POST = "FORUM_POST"
    TUTORIAL = "TUTORIAL"
    BLOG_POST = "BLOG_POST"
    STACK_OVERFLOW = "STACK_OVERFLOW"
    GITHUB = "GITHUB"
    ARXIV = "ARXIV"
    INTERNAL_KNOWLEDGE = "INTERNAL_KNOWLEDGE"


class ResearchQuality(Enum):
    """Quality assessment of research sources."""
    HIGH = "HIGH"  # Peer-reviewed, official documentation
    MEDIUM = "MEDIUM"  # Community-validated, reputable
    LOW = "LOW"  # Unverified, anecdotal
    UNCERTAIN = "UNCERTAIN"  # Quality cannot be determined


class InsightType(Enum):
    """Types of research insights."""
    SOLUTION = "SOLUTION"
    OPTIMIZATION = "OPTIMIZATION"
    ALTERNATIVE = "ALTERNATIVE"
    WARNING = "WARNING"
    BEST_PRACTICE = "BEST_PRACTICE"
    PATTERN = "PATTERN"
    ANTI_PATTERN = "ANTI_PATTERN"


@dataclass
class ResearchSource:
    """A research source with metadata."""
    id: str
    source_type: str
    url: str
    title: str
    authors: List[str]
    publication_date: str
    quality: str
    relevance_score: float
    access_count: int
    last_accessed: str
    tags: List[str]
    summary: str
    content_hash: str


@dataclass
class ResearchQuery:
    """A research query with metadata."""
    id: str
    query_text: str
    expanded_terms: List[str]
    context: Dict
    timestamp: str
    results_count: int
    satisfaction_score: float
    related_queries: List[str]


@dataclass
class ResearchInsight:
    """An insight extracted from research."""
    id: str
    insight_type: str
    content: str
    confidence: float
    source_ids: List[str]
    applicable_contexts: List[str]
    validation_status: str
    citations: List[str]
    extracted_at: str


@dataclass
class KnowledgeSynthesis:
    """Synthesized knowledge from multiple sources."""
    id: str
    topic: str
    key_findings: List[str]
    consensus_points: List[str]
    conflicting_points: List[str]
    recommended_actions: List[str]
    confidence_score: float
    source_count: int
    last_updated: str


class SemanticSearchEngine:
    """Semantic search for research queries."""
    
    def __init__(self):
        self.term_frequencies: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.document_frequencies: Dict[str, int] = defaultdict(int)
        self.total_documents = 0
        self.semantic_clusters: Dict[str, List[str]] = defaultdict(list)
    
    def index_document(self, doc_id: str, text: str, tags: List[str]):
        """Index a document for semantic search."""
        # Tokenize and count terms
        terms = self._tokenize(text)
        
        for term in terms:
            self.term_frequencies[doc_id][term] += 1
            self.document_frequencies[term] += 1
        
        # Add to semantic clusters based on tags
        for tag in tags:
            self.semantic_clusters[tag].append(doc_id)
        
        self.total_documents += 1
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        # Simple tokenization - in production, use more sophisticated NLP
        terms = re.findall(r'\b\w+\b', text.lower())
        return [term for term in terms if len(term) > 2]
    
    def expand_query(self, query: str) -> List[str]:
        """Expand query with related terms."""
        terms = self._tokenize(query)
        expanded_terms = set(terms)
        
        # Find semantically related terms
        for term in terms:
            # Find terms that co-occur frequently
            related = self._find_related_terms(term)
            expanded_terms.update(related[:5])  # Top 5 related terms
        
        return list(expanded_terms)
    
    def _find_related_terms(self, term: str, top_k: int = 10) -> List[str]:
        """Find terms semantically related to given term."""
        if term not in self.document_frequencies:
            return []
        
        # Calculate co-occurrence scores
        co_occurrence_scores = defaultdict(float)
        
        for doc_id, term_counts in self.term_frequencies.items():
            if term in term_counts:
                for other_term in term_counts.keys():
                    if other_term != term:
                        co_occurrence_scores[other_term] += term_counts[term] * term_counts[other_term]
        
        # Normalize and sort
        for other_term in co_occurrence_scores:
            co_occurrence_scores[other_term] /= self.document_frequencies[other_term]
        
        related = sorted(co_occurrence_scores.items(), key=lambda x: x[1], reverse=True)
        return [term for term, score in related[:top_k]]
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """Search for relevant documents."""
        expanded_terms = self.expand_query(query)
        
        # Calculate relevance scores
        doc_scores = defaultdict(float)
        
        for term in expanded_terms:
            idf = math.log(self.total_documents / (self.document_frequencies[term] + 1))
            
            for doc_id, term_counts in self.term_frequencies.items():
                if term in term_counts:
                    tf = term_counts[term]
                    doc_scores[doc_id] += tf * idf
        
        # Normalize scores
        max_score = max(doc_scores.values()) if doc_scores else 1.0
        normalized_scores = [(doc_id, score / max_score) for doc_id, score in doc_scores.items()]
        
        # Sort and return top results
        normalized_scores.sort(key=lambda x: x[1], reverse=True)
        return normalized_scores[:top_k]


class InsightExtractor:
    """Extract insights from research sources."""
    
    def __init__(self):
        self.patterns = {
            InsightType.SOLUTION: [
                r"solves? (the )?(problem|issue)",
                r"fixes? (the )?(bug|error)",
                r"resolves? (the )?(problem|issue)"
            ],
            InsightType.OPTIMIZATION: [
                r"optimi[sz]e",
                r"improve (performance|speed|efficiency)",
                r"reduce (time|memory|complexity)"
            ],
            InsightType.WARNING: [
                r"warning",
                r"caution",
                r"be careful",
                r"avoid"
            ],
            InsightType.BEST_PRACTICE: [
                r"best practice",
                r"recommended",
                r"should (use|do|implement)"
            ]
        }
    
    def extract_insights(self, source: ResearchSource, text: str) -> List[ResearchInsight]:
        """Extract insights from a research source."""
        insights = []
        sentences = self._split_sentences(text)
        
        for sentence in sentences:
            for insight_type, patterns in self.patterns.items():
                for pattern in patterns:
                    if re.search(pattern, sentence, re.IGNORECASE):
                        insight_id = hashlib.md5(f"{source.id}_{sentence}".encode()).hexdigest()[:8]
                        
                        insight = ResearchInsight(
                            id=insight_id,
                            insight_type=insight_type.value,
                            content=sentence.strip(),
                            confidence=self._calculate_confidence(sentence, insight_type),
                            source_ids=[source.id],
                            applicable_contexts=self._extract_contexts(sentence),
                            validation_status="PENDING",
                            citations=[source.id],
                            extracted_at=datetime.now().isoformat()
                        )
                        
                        insights.append(insight)
        
        return insights
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _calculate_confidence(self, sentence: str, insight_type: InsightType) -> float:
        """Calculate confidence score for an insight."""
        # Base confidence
        confidence = 0.5
        
        # Increase confidence for longer, more specific sentences
        if len(sentence) > 50:
            confidence += 0.2
        
        # Increase confidence for sentences with specific terms
        specific_terms = ["implement", "use", "apply", "method", "function", "algorithm"]
        if any(term in sentence.lower() for term in specific_terms):
            confidence += 0.1
        
        # Decrease confidence for uncertain language
        uncertain_terms = ["might", "could", "possibly", "maybe", "perhaps"]
        if any(term in sentence.lower() for term in uncertain_terms):
            confidence -= 0.2
        
        return max(0.1, min(0.95, confidence))
    
    def _extract_contexts(self, sentence: str) -> List[str]:
        """Extract applicable contexts from sentence."""
        contexts = []
        
        # Programming-related contexts
        programming_terms = ["python", "javascript", "java", "c++", "algorithm", "data structure"]
        for term in programming_terms:
            if term in sentence.lower():
                contexts.append(term)
        
        # Domain-specific contexts
        domain_terms = ["machine learning", "web development", "database", "api", "security"]
        for term in domain_terms:
            if term in sentence.lower():
                contexts.append(term)
        
        return contexts if contexts else ["general"]


class KnowledgeSynthesizer:
    """Synthesize knowledge from multiple sources."""
    
    def __init__(self):
        self.syntheses: Dict[str, KnowledgeSynthesis] = {}
    
    def synthesize(self, topic: str, insights: List[ResearchInsight], 
                  sources: List[ResearchSource]) -> KnowledgeSynthesis:
        """Synthesize knowledge from multiple insights and sources."""
        synthesis_id = hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        # Group insights by type
        insights_by_type = defaultdict(list)
        for insight in insights:
            insights_by_type[insight.insight_type].append(insight)
        
        # Extract key findings
        key_findings = []
        for insight_type, type_insights in insights_by_type.items():
            if insight_type in [InsightType.SOLUTION.value, InsightType.OPTIMIZATION.value]:
                key_findings.extend([i.content for i in type_insights[:3]])
        
        # Find consensus points
        consensus_points = self._find_consensus(insights)
        
        # Find conflicting points
        conflicting_points = self._find_conflicts(insights)
        
        # Generate recommended actions
        recommended_actions = self._generate_actions(insights_by_type)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence(insights, sources)
        
        synthesis = KnowledgeSynthesis(
            id=synthesis_id,
            topic=topic,
            key_findings=key_findings,
            consensus_points=consensus_points,
            conflicting_points=conflicting_points,
            recommended_actions=recommended_actions,
            confidence_score=confidence_score,
            source_count=len(sources),
            last_updated=datetime.now().isoformat()
        )
        
        self.syntheses[synthesis_id] = synthesis
        return synthesis
    
    def _find_consensus(self, insights: List[ResearchInsight]) -> List[str]:
        """Find points of consensus among insights."""
        # Simple consensus detection based on similar content
        consensus = []
        
        # Group insights by content similarity
        insight_groups = defaultdict(list)
        for insight in insights:
            # Simple similarity grouping
            content_hash = hashlib.md5(insight.content.lower().encode()).hexdigest()[:8]
            insight_groups[content_hash].append(insight)
        
        # Find groups with multiple insights (consensus)
        for group_hash, group_insights in insight_groups.items():
            if len(group_insights) >= 2:
                consensus.append(group_insights[0].content)
        
        return consensus
    
    def _find_conflicts(self, insights: List[ResearchInsight]) -> List[str]:
        """Find conflicting points among insights."""
        conflicts = []
        
        # Look for insights with opposite types
        solution_insights = [i for i in insights if i.insight_type == InsightType.SOLUTION.value]
        warning_insights = [i for i in insights if i.insight_type == InsightType.WARNING.value]
        
        # Check for similar content between solutions and warnings
        for solution in solution_insights:
            for warning in warning_insights:
                if self._content_similarity(solution.content, warning.content) > 0.7:
                    conflicts.append(f"Conflict: '{solution.content}' vs '{warning.content}'")
        
        return conflicts
    
    def _content_similarity(self, content1: str, content2: str) -> float:
        """Calculate similarity between two content strings."""
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1 & words2
        union = words1 | words2
        
        return len(intersection) / len(union)
    
    def _generate_actions(self, insights_by_type: Dict[str, List[ResearchInsight]]) -> List[str]:
        """Generate recommended actions from insights."""
        actions = []
        
        # Extract solutions and optimizations
        solution_insights = insights_by_type.get(InsightType.SOLUTION.value, [])
        optimization_insights = insights_by_type.get(InsightType.OPTIMIZATION.value, [])
        
        for insight in solution_insights[:3]:
            if insight.confidence > 0.7:
                actions.append(f"Consider: {insight.content}")
        
        for insight in optimization_insights[:2]:
            if insight.confidence > 0.6:
                actions.append(f"Optimize: {insight.content}")
        
        return actions
    
    def _calculate_confidence(self, insights: List[ResearchInsight], 
                            sources: List[ResearchSource]) -> float:
        """Calculate overall confidence score for synthesis."""
        if not insights:
            return 0.0
        
        # Average insight confidence
        avg_insight_confidence = sum(i.confidence for i in insights) / len(insights)
        
        # Source quality factor
        quality_scores = {
            ResearchQuality.HIGH: 1.0,
            ResearchQuality.MEDIUM: 0.7,
            ResearchQuality.LOW: 0.4,
            ResearchQuality.UNCERTAIN: 0.2
        }
        
        avg_source_quality = sum(quality_scores.get(s.quality, 0.5) for s in sources) / len(sources) if sources else 0.5
        
        # Source diversity factor
        source_types = set(s.source_type for s in sources)
        diversity_factor = min(1.0, len(source_types) / 3.0)
        
        # Combined confidence
        confidence = (avg_insight_confidence * 0.4 + 
                    avg_source_quality * 0.4 + 
                    diversity_factor * 0.2)
        
        return min(0.95, max(0.1, confidence))


class EnhancedResearchSystem:
    """
    Enhanced research system with AI-powered discovery and knowledge synthesis.
    """
    
    def __init__(self, storage_path="enhanced_research_system.json"):
        self.storage_path = storage_path
        self.sources: Dict[str, ResearchSource] = {}
        self.queries: Dict[str, ResearchQuery] = {}
        self.insights: Dict[str, ResearchInsight] = {}
        self.syntheses: Dict[str, KnowledgeSynthesis] = {}
        
        # AI components
        self.search_engine = SemanticSearchEngine()
        self.insight_extractor = InsightExtractor()
        self.synthesizer = KnowledgeSynthesizer()
        
        self.load_data()
    
    def add_source(self, url: str, title: str, content: str, 
                  source_type: SourceType, authors: List[str] = None,
                  tags: List[str] = None, quality: ResearchQuality = ResearchQuality.MEDIUM) -> str:
        """Add a research source to the system."""
        source_id = hashlib.md5(f"{url}_{title}".encode()).hexdigest()[:12]
        content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
        
        source = ResearchSource(
            id=source_id,
            source_type=source_type.value,
            url=url,
            title=title,
            authors=authors or [],
            publication_date=datetime.now().isoformat(),
            quality=quality.value,
            relevance_score=0.5,
            access_count=0,
            last_accessed=datetime.now().isoformat(),
            tags=tags or [],
            summary=content[:200] + "..." if len(content) > 200 else content,
            content_hash=content_hash
        )
        
        self.sources[source_id] = source
        
        # Index for search
        self.search_engine.index_document(source_id, content, tags or [])
        
        # Extract insights
        insights = self.insight_extractor.extract_insights(source, content)
        for insight in insights:
            self.insights[insight.id] = insight
        
        self.save_data()
        return source_id
    
    def research(self, query: str, context: Dict = None, max_results: int = 10) -> Dict[str, Any]:
        """
        Perform research with AI-powered discovery.
        """
        query_id = hashlib.md5(f"{query}_{datetime.now().isoformat()}".encode()).hexdigest()[:8]
        
        # Expand query
        expanded_terms = self.search_engine.expand_query(query)
        
        # Search for relevant sources
        search_results = self.search_engine.search(query, top_k=max_results)
        
        # Get source details
        relevant_sources = []
        for source_id, score in search_results:
            if source_id in self.sources:
                source = self.sources[source_id]
                source.relevance_score = score
                source.access_count += 1
                source.last_accessed = datetime.now().isoformat()
                relevant_sources.append(source)
        
        # Get relevant insights
        relevant_insights = []
        for source in relevant_sources:
            for insight_id, insight in self.insights.items():
                if source.id in insight.source_ids:
                    relevant_insights.append(insight)
        
        # Synthesize knowledge
        synthesis = None
        if relevant_insights:
            synthesis = self.synthesizer.synthesize(query, relevant_insights, relevant_sources)
            self.syntheses[synthesis.id] = synthesis
        
        # Record query
        research_query = ResearchQuery(
            id=query_id,
            query_text=query,
            expanded_terms=expanded_terms,
            context=context or {},
            timestamp=datetime.now().isoformat(),
            results_count=len(relevant_sources),
            satisfaction_score=0.0,  # To be updated by user feedback
            related_queries=self._find_related_queries(query)
        )
        
        self.queries[query_id] = research_query
        self.save_data()
        
        return {
            "query_id": query_id,
            "expanded_terms": expanded_terms,
            "sources": [s.to_dict() if hasattr(s, 'to_dict') else asdict(s) for s in relevant_sources],
            "insights": [i.to_dict() if hasattr(i, 'to_dict') else asdict(i) for i in relevant_insights],
            "synthesis": synthesis.to_dict() if synthesis else None,
            "total_sources": len(relevant_sources),
            "total_insights": len(relevant_insights)
        }
    
    def _find_related_queries(self, query: str) -> List[str]:
        """Find related queries based on history."""
        related = []
        
        for query_id, q in self.queries.items():
            if q.query_text != query:
                # Simple similarity check
                query_words = set(query.lower().split())
                q_words = set(q.query_text.lower().split())
                
                overlap = query_words & q_words
                if len(overlap) >= 2:
                    related.append(q.query_text)
        
        return related[:5]
    
    def get_knowledge_graph_data(self) -> Dict[str, Any]:
        """Get data for knowledge graph integration."""
        nodes = []
        edges = []
        
        # Add source nodes
        for source in self.sources.values():
            nodes.append({
                "id": source.id,
                "type": "source",
                "label": source.title,
                "source_type": source.source_type,
                "quality": source.quality
            })
        
        # Add insight nodes
        for insight in self.insights.values():
            nodes.append({
                "id": insight.id,
                "type": "insight",
                "label": insight.content[:50],
                "insight_type": insight.insight_type,
                "confidence": insight.confidence
            })
            
            # Add edges to sources
            for source_id in insight.source_ids:
                edges.append({
                    "source": source_id,
                    "target": insight.id,
                    "relationship": "contains_insight"
                })
        
        # Add synthesis nodes
        for synthesis in self.syntheses.values():
            nodes.append({
                "id": synthesis.id,
                "type": "synthesis",
                "label": synthesis.topic,
                "confidence": synthesis.confidence_score
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def assess_research_quality(self, topic: str) -> Dict[str, Any]:
        """Assess the quality of research on a topic."""
        # Get relevant insights
        relevant_insights = [i for i in self.insights.values() 
                           if topic.lower() in i.content.lower()]
        
        if not relevant_insights:
            return {
                "topic": topic,
                "quality_score": 0.0,
                "insight_count": 0,
                "assessment": "No research available"
            }
        
        # Calculate quality metrics
        avg_confidence = sum(i.confidence for i in relevant_insights) / len(relevant_insights)
        
        validated_count = sum(1 for i in relevant_insights if i.validation_status == "VALIDATED")
        validation_rate = validated_count / len(relevant_insights)
        
        # Source diversity
        source_ids = set()
        for insight in relevant_insights:
            source_ids.update(insight.source_ids)
        source_diversity = len(source_ids)
        
        # Overall quality score
        quality_score = (avg_confidence * 0.5 + 
                        validation_rate * 0.3 + 
                        min(1.0, source_diversity / 5) * 0.2)
        
        # Assessment
        if quality_score >= 0.8:
            assessment = "High-quality research available"
        elif quality_score >= 0.6:
            assessment = "Moderate-quality research available"
        elif quality_score >= 0.4:
            assessment = "Limited-quality research available"
        else:
            assessment = "Low-quality research available"
        
        return {
            "topic": topic,
            "quality_score": quality_score,
            "insight_count": len(relevant_insights),
            "avg_confidence": avg_confidence,
            "validation_rate": validation_rate,
            "source_diversity": source_diversity,
            "assessment": assessment
        }
    
    def save_data(self):
        """Save research system data to disk."""
        data = {
            "sources": {sid: s.to_dict() if hasattr(s, 'to_dict') else asdict(s) for sid, s in self.sources.items()},
            "queries": {qid: q.to_dict() if hasattr(q, 'to_dict') else asdict(q) for qid, q in self.queries.items()},
            "insights": {iid: i.to_dict() if hasattr(i, 'to_dict') else asdict(i) for iid, i in self.insights.items()},
            "syntheses": {sid: s.to_dict() if hasattr(s, 'to_dict') else asdict(s) for sid, s in self.syntheses.items()}
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_data(self):
        """Load research system data from disk."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Reconstruct sources
            for sid, s_data in data.get("sources", {}).items():
                self.sources[sid] = ResearchSource(**s_data)
                # Re-index
                self.search_engine.index_document(sid, s_data.get('summary', ''), s_data.get('tags', []))
            
            # Reconstruct queries
            for qid, q_data in data.get("queries", {}).items():
                self.queries[qid] = ResearchQuery(**q_data)
            
            # Reconstruct insights
            for iid, i_data in data.get("insights", {}).items():
                self.insights[iid] = ResearchInsight(**i_data)
            
            # Reconstruct syntheses
            for sid, s_data in data.get("syntheses", {}).items():
                self.syntheses[sid] = KnowledgeSynthesis(**s_data)
            
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error loading research data: {e}")


def test_enhanced_research_system():
    """Test the enhanced research system."""
    research_system = EnhancedResearchSystem("test_research_system.json")
    
    # Add some test sources
    research_system.add_source(
        url="https://docs.python.org/3/tutorial/",
        title="Python Tutorial",
        content="Python is a high-level programming language. It is great for beginners. Python supports multiple programming paradigms.",
        source_type=SourceType.DOCUMENTATION,
        authors=["Python Software Foundation"],
        tags=["python", "programming", "tutorial"],
        quality=ResearchQuality.HIGH
    )
    
    research_system.add_source(
        url="https://stackoverflow.com/questions/123",
        title="How to optimize Python code",
        content="To optimize Python code, you should use built-in functions. List comprehensions are faster than loops. Avoid global variables.",
        source_type=SourceType.STACK_OVERFLOW,
        tags=["python", "optimization", "performance"],
        quality=ResearchQuality.MEDIUM
    )
    
    # Perform research
    results = research_system.research("python optimization", {"context": "performance"})
    
    print(f"Research results for 'python optimization':")
    print(f"  Expanded terms: {results['expanded_terms']}")
    print(f"  Sources found: {results['total_sources']}")
    print(f"  Insights found: {results['total_insights']}")
    
    if results['synthesis']:
        synthesis = results['synthesis']
        print(f"\nSynthesis:")
        print(f"  Topic: {synthesis['topic']}")
        print(f"  Confidence: {synthesis['confidence_score']:.2f}")
        print(f"  Key findings: {synthesis['key_findings']}")
    
    # Assess research quality
    quality = research_system.assess_research_quality("python")
    print(f"\nResearch quality assessment: {quality['assessment']}")
    print(f"  Quality score: {quality['quality_score']:.2f}")
    
    # Get knowledge graph data
    kg_data = research_system.get_knowledge_graph_data()
    print(f"\nKnowledge graph: {len(kg_data['nodes'])} nodes, {len(kg_data['edges'])} edges")
    
    # Cleanup
    import os
    if os.path.exists("test_research_system.json"):
        os.remove("test_research_system.json")


if __name__ == "__main__":
    test_enhanced_research_system()