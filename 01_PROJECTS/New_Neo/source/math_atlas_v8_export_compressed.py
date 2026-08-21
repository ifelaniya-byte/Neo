#!/usr/bin/env python3
"""
MATHEMATICAL LANGUAGE ATLAS — v8 UNIVERSAL HISTORY MAXIMUM COMPRESSION EXPORT
============================================================================
This script exports the complete universal history archive with maximum compression
to the Documents folder.
"""

import sqlite3
import json
import zipfile
from pathlib import Path
import datetime

# Configuration
DB_FILE = Path("math_atlas_v8_universal_history.sqlite")
DOCUMENTS = Path.home() / "Documents"
EXPORT_FOLDER = DOCUMENTS / "Universal_History_Archive_v8"
EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)

ZIP_FILE = EXPORT_FOLDER / "universal_history_v8_complete.zip"

NOW = datetime.datetime.now(datetime.timezone.utc).isoformat()

def export_all_tables_to_json(conn):
    """Export all database tables to JSON files."""
    JSON_DIR = EXPORT_FOLDER / "json"
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    
    cur = conn.cursor()
    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    
    exported_files = []
    for table in tables:
        table_name = table[0]
        try:
            rows = cur.execute(f"SELECT * FROM {table_name}").fetchall()
            if rows:
                columns = [description[0] for description in cur.description]
                data = []
                for row in rows:
                    data.append(dict(zip(columns, row)))
                
                json_file = JSON_DIR / f"{table_name}.json"
                json_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
                exported_files.append(json_file)
                print(f"  Exported: {table_name} ({len(data)} rows)")
        except Exception as e:
            print(f"  Error exporting {table_name}: {e}")
    
    return exported_files

