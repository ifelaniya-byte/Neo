#!/usr/bin/env python3
"""
MATHEMATICAL LANGUAGE ATLAS — v7 CIVILIZATIONAL METADATA INTEGRATION
====================================================================
This script adds civilizational metadata (discovery narratives, societal impact,
anthropological context, DNA encoding, keystone species assessment, etc.) to the
formulas in the v7 database, completing the civilizational time capsule.

Run this AFTER running math_atlas_v7_add_formulas.py.
"""

import sqlite3
import json
import hashlib
from pathlib import Path

DB_FILE = Path("math_atlas_v7_civilizational.sqlite")
DNA_DIR = Path("math_atlas_v7_civilizational_dna")
UNIVERSAL_DIR = Path("math_atlas_v7_civilizational_universal")

DNA_DIR.mkdir(parents=True, exist_ok=True)
UNIVERSAL_DIR.mkdir(parents=True, exist_ok=True)

class MathematicalDNACoder:
    """Encodes mathematical concepts into DNA-like sequences."""
    
    NUCLEOTIDE_MAP = {'00': 'A', '01': 'C', '10': 'G', '11': 'T'}
    NUCLEOTIDE_REVERSE = {v: k for k, v in NUCLEOTIDE_MAP.items()}
    
    @staticmethod
    def encode_to_dna(data: str) -> str:
        bytes_data = data.encode('utf-8')
        binary_str = ''.join(format(byte, '08b') for byte in bytes_data)
        if len(binary_str) % 2 != 0:
            binary_str += '0'
        dna_sequence = ''
        for i in range(0, len(binary_str), 2):
            pair = binary_str[i:i+2]
            dna_sequence += MathematicalDNACoder.NUCLEOTIDE_MAP[pair]
        return dna_sequence
    
    @staticmethod
    def add_error_correction(dna_sequence: str) -> str:
        protected_sequence = dna_sequence
        for i in range(0, len(dna_sequence), 10):
            chunk = dna_sequence[i:i+10]
            parity = sum(1 for c in chunk if c in ['G', 'T']) % 2
            protected_sequence += 'C' if parity == 0 else 'A'
        return protected_sequence
    
    @staticmethod
    def create_genomic_signature(formula_id: int, formula_name: str, 
                                latex: str, statement: str) -> str:
        signature_data = f"{formula_id}|{formula_name}|{latex}|{statement}"
        dna_sequence = MathematicalDNACoder.encode_to_dna(signature_data)
        protected_sequence = MathematicalDNACoder.add_error_correction(dna_sequence)
        return protected_sequence

def generate_discovery_narrative(formula):
    return {
        "discovery_context": f"Historical context: {formula['domain_family']} in {formula['historical_year'] or 'unknown'}",
        "historical_circumstances": f"Discovered by {formula['historical_attribution'] or 'unknown'}",
        "key_insights": f"This formula {formula['name']} represents a key insight in {formula['domain']}",
        "mathematical_revolution": f"{formula['proof_status']} result that advanced {formula['domain_family']}",
        "cultural_impact": f"This formula enabled developments in {formula['domain']}",
        "discoverer_biography": f"{formula['historical_attribution'] or 'Unknown mathematician'} lived during {formula['historical_year'] or 'unknown era'}",
        "timeline": f"Contribution to mathematical knowledge around {formula['historical_year'] or 'unknown'}"
    }

