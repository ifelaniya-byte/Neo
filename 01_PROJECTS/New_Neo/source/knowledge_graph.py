"""
PROJECT APEX: KNOWLEDGE GRAPH SYSTEM
Maintains relationships between bottlenecks, solutions, and code patterns.
Enables intelligent bottleneck prevention through pattern recognition.
"""

import json
import time
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import networkx as nx
import hashlib

class RelationshipType(Enum):
    CAUSES = "CAUSES"
    SOLVES = "SOLVES"
    RELATED_TO = "RELATED_TO"
    PREVENTS = "PREVENTS"
    SIMILAR_TO = "SIMILAR_TO"
    DEPENDS_ON = "DEPENDS_ON"

class NodeType(Enum):
    BOTTLENECK = "BOTTLENECK"
    SOLUTION = "SOLUTION"
    CODE_PATTERN = "CODE_PATTERN"
    ARCHITECTURAL_COMPONENT = "ARCHITECTURAL_COMPONENT"
    PERFORMANCE_METRIC = "PERFORMANCE_METRIC"

@dataclass
class KnowledgeNode:
    id: str
    node_type: NodeType
    properties: Dict
    created_at: str
    last_updated: str
    confidence: float
    occurrence_count: int
    
    def to_dict(self):
        return asdict(self)

@dataclass
class KnowledgeEdge:
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    strength: float
    created_at: str
    validated: bool
    
    def to_dict(self):
        return asdict(self)