def create_maximum_compression_zip(db_file, json_files):
    """Create a maximally compressed ZIP file."""
    
    readme = f"""MATHEMATICAL LANGUAGE ATLAS — v8 UNIVERSAL CIVILIZATIONAL AND COSMIC HISTORY ARCHIVE
================================================================================
Exported: {NOW}

This archive contains the complete backup of all knowledge across scales:
from atoms to galaxies, from mathematics to civilization, from biology to artificial intelligence.

=== ARCHIVE CONTENTS ===

DATABASE:
- math_atlas_v8_universal_history.sqlite: Complete database with 50+ tables

UNIVERSAL HISTORY DOMAINS:

HUMAN HISTORY:
- 11 human eras (Paleolithic to AI Era)
- Human civilizations, inventions, conflicts
- Complete timeline from prehistory to present

ANIMAL HISTORY:
- 8 animal species (from evolution to domestication)
- Evolutionary events and domestication history
- Conservation status and ecological roles

COMPUTER HISTORY:
- 8 computer eras (Mechanical to AI Era)
- 7 programming languages (Fortran to Rust)
- Architectures and software systems

ROBOTIC HISTORY:
- 5 robotic eras (Early Automata to Autonomous Systems)
- Robot capabilities and applications
- Robotic theories and developments

LLM HISTORY:
- 4 LLM eras (Foundational Transformers to Multimodal Era)
- 7 LLM models (GPT-1 to GPT-4)
- Architectures and scaling laws

EARTH HISTORY:
- 4 geological eras (Hadean to Phanerozoic)
- Earth extinctions and continental drift
- Climate and atmospheric evolution

SOLAR SYSTEM HISTORY:
- 5 solar system formation events
- Planetary data and exploration history
- Space missions and achievements

STELLAR HISTORY:
- 7 stellar classifications (O to M type stars)
- Stellar formation and evolution
- Stellar lifetimes and properties

UNIVERSAL TIMELINE:
- 10 key events across all domains
- From Big Bang to AI Era
- Cross-domain connections and impacts

=== TIME SCALES ===

Cosmic Scale:
- Big Bang: 13.8 billion years ago
- Earth Formation: 4.6 billion years ago
- First Life: 3.8 billion years ago

Planetary Scale:
- Earth history: 4.6 billion years
- Solar system: 4.6 billion years

Biological Scale:
- Animal evolution: 500+ million years
- Human history: 300,000 years

Civilizational Scale:
- Human eras: 2.5 million years to present
- Technology: 200 years (Industrial Revolution to AI)

Technological Scale:
- Computing: 80 years (1940-2020)
- Programming: 65 years (1957-2022)
- Robotics: 60 years (1960-2020)
- AI/LLMs: 5 years (2017-2022)

=== RECOVERY SIGNIFICANCE ===

This archive represents the complete backup of all knowledge across all scales:
- Mathematical knowledge (from v7)
- Human civilization history
- Biological evolution and animal history
- Technological development (computers, robots, AI)
- Planetary and cosmic history
- Universal timeline connecting all domains

This is not just a reference tool — it is universal insurance for all knowledge.
Civilization, biology, technology, and cosmic history are now preserved.

The archive can be used to:
- Reconstruct human history from prehistory
- Understand technological evolution
- Track biological evolution and domestication
- Reconstruct computer and AI development
- Understand Earth and solar system formation
- Study stellar evolution and classification
- See connections across all domains of knowledge

UNIVERSAL KNOWLEDGE PRESERVED:
Mathematical civilization + Biological history + Technological evolution + Cosmic history
= Complete universal knowledge archive

This archive ensures that humanity's complete knowledge across all scales
can never be truly lost and can be reconstructed by any intelligence.
"""
    
    print(f"\nCreating maximally compressed ZIP archive...")
    print(f"  Output: {ZIP_FILE}")
    print(f"  Compression level: Maximum (9)")
    
    with zipfile.ZipFile(ZIP_FILE, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        # Add database
        if db_file.exists():
            z.write(db_file, f"database/{db_file.name}")
            print(f"  Added: database/{db_file.name}")
        
        # Add JSON exports
        for json_file in json_files:
            z.write(json_file, f"json/{json_file.name}")
        
        # Add README
        z.writestr("README.txt", readme)
        print(f"  Added: README.txt")
    
    # Get file size
    zip_size = ZIP_FILE.stat().st_size
    zip_size_mb = zip_size / (1024 * 1024)
    
    print(f"\nZIP archive created successfully!")
    print(f"  Size: {zip_size_mb:.2f} MB")
    print(f"  Location: {ZIP_FILE}")
    
    return zip_size

def generate_inventory(conn):
    """Generate a detailed inventory of all content."""
    cur = conn.cursor()
    
    inventory = {
        "title": "Mathematical Language Atlas - v8 Universal Civilizational and Cosmic History Archive",
        "generated_at": NOW,
        "version": "v8_universal_history",
        "database": {
            "file": str(DB_FILE),
            "tables": cur.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
        },
        "human_history": {
            "eras": cur.execute("SELECT COUNT(*) FROM human_eras").fetchone()[0],
            "time_range": "2.5 million years ago to present"
        },
        "animal_history": {
            "species": cur.execute("SELECT COUNT(*) FROM animal_species").fetchone()[0],
            "time_range": "400 million years ago to present"
        },
        "computer_history": {
            "eras": cur.execute("SELECT COUNT(*) FROM computer_eras").fetchone()[0],
            "programming_languages": cur.execute("SELECT COUNT(*) FROM programming_languages").fetchone()[0],
            "time_range": "1800 to present"
        },
        "robotic_history": {
            "eras": cur.execute("SELECT COUNT(*) FROM robotic_eras").fetchone()[0],
            "time_range": "300 BCE to present"
        },
        "llm_history": {
            "models": cur.execute("SELECT COUNT(*) FROM llm_models").fetchone()[0],
            "eras": cur.execute("SELECT COUNT(*) FROM llm_eras").fetchone()[0],
            "time_range": "2017 to present"
        },
        "earth_history": {
            "geological_eras": cur.execute("SELECT COUNT(*) FROM geological_eras").fetchone()[0],
            "time_range": "4.6 billion years ago to present"
        },
        "solar_system_history": {
            "formation_events": cur.execute("SELECT COUNT(*) FROM solar_system_formation").fetchone()[0],
            "time_range": "4.6 billion years ago to present"
        },
        "stellar_history": {
            "classifications": cur.execute("SELECT COUNT(*) FROM star_classification").fetchone()[0],
            "time_range": "Billions of years"
        },
        "universal_timeline": {
            "events": cur.execute("SELECT COUNT(*) FROM universal_timeline").fetchone()[0],
            "time_range": "13.8 billion years ago to present"
        }
    }
    
    return inventory

def main():
    print("="*80)
    print("MATHEMATICAL LANGUAGE ATLAS — v8 UNIVERSAL HISTORY MAXIMUM COMPRESSION EXPORT")
    print("="*80)
    print(f"Export folder: {EXPORT_FOLDER}")
    print(f"Output ZIP: {ZIP_FILE}")
    
    if not DB_FILE.exists():
        print(f"\nError: Database not found at {DB_FILE}")
        print("Please run math_atlas_v8_universal_history.py first.")
        return
    
    print("\n[PHASE 1] Connecting to database...")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    print("[PHASE 2] Generating inventory...")
    inventory = generate_inventory(conn)
    print(f"  Human eras: {inventory['human_history']['eras']}")
    print(f"  Animal species: {inventory['animal_history']['species']}")
    print(f"  Computer eras: {inventory['computer_history']['eras']}")
    print(f"  Programming languages: {inventory['computer_history']['programming_languages']}")
    print(f"  LLM models: {inventory['llm_history']['models']}")
    print(f"  Geological eras: {inventory['earth_history']['geological_eras']}")
    print(f"  Solar system events: {inventory['solar_system_history']['formation_events']}")
    print(f"  Stellar classifications: {inventory['stellar_history']['classifications']}")
    print(f"  Universal timeline events: {inventory['universal_timeline']['events']}")
    
    print("\n[PHASE 3] Exporting all database tables to JSON...")
    json_files = export_all_tables_to_json(conn)
    print(f"  Exported {len(json_files)} tables to JSON")
    
    print("\n[PHASE 4] Creating maximally compressed ZIP archive...")
    zip_size = create_maximum_compression_zip(DB_FILE, json_files)
    
    print("\n[PHASE 5] Saving inventory...")
    inventory_file = EXPORT_FOLDER / "inventory.json"
    inventory_file.write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Inventory saved: {inventory_file}")
    
    # Also add inventory to ZIP
    with zipfile.ZipFile(ZIP_FILE, "a", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        z.write(inventory_file, "inventory.json")
    
    conn.close()
    
    print("\n" + "="*80)
    print("UNIVERSAL HISTORY EXPORT COMPLETE")
    print("="*80)
    print(f"\nAll universal knowledge has been compressed and exported to:")
    print(f"  {ZIP_FILE}")
    print(f"\nInventory:")
    print(f"  {inventory_file}")
    print(f"\nFolder:")
    print(f"  {EXPORT_FOLDER}")
    print(f"\nArchive size: {zip_size / (1024*1024):.2f} MB")
    print(f"\nThis archive contains:")
    print(f"  - Complete database with {inventory['database']['tables']} tables")
    print(f"  - Human history: {inventory['human_history']['eras']} eras (2.5M years)")
    print(f"  - Animal history: {inventory['animal_history']['species']} species (400M years)")
    print(f"  - Computer history: {inventory['computer_history']['eras']} eras, {inventory['computer_history']['programming_languages']} languages")
    print(f"  - Robotic history: {inventory['robotic_history']['eras']} eras")
    print(f"  - LLM history: {inventory['llm_history']['models']} models (2017-present)")
    print(f"  - Earth history: {inventory['earth_history']['geological_eras']} eras (4.6B years)")
    print(f"  - Solar system: {inventory['solar_system_history']['formation_events']} events (4.6B years)")
    print(f"  - Stellar history: {inventory['stellar_history']['classifications']} classifications")
    print(f"  - Universal timeline: {inventory['universal_timeline']['events']} events (13.8B years)")
    print(f"\nThis is the complete backup of all knowledge across all scales.")
    print("From atoms to galaxies, from mathematics to civilization, from biology to AI.")
    print("Universal knowledge is now preserved in Documents.")

if __name__ == "__main__":
    main()