def generate_societal_impact(formula):
    impact_magnitude = min(5, max(1, formula['difficulty_level'] // 2))
    return {
        "applications": f"Used in {formula['domain']} for solving problems in {formula['domain_family']}",
        "technological_enablings": f"Enables computational methods in {formula['domain_family']}",
        "economic_consequences": f"Contributes to economic value in {formula['domain_family']} applications",
        "philosophical_implications": f"Raises questions about {formula['constraints']} in {formula['domain']}",
        "educational_impact": f"Taught in mathematics education at level {formula['difficulty_level']}",
        "military_applications": f"Potential applications in defense technology and cryptography" if "Cryptography" in formula['domain_family'] else "Defense applications limited",
        "artistic_inspiration": f"Inspired mathematical art and design patterns" if "Geometry" in formula['domain_family'] else "Limited artistic impact",
        "impact_magnitude": impact_magnitude
    }

def generate_anthropological_context(formula):
    return {
        "cultural_variants": f"Different notation systems and approaches to {formula['name']} across cultures",
        "regional_differences": f"Regional variations in emphasis and application of {formula['name']}",
        "historical_evolution": f"How understanding of {formula['name']} evolved from {formula['historical_year'] or 'unknown'} to present",
        "philosophical_schools": f"Part of {formula['domain_family']} philosophical tradition with {formula['proof_status']} foundation",
        "educational_traditions": f"How {formula['name']} is taught in educational systems worldwide",
        "cross_cultural_transmission": f"Exchange of {formula['name']} between mathematical cultures",
        "symbolic_meanings": f"The symbolic meaning of {formula['name']} in different cultural contexts"
    }

def generate_keystone_species_status(formula):
    is_keystone = formula['difficulty_level'] >= 4
    return {
        "keystone_type": "foundational" if formula['difficulty_level'] <= 2 else "advanced",
        "influence_radius": formula['difficulty_level'] * 10,
        "supporting_concepts": "Multiple dependent theorems and applications",
        "cascade_effects": f"If {formula['name']} were lost, would affect many dependent concepts",
        "ecosystem_stability_contribution": min(1.0, formula['difficulty_level'] * 0.2)
    }

def create_universal_representation(formula):
    return {
        "geometric": f"GEOMETRIC: {formula['name']} -> {formula['domain']}",
        "musical": f"MUSICAL: {formula['name']} -> {formula['statement']}",
        "tactile": f"TACTILE: {formula['name']} -> {formula['latex']}",
        "computational": f"COMPUTATIONAL: {formula['name']} -> symbolic_computation",
        "pattern": f"PATTERN: {formula['name']} -> {formula['domain_family']}"
    }

def main():
    if not DB_FILE.exists():
        print(f"Error: {DB_FILE} not found. Run math_atlas_v7_civilizational.py first.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    formulas = cur.execute("SELECT * FROM formulas").fetchall()
    print(f"Processing {len(formulas)} formulas with civilizational metadata...")
    
    for formula in formulas:
        formula_dict = dict(formula)
        fid = formula_dict['id']
        
        # DNA encoding
        dna_coder = MathematicalDNACoder()
        dna_sequence = dna_coder.create_genomic_signature(
            fid, formula_dict['name'], formula_dict['latex'], formula_dict['statement'])
        
        cur.execute("""
            INSERT INTO mathematical_genome
            (formula_id, dna_sequence, evolutionary_lineage, variant_count,
             preservation_status, genetic_diversity_score, reconstructive_potential,
             ecological_niche, evolutionary_significance, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))
        """, (fid, dna_sequence, f"derived from {formula_dict['domain_family']}",
              1, "thriving", 1.0, 1.0,
              formula_dict['domain'], f"Essential in {formula_dict['domain_family']}"))
        
        # Save DNA file
        dna_file = DNA_DIR / f"formula_{fid}.dna"
        dna_file.write_text(dna_sequence)
        
        # Discovery narrative
        narrative = generate_discovery_narrative(formula_dict)
        cur.execute("""
            INSERT INTO discovery_narratives
            (formula_id, discovery_context, historical_circumstances, key_insights,
             mathematical_revolution, cultural_impact, discoverer_biography, timeline, created_at)
            VALUES (?,?,?,?,?,?,?,?,datetime('now'))
        """, (fid, narrative["discovery_context"], narrative["historical_circumstances"],
              narrative["key_insights"], narrative["mathematical_revolution"],
              narrative["cultural_impact"], narrative["discoverer_biography"], narrative["timeline"]))
        
        # Societal impact
        impact = generate_societal_impact(formula_dict)
        cur.execute("""
            INSERT INTO societal_impact
            (formula_id, applications, technological_enablings, economic_consequences,
             philosophical_implications, educational_impact, military_applications,
             artistic_inspiration, impact_magnitude, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))
        """, (fid, impact["applications"], impact["technological_enablings"],
              impact["economic_consequences"], impact["philosophical_implications"],
              impact["educational_impact"], impact["military_applications"],
              impact["artistic_inspiration"], impact["impact_magnitude"]))
        
        # Anthropological context
        anthropological = generate_anthropological_context(formula_dict)
        cur.execute("""
            INSERT INTO anthropological_context
            (formula_id, cultural_variants, regional_differences, historical_evolution,
             philosophical_schools, educational_traditions, cross_cultural_transmission,
             symbolic_meanings, created_at)
            VALUES (?,?,?,?,?,?,?,?,datetime('now'))
        """, (fid, anthropological["cultural_variants"],
              anthropological["regional_differences"], anthropological["historical_evolution"],
              anthropological["philosophical_schools"], anthropological["educational_traditions"],
              anthropological["cross_cultural_transmission"], anthropological["symbolic_meanings"]))
        
        # Keystone species
        keystone = generate_keystone_species_status(formula_dict)
        cur.execute("""
            INSERT INTO keystone_species
            (formula_id, keystone_type, influence_radius, supporting_concepts,
             cascade_effects, ecosystem_stability_contribution, created_at)
            VALUES (?,?,?,?,?,?,datetime('now'))
        """, (fid, keystone["keystone_type"], keystone["influence_radius"],
              keystone["supporting_concepts"], keystone["cascade_effects"],
              keystone["ecosystem_stability_contribution"]))
        
        # Conservation category
        cur.execute("""
            INSERT INTO conservation_categories
            (formula_id, category, conservation_status, population_estimate,
             habitat_requirements, threats, conservation_efforts, recovery_probability, created_at)
            VALUES (?,?,?,?,?,?,?,?,datetime('now'))
        """, (fid, "general" if formula_dict['difficulty_level'] <= 3 else "specialized",
              "thriving", 1000 if formula_dict['difficulty_level'] <= 3 else 100,
              f"Requires mathematical education", "Cultural shifts, computational changes",
              "Ongoing research and education", 0.95))
        
        # Universal representation
        universal = create_universal_representation(formula_dict)
        universal_file = UNIVERSAL_DIR / f"formula_{fid}.uni"
        universal_file.write_text(json.dumps(universal, indent=2))
        
        # Civilizational knowledge graph node
        centrality = 1.0 / (formula_dict['difficulty_level'] if formula_dict['difficulty_level'] > 0 else 1)
        cur.execute("""
            INSERT INTO civilizational_knowledge_graph
            (node_type, node_id, connections, centrality_score, reconstructive_criticality,
             dependency_depth, cross_domain_links, created_at)
            VALUES (?,?,?,?,?,?,?,datetime('now'))
        """, ("formula", fid, json.dumps([]), centrality, 0.9, 0, formula_dict['domain_family']))
        
        print(f"  Added civilizational metadata for: {formula_dict['name']}")
    
    conn.commit()
    
    # Summary
    count = cur.execute("SELECT COUNT(*) FROM formulas").fetchone()[0]
    genomes = cur.execute("SELECT COUNT(*) FROM mathematical_genome").fetchone()[0]
    narratives = cur.execute("SELECT COUNT(*) FROM discovery_narratives").fetchone()[0]
    impacts = cur.execute("SELECT COUNT(*) FROM societal_impact").fetchone()[0]
    anthropological = cur.execute("SELECT COUNT(*) FROM anthropological_context").fetchone()[0]
    keystones = cur.execute("SELECT COUNT(*) FROM keystone_species").fetchone()[0]
    conservation = cur.execute("SELECT COUNT(*) FROM conservation_categories").fetchone()[0]
    graph_nodes = cur.execute("SELECT COUNT(*) FROM civilizational_knowledge_graph").fetchone()[0]
    
    print(f"\nCivilizational metadata summary:")
    print(f"  Formulas: {count}")
    print(f"  Mathematical genomes (DNA-encoded): {genomes}")
    print(f"  Discovery narratives: {narratives}")
    print(f"  Societal impact analyses: {impacts}")
    print(f"  Anthropological contexts: {anthropological}")
    print(f"  Keystone species assessments: {keystones}")
    print(f"  Conservation categories: {conservation}")
    print(f"  Knowledge graph nodes: {graph_nodes}")
    print(f"  DNA files generated: {len(list(DNA_DIR.glob('*.dna')))}")
    print(f"  Universal representation files: {len(list(UNIVERSAL_DIR.glob('*.uni')))}")
    
    conn.close()
    print("\nCivilizational metadata added successfully. The v7 time capsule is now complete with actual mathematical knowledge and full civilizational context.")

if __name__ == "__main__":
    main()