class KnowledgeGraph:
    """
    Knowledge graph for tracking relationships between bottlenecks, solutions, and patterns.
    Enables intelligent prevention through pattern recognition and inference.
    """
    
    def __init__(self, storage_path="knowledge_graph.json"):
        self.storage_path = storage_path
        self.graph = nx.DiGraph()
        self.nodes = {}
        self.edges = {}
        self.load_graph()
    
    def generate_node_id(self, node_type: NodeType, properties: Dict) -> str:
        """Generate unique ID based on node properties."""
        signature = f"{node_type.value}:{json.dumps(properties, sort_keys=True)}"
        return hashlib.md5(signature.encode()).hexdigest()[:16]
    
    def add_node(self, node_type: NodeType, properties: Dict, confidence: float = 0.5) -> str:
        """
        Add a node to the knowledge graph.
        Returns node ID.
        """
        node_id = self.generate_node_id(node_type, properties)
        
        # Check if node already exists
        if node_id in self.nodes:
            # Update existing node
            existing_node = self.nodes[node_id]
            existing_node.occurrence_count += 1
            existing_node.last_updated = time.strftime("%Y-%m-%d %H:%M:%S")
            existing_node.confidence = max(existing_node.confidence, confidence)
            # Merge properties
            existing_node.properties.update(properties)
        else:
            # Create new node
            new_node = KnowledgeNode(
                id=node_id,
                node_type=node_type,
                properties=properties,
                created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                last_updated=time.strftime("%Y-%m-%d %H:%M:%S"),
                confidence=confidence,
                occurrence_count=1
            )
            self.nodes[node_id] = new_node
            self.graph.add_node(node_id, **properties)
        
        self.save_graph()
        return node_id
    
    def add_edge(self, source_id: str, target_id: str, 
                relationship_type: RelationshipType, strength: float = 0.5) -> str:
        """
        Add a relationship edge between nodes.
        Returns edge ID.
        """
        edge_id = f"{source_id}_{relationship_type.value}_{target_id}"
        
        # Check if edge already exists
        if edge_id in self.edges:
            # Update existing edge
            existing_edge = self.edges[edge_id]
            existing_edge.strength = max(existing_edge.strength, strength)
            existing_edge.validated = True
        else:
            # Create new edge
            new_edge = KnowledgeEdge(
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship_type,
                strength=strength,
                created_at=time.strftime("%Y-%m-%d %H:%M:%S"),
                validated=False
            )
            self.edges[edge_id] = new_edge
            self.graph.add_edge(source_id, target_id, 
                              relationship=relationship_type.value,
                              strength=strength)
        
        self.save_graph()
        return edge_id
    
    def add_bottleneck_solution_relationship(self, bottleneck_id: str, 
                                            solution_id: str, 
                                            effectiveness: float):
        """
        Add a bottleneck-solution relationship with effectiveness tracking.
        """
        self.add_edge(bottleneck_id, solution_id, 
                     RelationshipType.SOLVES, effectiveness)
        
        # Also add prevention relationships
        self.add_edge(solution_id, bottleneck_id, 
                     RelationshipType.PREVENTS, effectiveness)
    
    def find_similar_bottlenecks(self, bottleneck_properties: Dict, 
                                threshold: float = 0.7) -> List[str]:
        """
        Find bottlenecks similar to the given properties.
        Uses graph similarity and property matching.
        """
        similar_nodes = []
        
        for node_id, node in self.nodes.items():
            if node.node_type == NodeType.BOTTLENECK:
                similarity = self.calculate_similarity(bottleneck_properties, 
                                                       node.properties)
                if similarity >= threshold:
                    similar_nodes.append((node_id, similarity))
        
        # Sort by similarity
        similar_nodes.sort(key=lambda x: x[1], reverse=True)
        return [node_id for node_id, _ in similar_nodes]
    
    def calculate_similarity(self, props1: Dict, props2: Dict) -> float:
        """Calculate similarity between two property dictionaries."""
        # Simple Jaccard similarity for categorical properties
        keys1 = set(props1.keys())
        keys2 = set(props2.keys())
        
        intersection = keys1 & keys2
        union = keys1 | keys2
        
        if not union:
            return 0.0
        
        key_similarity = len(intersection) / len(union)
        
        # Value similarity for shared keys
        value_similarities = []
        for key in intersection:
            val1 = props1[key]
            val2 = props2[key]
            
            if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                # Numerical similarity
                max_val = max(abs(val1), abs(val2))
                if max_val > 0:
                    sim = 1.0 - abs(val1 - val2) / max_val
                    value_similarities.append(sim)
                else:
                    value_similarities.append(1.0)
            elif val1 == val2:
                value_similarities.append(1.0)
            else:
                value_similarities.append(0.0)
        
        if value_similarities:
            value_similarity = sum(value_similarities) / len(value_similarities)
        else:
            value_similarity = 0.0
        
        # Combine key and value similarities
        return (key_similarity * 0.3 + value_similarity * 0.7)
    
    def suggest_preventive_measures(self, bottleneck_properties: Dict) -> List[Dict]:
        """
        Suggest preventive measures based on similar resolved bottlenecks.
        """
        similar_bottlenecks = self.find_similar_bottlenecks(bottleneck_properties)
        
        preventive_measures = []
        
        for bottleneck_id in similar_bottlenecks:
            # Find solutions that solved similar bottlenecks
            successors = self.graph.successors(bottleneck_id)
            
            for successor_id in successors:
                edge_data = self.graph.get_edge_data(bottleneck_id, successor_id)
                if edge_data.get('relationship') == RelationshipType.SOLVES.value:
                    solution_node = self.nodes.get(successor_id)
                    if solution_node and solution_node.confidence > 0.8:
                        preventive_measures.append({
                            'solution_id': successor_id,
                            'properties': solution_node.properties,
                            'confidence': solution_node.confidence,
                            'effectiveness': edge_data.get('strength', 0.5),
                            'based_on_bottleneck': bottleneck_id
                        })
        
        # Sort by effectiveness and confidence
        preventive_measures.sort(
            key=lambda x: (x['effectiveness'] * x['confidence']), 
            reverse=True
        )
        
        return preventive_measures[:5]  # Return top 5 suggestions
    
    def detect_cascading_failures(self, start_node_id: str) -> List[str]:
        """
        Detect potential cascading failures from a given node.
        Returns list of nodes that could be affected.
        """
        affected_nodes = []
        
        # Find all nodes that depend on the start node
        predecessors = list(self.graph.predecessors(start_node_id))
        
        for pred_id in predecessors:
            edge_data = self.graph.get_edge_data(pred_id, start_node_id)
            if edge_data.get('relationship') == RelationshipType.DEPENDS_ON.value:
                affected_nodes.append(pred_id)
                # Recursively find dependencies
                affected_nodes.extend(self.detect_cascading_failures(pred_id))
        
        return list(set(affected_nodes))  # Remove duplicates
    
    def get_bottleneck_clusters(self) -> List[List[str]]:
        """
        Identify clusters of related bottlenecks.
        Useful for understanding systemic issues.
        """
        bottleneck_nodes = [
            node_id for node_id, node in self.nodes.items()
            if node.node_type == NodeType.BOTTLENECK
        ]
        
        if not bottleneck_nodes:
            return []
        
        # Create subgraph with only bottleneck nodes
        subgraph = self.graph.subgraph(bottleneck_nodes)
        
        # Find connected components
        clusters = list(nx.connected_components(subgraph.to_undirected()))
        
        return [list(cluster) for cluster in clusters]
    
    def get_high_impact_solutions(self, min_impact: float = 0.8) -> List[Dict]:
        """
        Get solutions that have high impact across multiple bottlenecks.
        """
        solution_impacts = {}
        
        for edge_id, edge in self.edges.items():
            if edge.relationship_type == RelationshipType.SOLVES:
                if edge.target_id not in solution_impacts:
                    solution_impacts[edge.target_id] = {
                        'solved_count': 0,
                        'total_strength': 0.0,
                        'bottlenecks': []
                    }
                
                solution_impacts[edge.target_id]['solved_count'] += 1
                solution_impacts[edge.target_id]['total_strength'] += edge.strength
                solution_impacts[edge.target_id]['bottlenecks'].append(edge.source_id)
        
        # Calculate average impact
        high_impact_solutions = []
        for solution_id, impact_data in solution_impacts.items():
            if impact_data['solved_count'] > 0:
                avg_strength = impact_data['total_strength'] / impact_data['solved_count']
                if avg_strength >= min_impact:
                    solution_node = self.nodes.get(solution_id)
                    if solution_node:
                        high_impact_solutions.append({
                            'solution_id': solution_id,
                            'properties': solution_node.properties,
                            'solved_count': impact_data['solved_count'],
                            'average_effectiveness': avg_strength,
                            'bottlenecks_solved': impact_data['bottlenecks']
                        })
        
        # Sort by total impact
        high_impact_solutions.sort(
            key=lambda x: x['solved_count'] * x['average_effectiveness'],
            reverse=True
        )
        
        return high_impact_solutions
    
    def validate_relationship(self, edge_id: str, validated: bool):
        """Mark a relationship as validated or invalid."""
        if edge_id in self.edges:
            self.edges[edge_id].validated = validated
            self.save_graph()
    
    def get_graph_statistics(self) -> Dict:
        """Get comprehensive statistics about the knowledge graph."""
        node_type_counts = {}
        for node in self.nodes.values():
            node_type_counts[node.node_type.value] = node_type_counts.get(node.node_type.value, 0) + 1
        
        relationship_type_counts = {}
        for edge in self.edges.values():
            rel_type = edge.relationship_type.value
            relationship_type_counts[rel_type] = relationship_type_counts.get(rel_type, 0) + 1
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_type_distribution': node_type_counts,
            'relationship_type_distribution': relationship_type_counts,
            'average_confidence': sum(n.confidence for n in self.nodes.values()) / len(self.nodes) if self.nodes else 0,
            'high_confidence_nodes': sum(1 for n in self.nodes.values() if n.confidence > 0.8)
        }
    
    def save_graph(self):
        """Save knowledge graph to disk."""
        data = {
            'nodes': {k: v.to_dict() for k, v in self.nodes.items()},
            'edges': {k: v.to_dict() for k, v in self.edges.items()},
            'graph_data': nx.node_link_data(self.graph)
        }
        
        with open(self.storage_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load_graph(self):
        """Load knowledge graph from disk."""
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
            
            # Reconstruct nodes
            for node_id, node_data in data.get('nodes', {}).items():
                self.nodes[node_id] = KnowledgeNode(**node_data)
            
            # Reconstruct edges
            for edge_id, edge_data in data.get('edges', {}).items():
                self.edges[edge_id] = KnowledgeEdge(**edge_data)
            
            # Reconstruct graph
            graph_data = data.get('graph_data', {})
            if graph_data:
                self.graph = nx.node_link_graph(graph_data)
                
        except FileNotFoundError:
            # First run - initialize empty graph
            self.graph = nx.DiGraph()
            self.nodes = {}
            self.edges = {}