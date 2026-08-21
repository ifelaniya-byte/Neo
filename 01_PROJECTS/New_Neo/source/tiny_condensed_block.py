"""
PROJECT APEX: TINY CONDENSED DATA BLOCK SYSTEM
Hyper-condensed model storage that can expand to full LLM with weights.
Supports multiple external model blocks and dynamic loading.
"""

import torch
import torch.nn as nn
import numpy as np
import hashlib
import zlib
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pickle
import base64

class BlockType(Enum):
    """Types of condensed model blocks."""
    BASE_MICRO_LLM = "BASE_MICRO_LLM"
    DEEPSEEK_V1 = "DEEPSEEK_V1"
    GLM_LATEST = "GLM_LATEST"
    KIMI = "KIMI"
    HYPERMUTATED = "HYPERMUTATED"
    CUSTOM = "CUSTOM"

class CompressionMethod(Enum):
    """Compression methods for model blocks."""
    ZLIB = "ZLIB"
    GZIP = "GZIP"
    LZMA = "LZMA"
    QUANTIZATION = "QUANTIZATION"
    SPARSIFICATION = "SPARSIFICATION"
    TENSOR_DECOMPOSITION = "TENSOR_DECOMPOSITION"
    HYBRID = "HYBRID"

@dataclass
class ModelBlockHeader:
    """Header information for condensed model block."""
    block_id: str
    block_type: BlockType
    original_params: int
    compressed_size: int
    compression_ratio: float
    compression_method: CompressionMethod
    model_architecture: str
    performance_metrics: Dict
    creation_date: str
    version: str
    checksum: str
    
    def to_dict(self):
        return self.__dict__

@dataclass
class ModelBlock:
    """Hyper-condensed model block."""
    header: ModelBlockHeader
    compressed_data: bytes
    metadata: Dict
    access_count: int
    last_accessed: str
    
    def to_dict(self):
        return {
            'header': self.header.to_dict(),
            'compressed_size': len(self.compressed_data),
            'metadata': self.metadata,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed
        }

