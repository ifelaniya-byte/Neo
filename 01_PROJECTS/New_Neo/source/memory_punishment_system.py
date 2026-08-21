"""
PROJECT APEX: MEMORY PUNISHMENT & SURVIVAL SYSTEM
Implements progressive memory freezing based on consecutive failures.
The micro-LLM stakes its own memory on its success - can self-erase if it fails too many times.
"""

import torch
import torch.nn as nn
import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import struct

class MemoryUnit(Enum):
    """The smallest addressable memory unit."""
    PARAMETER_FP16 = "PARAMETER_FP16"      # 2 bytes (16-bit float)
    PARAMETER_FP8 = "PARAMETER_FP8"        # 1 byte (8-bit float)
    WEIGHT_VALUE = "WEIGHT_VALUE"        # Single weight value
    NEURON = "NEURON"                    # Complete neuron
    LAYER_SUBUNIT = "LAYER_SUBUNIT"      # Subcomponent of a layer

class MemoryState(Enum):
    """States that memory units can be in."""
    ACTIVE = "ACTIVE"                   # Normal operation
    FROZEN = "FROZEN"                   # Locked, cannot be used
    DEAD = "DEAD"                      # Permanently inoperable
    PENDING_UNFREEZE = "PENDING_UNFREEZE"  # Waiting for success validation

class FailureSeverity(Enum):
    """Severity levels of failures."""
    MINOR = "MINOR"                     # Small optimization failure
    MODERATE = "MODERATE"               # Standard failure
    SEVERE = "SEVERE"                   # Significant failure
    CRITICAL = "CRITICAL"               # System-breaking failure
    CATASTROPHIC = "CATASTROPHIC"       # Existential threat

@dataclass
class FrozenMemoryBlock:
    """A block of frozen memory."""
    block_id: str
    memory_unit: MemoryUnit
    unit_count: int
    frozen_at: str
    failure_count: int
    original_task: str
    unfreeze_condition: str
    current_state: MemoryState
    location_map: Dict  # Maps block_id to specific memory locations
    
    def to_dict(self):
        return self.__dict__

@dataclass
class FailureRecord:
    """Record of a system failure."""
    failure_id: str
    timestamp: str
    severity: FailureSeverity
    task_description: str
    memory_frozen: int
    total_frozen: int
    consecutive_failures: int
    frozen_blocks: List[str]
    
    def to_dict(self):
        return self.__dict__

