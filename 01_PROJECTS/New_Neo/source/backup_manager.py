"""
PROJECT APEX: BACKUP & ROLLBACK MANAGER
Provides comprehensive backup and rollback capabilities.
Ensures system can recover from any failed optimization.
"""

import os
import shutil
import json
import time
import hashlib
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

@dataclass
class BackupSnapshot:
    snapshot_id: str
    timestamp: str
    description: str
    files_backed_up: List[str]
    file_hashes: Dict[str, str]
    metadata: Dict
    size_bytes: int
    
    def to_dict(self):
        return asdict(self)

class BackupManager:
    """
    Comprehensive backup and rollback system.
    Creates snapshots before any changes and enables instant rollback.
    """
    
    def __init__(self, backup_dir="backups", max_snapshots=50):
        self.backup_dir = Path(backup_dir)
        self.max_snapshots = max_snapshots
        self.snapshots = {}
        self.current_snapshot_id = None
        
        # Create backup directory
        self.backup_dir.mkdir(exist_ok=True)
        
        # Load existing snapshots
        self.load_snapshots()
    
    def create_snapshot(self, files_to_backup: List[str], 
                       description: str = "Automated backup") -> str:
        """
        Create a backup snapshot of specified files.
        Returns snapshot ID.
        """
        snapshot_id = self._generate_snapshot_id()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Create snapshot directory
        snapshot_path = self.backup_dir / snapshot_id
        snapshot_path.mkdir(exist_ok=True)
        
        file_hashes = {}
        total_size = 0
        
        # Backup each file
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                # Calculate file hash
                file_hash = self._calculate_file_hash(file_path)
                file_hashes[file_path] = file_hash
                
                # Copy file to backup
                backup_path = snapshot_path / os.path.basename(file_path)
                shutil.copy2(file_path, backup_path)
                
                total_size += os.path.getsize(file_path)
        
        # Create snapshot metadata
        snapshot = BackupSnapshot(
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            description=description,
            files_backed_up=files_to_backup,
            file_hashes=file_hashes,
            metadata={
                'system_state': self._capture_system_state(),
                'git_commit': self._get_git_commit()
            },
            size_bytes=total_size
        )
        
        self.snapshots[snapshot_id] = snapshot
        self.current_snapshot_id = snapshot_id
        
        # Save snapshot metadata
        self._save_snapshot_metadata(snapshot, snapshot_path)
        
        # Cleanup old snapshots if needed
        self._cleanup_old_snapshots()
        
        return snapshot_id
    
    def restore_snapshot(self, snapshot_id: str, 
                        files_to_restore: List[str] = None) -> bool:
        """
        Restore files from a snapshot.
        Returns True if successful.
        """
        if snapshot_id not in self.snapshots:
            print(f"[BACKUP] Snapshot {snapshot_id} not found")
            return False
        
        snapshot = self.snapshots[snapshot_id]
        snapshot_path = self.backup_dir / snapshot_id
        
        if not snapshot_path.exists():
            print(f"[BACKUP] Snapshot directory not found")
            return False
        
        # Determine which files to restore
        if files_to_restore is None:
            files_to_restore = snapshot.files_backed_up
        
        # Restore each file
        restored_count = 0
        for file_path in files_to_restore:
            backup_path = snapshot_path / os.path.basename(file_path)
            
            if backup_path.exists():
                # Create backup of current file before restoring
                if os.path.exists(file_path):
                    temp_backup = f"{file_path}.temp_backup"
                    shutil.copy2(file_path, temp_backup)
                
                try:
                    shutil.copy2(backup_path, file_path)
                    restored_count += 1
                    
                    # Verify hash
                    current_hash = self._calculate_file_hash(file_path)
                    if current_hash != snapshot.file_hashes.get(file_path):
                        print(f"[BACKUP] Hash mismatch for {file_path}")
                        # Restore from temp backup if exists
                        if os.path.exists(f"{file_path}.temp_backup"):
                            shutil.copy2(f"{file_path}.temp_backup", file_path)
                    
                    # Clean up temp backup
                    if os.path.exists(f"{file_path}.temp_backup"):
                        os.remove(f"{file_path}.temp_backup")
                        
                except Exception as e:
                    print(f"[BACKUP] Error restoring {file_path}: {e}")
                    # Restore from temp backup if exists
                    if os.path.exists(f"{file_path}.temp_backup"):
                        shutil.copy2(f"{file_path}.temp_backup", file_path)
        
        print(f"[BACKUP] Restored {restored_count}/{len(files_to_restore)} files")
        return restored_count == len(files_to_restore)
    
    def create_incremental_backup(self, base_snapshot_id: str, 
                                  changed_files: List[str],
                                  description: str = "Incremental backup") -> str:
        """
        Create incremental backup based on a previous snapshot.
        Only stores files that have changed.
        """
        if base_snapshot_id not in self.snapshots:
            print(f"[BACKUP] Base snapshot {base_snapshot_id} not found")
            return None
        
        base_snapshot = self.snapshots[base_snapshot_id]
        
        # Filter to only changed files
        changed_files_filtered = []
        for file_path in changed_files:
            if file_path in base_snapshot.file_hashes:
                current_hash = self._calculate_file_hash(file_path)
                if current_hash != base_snapshot.file_hashes[file_path]:
                    changed_files_filtered.append(file_path)
            else:
                changed_files_filtered.append(file_path)
        
        if not changed_files_filtered:
            print("[BACKUP] No files changed, skipping incremental backup")
            return base_snapshot_id
        
        # Create snapshot with only changed files
        snapshot_id = self.create_snapshot(changed_files_filtered, description)
        
        # Update metadata to reference base snapshot
        if snapshot_id:
            self.snapshots[snapshot_id].metadata['base_snapshot'] = base_snapshot_id
            self.snapshots[snapshot_id].metadata['backup_type'] = 'incremental'
        
        return snapshot_id
    
    def compare_snapshots(self, snapshot_id1: str, snapshot_id2: str) -> Dict:
        """
        Compare two snapshots and return differences.
        """
        if snapshot_id1 not in self.snapshots or snapshot_id2 not in self.snapshots:
            return {}
        
        snap1 = self.snapshots[snapshot_id1]
        snap2 = self.snapshots[snapshot_id2]
        
        differences = {
            'added_files': [],
            'removed_files': [],
            'modified_files': [],
            'unchanged_files': []
        }
        
        all_files = set(snap1.files_backed_up) | set(snap2.files_backed_up)
        
        for file_path in all_files:
            hash1 = snap1.file_hashes.get(file_path)
            hash2 = snap2.file_hashes.get(file_path)
            
            if hash1 and not hash2:
                differences['removed_files'].append(file_path)
            elif not hash1 and hash2:
                differences['added_files'].append(file_path)
            elif hash1 != hash2:
                differences['modified_files'].append(file_path)
            else:
                differences['unchanged_files'].append(file_path)
        
        return differences
    
    def get_snapshot_info(self, snapshot_id: str) -> Optional[Dict]:
        """Get detailed information about a snapshot."""
        if snapshot_id not in self.snapshots:
            return None
        
        snapshot = self.snapshots[snapshot_id]
        return {
            'snapshot_id': snapshot.snapshot_id,
            'timestamp': snapshot.timestamp,
            'description': snapshot.description,
            'files_count': len(snapshot.files_backed_up),
            'size_mb': snapshot.size_bytes / (1024 * 1024),
            'metadata': snapshot.metadata
        }
    
    def list_snapshots(self, limit: int = 10) -> List[Dict]:
        """List recent snapshots."""
        sorted_snapshots = sorted(
            self.snapshots.values(),
            key=lambda s: s.timestamp,
            reverse=True
        )
        
        return [
            self.get_snapshot_info(s.snapshot_id)
            for s in sorted_snapshots[:limit]
        ]
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a snapshot."""
        if snapshot_id not in self.snapshots:
            return False
        
        snapshot_path = self.backup_dir / snapshot_id
        
        try:
            if snapshot_path.exists():
                shutil.rmtree(snapshot_path)
            
            del self.snapshots[snapshot_id]
            return True
            
        except Exception as e:
            print(f"[BACKUP] Error deleting snapshot: {e}")
            return False
    
    def rollback_to_safe_state(self) -> Optional[str]:
        """
        Rollback to the last known safe state.
        Returns snapshot ID used for rollback.
        """
        # Find most recent snapshot marked as safe
        for snapshot_id in sorted(self.snapshots.keys(), reverse=True):
            snapshot = self.snapshots[snapshot_id]
            if snapshot.metadata.get('safe_state', False):
                if self.restore_snapshot(snapshot_id):
                    return snapshot_id
        
        # If no marked safe state, use most recent snapshot
        if self.snapshots:
            most_recent = max(self.snapshots.keys(), 
                             key=lambda k: self.snapshots[k].timestamp)
            if self.restore_snapshot(most_recent):
                return most_recent
        
        return None
    
    def mark_snapshot_safe(self, snapshot_id: str, safe: bool = True):
        """Mark a snapshot as safe or unsafe."""
        if snapshot_id in self.snapshots:
            self.snapshots[snapshot_id].metadata['safe_state'] = safe
            self._save_snapshot_metadata(self.snapshots[snapshot_id], 
                                        self.backup_dir / snapshot_id)
    
    def _generate_snapshot_id(self) -> str:
        """Generate unique snapshot ID."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_suffix = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        return f"snapshot_{timestamp}_{random_suffix}"
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _capture_system_state(self) -> Dict:
        """Capture current system state metadata."""
        import psutil
        
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
            'timestamp': time.time()
        }
    
    def _get_git_commit(self) -> str:
        """Get current git commit hash."""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return "unknown"
    
    def _save_snapshot_metadata(self, snapshot: BackupSnapshot, snapshot_path: Path):
        """Save snapshot metadata to file."""
        metadata_path = snapshot_path / "metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(snapshot.to_dict(), f, indent=2, default=str)
    
    def _cleanup_old_snapshots(self):
        """Remove old snapshots if we exceed max limit."""
        if len(self.snapshots) <= self.max_snapshots:
            return
        
        # Sort by timestamp and remove oldest
        sorted_snapshots = sorted(
            self.snapshots.keys(),
            key=lambda k: self.snapshots[k].timestamp
        )
        
        snapshots_to_remove = sorted_snapshots[:len(self.snapshots) - self.max_snapshots]
        
        for snapshot_id in snapshots_to_remove:
            self.delete_snapshot(snapshot_id)
    
    def load_snapshots(self):
        """Load existing snapshots from backup directory."""
        if not self.backup_dir.exists():
            return
        
        for snapshot_dir in self.backup_dir.iterdir():
            if snapshot_dir.is_dir():
                metadata_path = snapshot_dir / "metadata.json"
                if metadata_path.exists():
                    try:
                        with open(metadata_path, 'r') as f:
                            data = json.load(f)
                        
                        snapshot = BackupSnapshot(**data)
                        self.snapshots[snapshot.snapshot_id] = snapshot
                        
                    except Exception as e:
                        print(f"[BACKUP] Error loading snapshot {snapshot_dir.name}: {e}")
    
    def get_backup_statistics(self) -> Dict:
        """Get statistics about backup system."""
        total_size = sum(s.size_bytes for s in self.snapshots.values())
        
        return {
            'total_snapshots': len(self.snapshots),
            'total_size_mb': total_size / (1024 * 1024),
            'oldest_snapshot': min((s.timestamp for s in self.snapshots.values()), default=None),
            'newest_snapshot': max((s.timestamp for s in self.snapshots.values()), default=None),
            'max_snapshots': self.max_snapshots
        }