class TinyCondensedBlockSystem:
    """
    System for managing hyper-condensed model blocks.
    Can expand blocks to full models and merge multiple blocks.
    """
    
    def __init__(self, storage_path="condensed_blocks"):
        self.storage_path = storage_path
        self.loaded_blocks = {}  # coat rack - currently loaded blocks
        self.block_registry = {}  # all available blocks
        self.merged_models = {}  # merged model combinations
        self.active_block = None  # currently active block
        
        # Initialize storage
        import os
        os.makedirs(storage_path, exist_ok=True)
        
        # Load registry
        self.load_registry()
    
    def create_condensed_block(self, model: nn.Module, block_type: BlockType,
                              compression_method: CompressionMethod = CompressionMethod.HYBRID,
                              metadata: Dict = None) -> str:
        """
        Create a hyper-condensed block from a model.
        Returns block ID.
        """
        if metadata is None:
            metadata = {}
        
        # Get model state dict
        state_dict = model.state_dict()
        
        # Calculate original parameters
        original_params = sum(p.numel() for p in model.parameters())
        
        # Compress the state dict
        compressed_data, compression_ratio = self.compress_state_dict(
            state_dict, compression_method
        )
        
        # Create header
        block_id = self.generate_block_id(block_type, state_dict)
        header = ModelBlockHeader(
            block_id=block_id,
            block_type=block_type,
            original_params=original_params,
            compressed_size=len(compressed_data),
            compression_ratio=compression_ratio,
            compression_method=compression_method,
            model_architecture=str(type(model)),
            performance_metrics=metadata.get('performance_metrics', {}),
            creation_date=self.get_timestamp(),
            version="1.0",
            checksum=self.calculate_checksum(compressed_data)
        )
        
        # Create block
        block = ModelBlock(
            header=header,
            compressed_data=compressed_data,
            metadata=metadata,
            access_count=0,
            last_accessed=""
        )
        
        # Save block
        self.save_block(block)
        
        # Register block
        self.block_registry[block_id] = {
            'header': header.to_dict(),
            'metadata': metadata,
            'file_path': f"{self.storage_path}/{block_id}.block"
        }
        
        self.save_registry()
        
        return block_id
    
    def compress_state_dict(self, state_dict: Dict, 
                          method: CompressionMethod) -> Tuple[bytes, float]:
        """Compress state dict using specified method."""
        # Serialize state dict
        serialized = pickle.dumps(state_dict)
        original_size = len(serialized)
        
        compressed_data = serialized
        
        if method == CompressionMethod.ZLIB:
            compressed_data = zlib.compress(serialized, level=9)
        elif method == CompressionMethod.GZIP:
            import gzip
            compressed_data = gzip.compress(serialized, compresslevel=9)
        elif method == CompressionMethod.LZMA:
            import lzma
            compressed_data = lzma.compress(serialized, preset=9)
        elif method == CompressionMethod.QUANTIZATION:
            compressed_data = self.quantize_and_compress(state_dict)
        elif method == CompressionMethod.SPARSIFICATION:
            compressed_data = self.sparsify_and_compress(state_dict)
        elif method == CompressionMethod.TENSOR_DECOMPOSITION:
            compressed_data = self.decompose_and_compress(state_dict)
        elif method == CompressionMethod.HYBRID:
            # Combine multiple methods for maximum compression
            compressed_data = self.hybrid_compress(state_dict)
        
        compression_ratio = original_size / len(compressed_data)
        return compressed_data, compression_ratio
    
    def quantize_and_compress(self, state_dict: Dict) -> bytes:
        """Quantize weights and compress."""
        quantized_dict = {}
        
        for key, tensor in state_dict.items():
            # Quantize to INT8
            quantized = torch.quantize_per_tensor(
                tensor, scale=0.1, zero_point=0, dtype=torch.qint8
            )
            quantized_dict[key] = quantized
        
        serialized = pickle.dumps(quantized_dict)
        return zlib.compress(serialized, level=9)
    
    def sparsify_and_compress(self, state_dict: Dict) -> bytes:
        """Sparsify weights and compress."""
        sparse_dict = {}
        
        for key, tensor in state_dict.items():
            # Keep only top 20% of weights by magnitude
            threshold = torch.quantile(torch.abs(tensor), 0.8)
            mask = torch.abs(tensor) > threshold
            sparse_dict[key] = tensor * mask.float()
        
        serialized = pickle.dumps(sparse_dict)
        return zlib.compress(serialized, level=9)
    
    def decompose_and_compress(self, state_dict: Dict) -> bytes:
        """Decompose tensors using SVD and compress."""
        decomposed_dict = {}
        
        for key, tensor in state_dict.items():
            if tensor.dim() == 2:  # Only decompose 2D tensors
                # SVD decomposition
                U, S, V = torch.svd(tensor)
                # Keep top 50% singular values
                k = len(S) // 2
                decomposed_dict[key] = {
                    'U': U[:, :k],
                    'S': S[:k],
                    'V': V[:, :k]
                }
            else:
                decomposed_dict[key] = tensor
        
        serialized = pickle.dumps(decomposed_dict)
        return zlib.compress(serialized, level=9)
    
    def hybrid_compress(self, state_dict: Dict) -> bytes:
        """Apply hybrid compression for maximum efficiency."""
        # Apply quantization first
        quantized_dict = {}
        for key, tensor in state_dict.items():
            quantized = torch.quantize_per_tensor(
                tensor, scale=0.1, zero_point=0, dtype=torch.qint8
            )
            quantized_dict[key] = quantized
        
        # Then sparsify
        sparse_dict = {}
        for key, tensor in quantized_dict.items():
            if hasattr(tensor, 'dequantize'):
                dequantized = tensor.dequantize()
                threshold = torch.quantile(torch.abs(dequantized), 0.7)
                mask = torch.abs(dequantized) > threshold
                sparse_dict[key] = tensor * mask.float()
            else:
                sparse_dict[key] = tensor
        
        # Finally compress with LZMA
        serialized = pickle.dumps(sparse_dict)
        import lzma
        return lzma.compress(serialized, preset=9)
    
    def expand_block(self, block_id: str, target_architecture: nn.Module) -> nn.Module:
        """
        Expand a condensed block back to a full model.
        Returns the loaded model.
        """
        # Load block
        block = self.load_block(block_id)
        if not block:
            raise ValueError(f"Block {block_id} not found")
        
        # Decompress data
        state_dict = self.decompress_state_dict(
            block.compressed_data, 
            block.header.compression_method
        )
        
        # Load into target architecture
        target_architecture.load_state_dict(state_dict)
        
        # Update access tracking
        block.access_count += 1
        block.last_accessed = self.get_timestamp()
        self.save_block(block)
        
        return target_architecture
    
    def decompress_state_dict(self, compressed_data: bytes, 
                            method: CompressionMethod) -> Dict:
        """Decompress state dict using specified method."""
        if method == CompressionMethod.ZLIB:
            serialized = zlib.decompress(compressed_data)
        elif method == CompressionMethod.GZIP:
            import gzip
            serialized = gzip.decompress(compressed_data)
        elif method == CompressionMethod.LZMA:
            import lzma
            serialized = lzma.decompress(compressed_data)
        elif method in [CompressionMethod.QUANTIZATION, CompressionMethod.SPARSIFICATION,
                        CompressionMethod.TENSOR_DECOMPOSITION, CompressionMethod.HYBRID]:
            # These methods need custom decompression
            serialized = self.custom_decompress(compressed_data, method)
        else:
            serialized = compressed_data
        
        return pickle.loads(serialized)
    
    def custom_decompress(self, compressed_data: bytes, 
                         method: CompressionMethod) -> bytes:
        """Custom decompression for advanced methods."""
        # For now, just decompress with zlib
        # In production, would handle each method specifically
        return zlib.decompress(compressed_data)
    
    def load_to_coat_rack(self, block_id: str) -> bool:
        """
        Load a block to the coat rack (active memory).
        Makes it immediately accessible for the micro-LLM.
        """
        block = self.load_block(block_id)
        if not block:
            return False
        
        # Load to active memory
        self.loaded_blocks[block_id] = block
        
        # Update access tracking
        block.access_count += 1
        block.last_accessed = self.get_timestamp()
        
        return True
    
    def unload_from_coat_rack(self, block_id: str) -> bool:
        """Unload a block from the coat rack."""
        if block_id in self.loaded_blocks:
            del self.loaded_blocks[block_id]
            return True
        return False
    
    def set_active_block(self, block_id: str) -> bool:
        """Set the currently active block for the micro-LLM."""
        if block_id in self.loaded_blocks:
            self.active_block = block_id
            return True
        return False
    
    def merge_blocks(self, block_ids: List[str], merge_strategy: str = "average") -> str:
        """
        Merge multiple blocks into a single enhanced block.
        Returns the new merged block ID.
        """
        if not block_ids:
            raise ValueError("No blocks to merge")
        
        # Load all blocks
        blocks = [self.load_block(bid) for bid in block_ids]
        if not all(blocks):
            raise ValueError("Some blocks could not be loaded")
        
        # Decompress all state dicts
        state_dicts = []
        for block in blocks:
            state_dict = self.decompress_state_dict(
                block.compressed_data,
                block.header.compression_method
            )
            state_dicts.append(state_dict)
        
        # Merge state dicts
        merged_state_dict = self.merge_state_dicts(state_dicts, merge_strategy)
        
        # Create new block from merged state dict
        # This requires a model architecture to load into
        # For now, return a placeholder
        merged_block_id = f"merged_{self.generate_block_id(BlockType.CUSTOM, merged_state_dict)}"
        
        return merged_block_id
    
    def merge_state_dicts(self, state_dicts: List[Dict], 
                         strategy: str) -> Dict:
        """Merge multiple state dicts using specified strategy."""
        if strategy == "average":
            return self.average_merge(state_dicts)
        elif strategy == "weighted":
            return self.weighted_merge(state_dicts)
        elif strategy == "voting":
            return self.voting_merge(state_dicts)
        else:
            return state_dicts[0]  # Default to first
    
    def average_merge(self, state_dicts: List[Dict]) -> Dict:
        """Average state dicts."""
        merged = {}
        
        for key in state_dicts[0].keys():
            tensors = [sd[key] for sd in state_dicts if key in sd]
            if tensors:
                merged[key] = torch.stack(tensors).mean(dim=0)
        
        return merged
    
    def weighted_merge(self, state_dicts: List[Dict]) -> Dict:
        """Weighted average merge based on performance."""
        # In production, would use performance metrics for weighting
        return self.average_merge(state_dicts)
    
    def voting_merge(self, state_dicts: List[Dict]) -> Dict:
        """Voting-based merge for discrete choices."""
        # For continuous parameters, fall back to average
        return self.average_merge(state_dicts)
    
    def generate_block_id(self, block_type: BlockType, state_dict: Dict) -> str:
        """Generate unique block ID."""
        # Create signature from state dict keys and shapes
        signature = f"{block_type.value}"
        for key in sorted(state_dict.keys()):
            if hasattr(state_dict[key], 'shape'):
                signature += f"_{key}_{state_dict[key].shape}"
        
        return hashlib.md5(signature.encode()).hexdigest()[:16]
    
    def calculate_checksum(self, data: bytes) -> str:
        """Calculate checksum for data integrity."""
        return hashlib.sha256(data).hexdigest()
    
    def get_timestamp(self) -> str:
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def save_block(self, block: ModelBlock):
        """Save block to disk."""
        file_path = f"{self.storage_path}/{block.header.block_id}.block"
        
        with open(file_path, 'wb') as f:
            # Write header
            header_json = json.dumps(block.header.to_dict()).encode()
            f.write(len(header_json).to_bytes(4, 'big'))
            f.write(header_json)
            
            # Write compressed data
            f.write(block.compressed_data)
            
            # Write metadata
            metadata_json = json.dumps(block.metadata).encode()
            f.write(len(metadata_json).to_bytes(4, 'big'))
            f.write(metadata_json)
    
    def load_block(self, block_id: str) -> Optional[ModelBlock]:
        """Load block from disk."""
        file_path = f"{self.storage_path}/{block_id}.block"
        
        try:
            with open(file_path, 'rb') as f:
                # Read header
                header_size = int.from_bytes(f.read(4), 'big')
                header_json = f.read(header_size).decode()
                header = ModelBlockHeader(**json.loads(header_json))
                
                # Read compressed data
                # Need to know data size - would be stored in real implementation
                # For now, read rest of file except metadata
                import os
                file_size = os.path.getsize(file_path)
                remaining = file_size - f.tell() - 4  # -4 for metadata size
                compressed_data = f.read(remaining)
                
                # Read metadata
                metadata_size = int.from_bytes(f.read(4), 'big')
                metadata_json = f.read(metadata_size).decode()
                metadata = json.loads(metadata_json)
                
                return ModelBlock(
                    header=header,
                    compressed_data=compressed_data,
                    metadata=metadata,
                    access_count=0,
                    last_accessed=""
                )
        except Exception as e:
            print(f"[BLOCK SYSTEM] Error loading block {block_id}: {e}")
            return None
    
    def save_registry(self):
        """Save block registry to disk."""
        with open(f"{self.storage_path}/registry.json", 'w') as f:
            json.dump(self.block_registry, f, indent=2)
    
    def load_registry(self):
        """Load block registry from disk."""
        try:
            with open(f"{self.storage_path}/registry.json", 'r') as f:
                self.block_registry = json.load(f)
        except FileNotFoundError:
            self.block_registry = {}
    
    def get_block_info(self, block_id: str) -> Optional[Dict]:
        """Get information about a block."""
        if block_id in self.block_registry:
            return self.block_registry[block_id]
        return None
    
    def list_available_blocks(self) -> List[Dict]:
        """List all available blocks."""
        return [
            {
                'block_id': bid,
                'block_type': info['header']['block_type'],
                'original_params': info['header']['original_params'],
                'compression_ratio': info['header']['compression_ratio'],
                'creation_date': info['header']['creation_date']
            }
            for bid, info in self.block_registry.items()
        ]
    
    def get_coat_rack_status(self) -> Dict:
        """Get status of currently loaded blocks (coat rack)."""
        return {
            'loaded_blocks': list(self.loaded_blocks.keys()),
            'active_block': self.active_block,
            'total_loaded': len(self.loaded_blocks)
        }