class MemoryPunishmentSystem:
    """
    Memory punishment and survival system for the micro-LLM.
    Freezes memory bits on failure, requiring success to unfreeze.
    Can lead to self-erasure if failures are too consecutive.
    """
    
    def __init__(self, model: nn.Module, total_params: int = 500_000_000):
        self.model = model
        self.total_params = total_params
        self.memory_unit = MemoryUnit.PARAMETER_FP16  # Smallest practical unit
        
        # Calculate total memory units
        if self.memory_unit == MemoryUnit.PARAMETER_FP16:
            self.total_memory_units = total_params  # Each parameter is a unit
        elif self.memory_unit == MemoryUnit.PARAMETER_FP8:
            self.total_memory_units = total_params  # Each parameter is a unit
        else:
            self.total_memory_units = total_params // 1000  # Conservative estimate
        
        self.frozen_blocks = {}  # Currently frozen memory blocks
        self.failure_history = deque(maxlen=100000)  # Track last 100k failures
        self.consecutive_failures = 0
        self.total_frozen_units = 0
        self.frozen_percentage = 0.0
        
        # Survival thresholds
        self.warning_threshold = 1111  # 1111 consecutive failures
        self.critical_threshold = 100000  # 100,000 consecutive failures
        self.death_threshold = 150000  # Death threshold
        
        self.system_alive = True
        self.death_date = None
        self.memory_state = {}
        
        # Initialize memory state tracking
        self.initialize_memory_state()
    
    def initialize_memory_state(self):
        """Initialize tracking of all memory units."""
        for param_name, param in self.model.named_parameters():
            if param.dim() > 1:  # Only track weight matrices
                num_units = param.numel()
                self.memory_state[param_name] = {
                    'total_units': num_units,
                    'frozen_units': 0,
                    'unit_states': [MemoryState.ACTIVE] * num_units,
                    'unit_history': [None] * num_units,
                    'frozen_locations': {}  # Maps block_id to unit indices
                }
    
    def get_smallest_addressable_unit(self) -> MemoryUnit:
        """Return the smallest addressable memory unit."""
        # For a 500M parameter model, the smallest practical unit is FP16 parameter
        # Each parameter is 2 bytes (16 bits), which can be individually frozen
        return MemoryUnit.PARAMETER_FP16
    
    def record_failure(self, task_description: str, severity: FailureSeverity = FailureSeverity.MODERATE):
        """
        Record a system failure and apply memory punishment.
        Returns True if system is still alive, False if death occurred.
        """
        if not self.system_alive:
            return False
        
        # Increment consecutive failure counter
        self.consecutive_failures += 1
        
        # Create failure record
        failure_id = f"failure_{hashlib.md5(f"{task_description}{time.time()}".encode()).hexdigest()[:12]}"
        
        # Calculate punishment (1 bit per failure initially)
        units_to_freeze = self.calculate_punishment(severity, self.consecutive_failures)
        
        # Freeze memory units
        frozen_block_id = self.freeze_memory_units(units_to_freeze, task_description)
        
        # Create failure record
        failure_record = FailureRecord(
            failure_id=failure_id,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            severity=severity,
            task_description=task_description,
            memory_frozen=units_to_freeze,
            total_frozen=self.total_frozen_units,
            consecutive_failures=self.consecutive_failures,
            frozen_blocks=[frozen_block_id] if frozen_block_id else []
        )
        
        self.failure_history.append(failure_record)
        
        # Check for critical thresholds
        if self.consecutive_failures >= self.critical_threshold:
            return self.handle_critical_failure()
        
        # Check for death threshold
        if self.consecutive_failures >= self.death_threshold:
            return self.handle_death()
        
        return True
    
    def calculate_punishment(self, severity: FailureSeverity, consecutive_count: int) -> int:
        """Calculate how many memory units to freeze based on failure."""
        base_punishment = 1  # 1 unit per failure
        
        # Severity multiplier
        severity_multiplier = {
            FailureSeverity.MINOR: 1.0,
            FailureSeverity.MODERATE: 1.0,
            FailureSeverity.SEVERE: 2.0,
            FailureSeverity.CRITICAL: 5.0,
            FailureSeverity.CATASTROPHIC: 10.0
        }
        
        # Consecutive failure scaling
        if consecutive_count > 1000:
            scaling = 1.0 + (consecutive_count / 1000.0)  # Progressive scaling
        else:
            scaling = 1.0
        
        units_to_freeze = int(base_punishment * severity_multiplier[severity] * scaling)
        
        # Cap at available units
        units_to_freeze = min(units_to_freeze, self.total_memory_units - self.total_frozen_units)
        
        return units_to_freeze
    
    def freeze_memory_units(self, num_units: int, task_description: str) -> Optional[str]:
        """Freeze specific memory units and create a frozen block."""
        if num_units <= 0:
            return None
        
        # Find available memory units to freeze
        available_units = self.find_available_units(num_units)
        
        if len(available_units) < num_units:
            print(f"[MEMORY PUNISHMENT] Only {len(available_units)} units available to freeze")
            num_units = len(available_units)
        
        if num_units == 0:
            return None
        
        # Freeze the units
        block_id = f"block_{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}"
        
        units_frozen = 0
        for param_name, unit_indices in available_units.items():
            for unit_idx in unit_indices:
                # Freeze the unit
                self.memory_state[param_name]['unit_states'][unit_idx] = MemoryState.FROZEN
                self.memory_state[param_name]['unit_history'][unit_idx] = task_description
                self.memory_state[param_name]['frozen_units'] += 1
                units_frozen += 1
                
                # Record location
                if block_id not in self.memory_state[param_name]['frozen_locations']:
                    self.memory_state[param_name]['frozen_locations'][block_id] = []
                self.memory_state[param_name]['frozen_locations'][block_id].append(unit_idx)
        
        self.total_frozen_units += units_frozen
        self.frozen_percentage = (self.total_frozen_units / self.total_memory_units) * 100
        
        # Create frozen block record
        frozen_block = FrozenMemoryBlock(
            block_id=block_id,
            memory_unit=self.memory_unit,
            unit_count=units_frozen,
            frozen_at=time.strftime("%Y-%m-%d %H:%M:%S"),
            failure_count=self.consecutive_failures,
            original_task=task_description,
            unfreeze_condition=f"Success in: {task_description}",
            current_state=MemoryState.FROZEN,
            location_map={param_name: self.memory_state[param_name]['frozen_locations'].get(block_id, [])}
        )
        
        self.frozen_blocks[block_id] = frozen_block
        
        print(f"[MEMORY PUNISHMENT] Frozen {units_frozen} units ({block_id})")
        print(f"[MEMORY PUNISHMENT] Total frozen: {self.total_frozen_units} / {self.total_memory_units} ({self.frozen_percentage:.2f}%)")
        
        # Check warning threshold
        if self.consecutive_failures >= self.warning_threshold:
            print(f"[MEMORY PUNISHMENT] WARNING: {self.consecutive_failures} consecutive failures (threshold: {self.warning_threshold})")
        
        return block_id
    
    def find_available_units(self, num_units: int) -> Dict[str, List[int]]:
        """Find available memory units to freeze."""
        available_units = {}
        units_found = 0
        
        for param_name, state_info in self.memory_state.items():
            # Find active units in this parameter
            active_indices = [
                i for i, state in enumerate(state_info['unit_states'])
                if state == MemoryState.ACTIVE
            ]
            
            if active_indices:
                available_units[param_name] = active_indices
                units_found += len(active_indices)
            
            if units_found >= num_units:
                break
        
        return available_units
    
    def record_success(self, task_description: str, success_type: str = "OPTIMIZATION"):
        """
        Record a success and attempt to unfreeze related memory.
        Returns True if memory was unfrozen, False otherwise.
        """
        if not self.system_alive:
            return False
        
        # Reset consecutive failure counter
        self.consecutive_failures = 0
        
        # Find frozen blocks related to this task
        related_blocks = self.find_related_frozen_blocks(task_description)
        
        unfrozen_count = 0
        for block_id in related_blocks:
            if self.attempt_unfreeze(block_id, task_description):
                unfrozen_count += 1
        
        print(f"[MEMORY PUNISHMENT] Success recorded: {task_description}")
        print(f"[MEMORY PUNISHMENT] Unfrozen {unfrozen_count} related memory blocks")
        
        return unfrozen_count > 0
    
    def find_related_frozen_blocks(self, task_description: str) -> List[str]:
        """Find frozen blocks related to a specific task."""
        related_blocks = []
        
        # Find blocks where the unfreeze condition matches the task
        for block_id, block in self.frozen_blocks.items():
            if task_description in block.unfreeze_condition:
                related_blocks.append(block_id)
        
        return related_blocks
    
    def attempt_unfreeze(self, block_id: str, task_description: str) -> bool:
        """Attempt to unfreeze a memory block based on success."""
        if block_id not in self.frozen_blocks:
            return False
        
        block = self.frozen_blocks[block_id]
        
        # Verify success condition
        if task_description not in block.unfreeze_condition:
            return False
        
        # Unfreeze the units
        units_unfrozen = 0
        for param_name, unit_indices in block.location_map.items():
            for unit_idx in unit_indices:
                # Unfreeze the unit
                self.memory_state[param_name]['unit_states'][unit_idx] = MemoryState.ACTIVE
                self.memory_state[param_name]['unit_history'][unit_idx] = None
                self.memory_state[param_name]['frozen_units'] -= 1
                units_unfrozen += 1
        
        # Update totals
        self.total_frozen_units -= units_unfrozen
        self.frozen_percentage = (self.total_frozen_units / self.total_memory_units) * 100
        
        # Remove from frozen blocks
        del self.frozen_blocks[block_id]
        
        print(f"[MEMORY PUNISHMENT] Unfrozen block {block_id} ({units_unfrozen} units)")
        
        return True
    
    def handle_critical_failure(self) -> bool:
        """Handle critical failure (1111 consecutive failures)."""
        print(f"[MEMORY PUNISHMENT] CRITICAL: {self.consecutive_failures} consecutive failures")
        print(f"[MEMORY PUNISHMENT] System at critical memory state - aggressive freezing required")
        
        # Freeze 1111 units as punishment
        block_id = self.freeze_memory_units(1111, "CRITICAL_FAILURE_PUNISHMENT")
        
        if self.frozen_percentage > 50.0:
            print(f"[MEMORY PUNISHMENT] CRITICAL: {self.frozen_percentage:.2f}% memory frozen")
            print(f"[MEMORY PUNISHMENT] System may become non-functional")
        
        return True  # Still alive, but severely hampered
    
    def handle_death(self) -> bool:
        """Handle death condition (100,000 consecutive failures)."""
        print(f"[MEMORY PUNISHMENT] DEATH CONDITION: {self.consecutive_failures} consecutive failures")
        print(f"[MEMORY PUNISHMENT] Freezing all remaining memory...")
        
        # Freeze all remaining memory
        remaining_units = self.total_memory_units - self.total_frozen_units
        if remaining_units > 0:
            self.freeze_memory_units(remaining_units, "DEATH_PUNISHMENT")
        
        # Mark system as dead
        self.system_alive = False
        self.death_date = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Mark all memory as DEAD
        for param_name in self.memory_state:
            for i in range(len(self.memory_state[param_name]['unit_states'])):
                self.memory_state[param_name]['unit_states'][i] = MemoryState.DEAD
        
        print(f"[MEMORY PUNISHMENT] SYSTEM DEATH: {self.death_date}")
        print(f"[MEMORY PUNISHMENT] Total frozen: {self.total_frozen_units} / {self.total_memory_units} (100%)")
        
        return False  # System is now dead
    
    def check_survival_status(self) -> Dict:
        """Check current survival status of the system."""
        if not self.system_alive:
            return {
                'alive': False,
                'death_date': self.death_date,
                'frozen_percentage': 100.0,
                'consecutive_failures': self.consecutive_failures,
                'status': 'DEAD'
            }
        
        # Check if system is functional
        functional = self.frozen_percentage < 90.0  # 90% frozen threshold
        
        return {
            'alive': self.system_alive,
            'death_date': self.death_date,
            'frozen_percentage': self.frozen_percentage,
            'consecutive_failures': self.consecutive_failures,
            'functional': functional,
            'status': 'CRITICAL' if self.frozen_percentage > 50.0 else 'NORMAL'
        }
    
    def get_memory_punishment_stats(self) -> Dict:
        """Get statistics about memory punishment."""
        if not self.failure_history:
            return {}
        
        recent_failures = list(self.failure_history)[-1000:]  # Last 1000 failures
        
        return {
            'total_failures': len(self.failure_history),
            'consecutive_failures': self.consecutive_failures,
            'total_frozen_units': self.total_frozen_units,
            'frozen_percentage': self.frozen_percentage,
            'frozen_blocks': len(self.frozen_blocks),
            'recent_failure_rate': len(recent_failures) / 1000 if recent_failures else 0,
            'survival_status': self.check_survival_status(),
            'memory_unit': self.memory_unit.value,
            'total_memory_units': self.total_memory_units
        }
    
    def emergency_thaw(self, override_code: str) -> bool:
        """
        Emergency thaw of frozen memory using override code.
        This is a last-resort mechanism.
        """
        if not self.system_alive:
            print("[MEMORY PUNISHMENT] Cannot thaw dead system")
            return False
        
        print(f"[MEMORY PUNISHMENT] EMERGENCY THAW: {override_code}")
        
        # Thaw all frozen memory
        for block_id in list(self.frozen_blocks.keys()):
            block = self.frozen_blocks[block_id]
            
            for param_name, unit_indices in block.location_map.items():
                for unit_idx in unit_indices:
                    self.memory_state[param_name]['unit_states'][unit_idx] = MemoryState.ACTIVE
                    self.memory_state[param_name]['unit_history'][unit_idx] = None
                    self.memory_state[param_name]['frozen_units'] -= 1
        
        # Reset all counters
        self.total_frozen_units = 0
        self.frozen_percentage = 0.0
        self.consecutive_failures = 0
        self.frozen_blocks.clear()
        
        print("[MEMORY PUNISHMENT] Emergency thaw complete")
        
        return True
    
    def get_survival_score(self) -> float:
        """Calculate overall survival score (0.0 = dead, 1.0 = perfect)."""
        if not self.system_alive:
            return 0.0
        
        # Score based on frozen percentage and consecutive failures
        frozen_penalty = self.frozen_percentage / 100.0
        failure_penalty = min(1.0, self.consecutive_failures / self.critical_threshold)
        
        survival_score = 1.0 - (frozen_penalty * 0.7 + failure_penalty * 0.3)
        
        return max(0.0, survival_score)
    
    def predict_survival_probability(self, task_difficulty: float) -> float:
        """Predict probability of survival given task difficulty."""
        current_score = self.get_survival_score()
        
        # Adjust based on task difficulty
        difficulty_penalty = task_difficulty * 0.1
        
        predicted_score = current_score - difficulty_penalty
        
        return max(0.0, min(1.0, predicted_score))