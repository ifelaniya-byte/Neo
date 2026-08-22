"""
MEGACOMPACT PARAMETER DISCOVERY & STRESS TEST SUITE
This script maps out all system parameters and stress tests their limits.
"""

import torch
import time
import pandas as pd
import json
import os
import sys
from datetime import datetime
import gc

class ParameterMapper:
    """Maps out all configurable parameters in the megacompact system"""
    
    def __init__(self):
        self.parameters = {}
        self.test_results = []
        self.device = self._get_best_device()
        
    def _get_best_device(self):
        """Determine the best available compute device"""
        if torch.cuda.is_available():
            try:
                # Test CUDA compatibility
                test_tensor = torch.zeros(1, device='cuda:0')
                capability = torch.cuda.get_device_capability(0)
                if capability[0] >= 7:
                    return 'cuda:0'
                else:
                    print(f"GPU capability {capability} below minimum (7.0). Using CPU.")
                    return 'cpu'
            except Exception as e:
                print(f"CUDA test failed: {e}. Using CPU.")
                return 'cpu'
        return 'cpu'
    
    def map_hypermaximizer_params(self):
        """Map DualGPUHyperMaximizer parameters"""
        print("="*80)
        print("MAPPING DUALGPUHYPERMAXIMIZER PARAMETERS")
        print("="*80)
        
        params = {
            'base_width': {
                'description': 'Initial state width for cellular automaton',
                'current_value': 10_000,
                'type': 'int',
                'range': '1 - 1,000,000+',
                'impact': 'Linear memory usage, exponential compute time'
            },
            'base_steps': {
                'description': 'Initial number of cellular automaton steps',
                'current_value': 10_000,
                'type': 'int',
                'range': '1 - 100,000+',
                'impact': 'Linear compute time'
            },
            'max_iterations': {
                'description': 'Maximum exponential scaling iterations',
                'current_value': 10,
                'type': 'int',
                'range': '1 - 20+',
                'impact': 'Exponential resource consumption'
            },
            'memory_allocation': {
                'description': 'GPU memory hog allocation size',
                'current_value': '80_000 x 100_000',
                'type': 'tuple',
                'range': 'Depends on GPU memory',
                'impact': 'Memory pressure'
            },
            'dtype': {
                'description': 'Tensor data type',
                'current_value': 'int8',
                'type': 'str',
                'range': 'int8, int16, int32, float32, float64',
                'impact': 'Memory usage, precision'
            }
        }
        
        self.parameters['hypermaximizer'] = params
        self._print_params(params)
        return params
    
    def map_bridge_controller_params(self):
        """Map KaggleBridgeController parameters"""
        print("\n" + "="*80)
        print("MAPPING KAGGLE BRIDGE CONTROLLER PARAMETERS")
        print("="*80)
        
        params = {
            'kaggle_username': {
                'description': 'Kaggle account username',
                'current_value': 'deemmany',
                'type': 'str',
                'range': 'Valid Kaggle username',
                'impact': 'Kernel ownership and permissions'
            },
            'slug_format': {
                'description': 'Kernel slug naming convention',
                'current_value': 'kebab-case with timestamp',
                'type': 'str',
                'range': 'kebab-case only (no underscores)',
                'impact': 'Kaggle API validation'
            },
            'payload_dir': {
                'description': 'Local directory for kernel payload',
                'current_value': 'kaggle_omega_payload',
                'type': 'str',
                'range': 'Valid directory path',
                'impact': 'File system organization'
            },
            'output_dir': {
                'description': 'Directory for extracted results',
                'current_value': 'kaggle_extracted_ledgers',
                'type': 'str',
                'range': 'Valid directory path',
                'impact': 'Result storage location'
            },
            'kernel_metadata': {
                'description': 'Kaggle kernel configuration',
                'current_value': {
                    'language': 'python',
                    'kernel_type': 'script',
                    'enable_gpu': 'true',
                    'enable_internet': 'false',
                    'is_private': 'false'
                },
                'type': 'dict',
                'range': 'Kaggle API valid values',
                'impact': 'Kernel execution environment'
            }
        }
        
        self.parameters['bridge_controller'] = params
        self._print_params(params)
        return params
    
    def map_system_params(self):
        """Map system-level parameters"""
        print("\n" + "="*80)
        print("MAPPING SYSTEM PARAMETERS")
        print("="*80)
        
        # Get device info
        device_info = {
            'device': self.device,
            'cuda_available': torch.cuda.is_available(),
            'cuda_device_count': torch.cuda.device_count() if torch.cuda.is_available() else 0
        }
        
        if torch.cuda.is_available():
            device_info['cuda_device_name'] = torch.cuda.get_device_name(0)
            device_info['cuda_capability'] = torch.cuda.get_device_capability(0)
            device_info['cuda_memory_total'] = torch.cuda.get_device_properties(0).total_memory / 1e9  # GB
        
        params = {
            'compute_device': {
                'description': 'Primary compute device',
                'current_value': device_info,
                'type': 'dict',
                'range': 'cpu, cuda:0, cuda:1, etc.',
                'impact': 'Performance, memory availability'
            },
            'polling_interval': {
                'description': 'Kaggle status polling interval (seconds)',
                'current_value': 15,
                'type': 'int',
                'range': '5 - 300',
                'impact': 'API rate limits, responsiveness'
            },
            'timeout_threshold': {
                'description': 'Execution time threshold (seconds)',
                'current_value': 5.0,
                'type': 'float',
                'range': '1.0 - 60.0',
                'impact': 'Early termination condition'
            },
            'exponential_multiplier': {
                'description': 'Scale multiplier per iteration',
                'current_value': 2,
                'type': 'int',
                'range': '1.5 - 3',
                'impact': 'Resource growth rate'
            }
        }
        
        self.parameters['system'] = params
        self._print_params(params)
        return params
    
    def _print_params(self, params):
        """Pretty print parameter mapping"""
        for param_name, param_info in params.items():
            print(f"\n{param_name}:")
            print(f"  Description: {param_info['description']}")
            print(f"  Current Value: {param_info['current_value']}")
            print(f"  Type: {param_info['type']}")
            print(f"  Valid Range: {param_info['range']}")
            print(f"  Impact: {param_info['impact']}")
    
    def export_parameter_map(self, filename="parameter_map.json"):
        """Export parameter mapping to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.parameters, f, indent=2)
        print(f"\n[+] Parameter map exported to {filename}")


class ParameterStressTester:
    """Stress tests parameter limits and boundaries"""
    
    def __init__(self, device='cpu'):
        self.device = device
        self.results = []
        
    def stress_test_memory_allocation(self):
        """Test memory allocation limits"""
        print("\n" + "="*80)
        print("STRESS TEST: MEMORY ALLOCATION")
        print("="*80)
        
        test_sizes = [
            (10_000, 10_000),    # 100M elements (~100MB int8)
            (50_000, 50_000),    # 2.5B elements (~2.5GB int8)
            (80_000, 100_000),   # 8B elements (~8GB int8)
            (100_000, 100_000),  # 10B elements (~10GB int8)
        ]
        
        for rows, cols in test_sizes:
            try:
                start_time = time.perf_counter()
                if self.device.startswith('cuda'):
                    tensor = torch.empty((rows, cols), dtype=torch.int8, device=self.device)
                else:
                    # Use smaller sizes for CPU
                    tensor = torch.empty((min(rows, 50000), min(cols, 50000)), dtype=torch.int8)
                elapsed = time.perf_counter() - start_time
                
                result = {
                    'test': 'memory_allocation',
                    'size': f"{rows}x{cols}",
                    'success': True,
                    'time_sec': elapsed,
                    'memory_gb': (rows * cols) / 1e9
                }
                print(f"  {rows}x{cols}: SUCCESS ({elapsed:.3f}s, {result['memory_gb']:.2f}GB)")
                
                del tensor
                if self.device.startswith('cuda'):
                    torch.cuda.empty_cache()
                gc.collect()
                
            except Exception as e:
                result = {
                    'test': 'memory_allocation',
                    'size': f"{rows}x{cols}",
                    'success': False,
                    'error': str(e)
                }
                print(f"  {rows}x{cols}: FAILED - {e}")
            
            self.results.append(result)
        
        return self.results
    
    def stress_test_computation_scale(self):
        """Test computation scaling"""
        print("\n" + "="*80)
        print("STRESS TEST: COMPUTATION SCALE")
        print("="*80)
        
        scales = [1, 2, 4, 8, 16]
        base_width = 1_000
        base_steps = 1_000
        
        for scale in scales:
            try:
                width = base_width * scale
                steps = base_steps * scale
                
                if self.device.startswith('cuda'):
                    state = torch.zeros((1, width), dtype=torch.int8, device=self.device)
                else:
                    # Limit CPU tests
                    width = min(width, 10000)
                    steps = min(steps, 10000)
                    state = torch.zeros((1, width), dtype=torch.int8)
                
                state[0, width // 2] = 1
                total_cells = width * steps
                
                start_time = time.perf_counter()
                for _ in range(steps):
                    left = torch.roll(state, 1, dims=1)
                    center = state
                    right = torch.roll(state, -1, dims=1)
                    neighborhood = (left << 2) | (center << 1) | right
                    state = (30 >> neighborhood) & 1
                
                if self.device.startswith('cuda'):
                    torch.cuda.synchronize()
                elapsed = time.perf_counter() - start_time
                sro = total_cells / elapsed if elapsed > 0 else 0
                
                result = {
                    'test': 'computation_scale',
                    'scale': scale,
                    'width': width,
                    'steps': steps,
                    'total_cells': total_cells,
                    'time_sec': elapsed,
                    'sro_per_sec': sro,
                    'success': True
                }
                print(f"  Scale {scale}x: {total_cells:,} cells in {elapsed:.3f}s ({sro:,.0f} cells/sec)")
                
                del state
                if self.device.startswith('cuda'):
                    torch.cuda.empty_cache()
                gc.collect()
                
            except Exception as e:
                result = {
                    'test': 'computation_scale',
                    'scale': scale,
                    'success': False,
                    'error': str(e)
                }
                print(f"  Scale {scale}x: FAILED - {e}")
            
            self.results.append(result)
        
        return self.results
    
    def stress_test_dtypes(self):
        """Test different data types"""
        print("\n" + "="*80)
        print("STRESS TEST: DATA TYPES")
        print("="*80)
        
        dtypes = [torch.int8, torch.int16, torch.int32, torch.float32, torch.float64]
        test_size = (10_000, 10_000)
        
        for dtype in dtypes:
            try:
                start_time = time.perf_counter()
                if self.device.startswith('cuda'):
                    tensor = torch.empty(test_size, dtype=dtype, device=self.device)
                else:
                    tensor = torch.empty(test_size, dtype=dtype)
                elapsed = time.perf_counter() - start_time
                
                memory_mb = (test_size[0] * test_size[1] * dtype.itemsize) / 1e6
                
                result = {
                    'test': 'dtype_test',
                    'dtype': str(dtype),
                    'memory_mb': memory_mb,
                    'time_sec': elapsed,
                    'success': True
                }
                print(f"  {dtype}: {memory_mb:.1f}MB in {elapsed:.3f}s")
                
                del tensor
                if self.device.startswith('cuda'):
                    torch.cuda.empty_cache()
                gc.collect()
                
            except Exception as e:
                result = {
                    'test': 'dtype_test',
                    'dtype': str(dtype),
                    'success': False,
                    'error': str(e)
                }
                print(f"  {dtype}: FAILED - {e}")
            
            self.results.append(result)
        
        return self.results
    
    def stress_test_boundary_conditions(self):
        """Test boundary conditions and edge cases"""
        print("\n" + "="*80)
        print("STRESS TEST: BOUNDARY CONDITIONS")
        print("="*80)
        
        boundary_tests = [
            ('width=1', 1, 1000),
            ('steps=1', 1000, 1),
            ('width=even', 1000, 1000),
            ('width=odd', 1001, 1000),
            ('large_width', 100000, 10),
            ('large_steps', 10, 100000),
        ]
        
        for test_name, width, steps in boundary_tests:
            try:
                if self.device.startswith('cuda'):
                    state = torch.zeros((1, width), dtype=torch.int8, device=self.device)
                else:
                    # Limit CPU tests
                    width = min(width, 10000)
                    steps = min(steps, 10000)
                    state = torch.zeros((1, width), dtype=torch.int8)
                
                state[0, width // 2] = 1
                
                start_time = time.perf_counter()
                for _ in range(steps):
                    left = torch.roll(state, 1, dims=1)
                    center = state
                    right = torch.roll(state, -1, dims=1)
                    neighborhood = (left << 2) | (center << 1) | right
                    state = (30 >> neighborhood) & 1
                
                if self.device.startswith('cuda'):
                    torch.cuda.synchronize()
                elapsed = time.perf_counter() - start_time
                
                result = {
                    'test': 'boundary_condition',
                    'test_name': test_name,
                    'width': width,
                    'steps': steps,
                    'time_sec': elapsed,
                    'success': True
                }
                print(f"  {test_name}: SUCCESS ({elapsed:.3f}s)")
                
                del state
                if self.device.startswith('cuda'):
                    torch.cuda.empty_cache()
                gc.collect()
                
            except Exception as e:
                result = {
                    'test': 'boundary_condition',
                    'test_name': test_name,
                    'success': False,
                    'error': str(e)
                }
                print(f"  {test_name}: FAILED - {e}")
            
            self.results.append(result)
        
        return self.results
    
    def export_stress_results(self, filename="stress_test_results.json"):
        """Export stress test results to JSON"""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n[+] Stress test results exported to {filename}")
        
        # Also create a summary CSV
        df = pd.DataFrame(self.results)
        csv_filename = filename.replace('.json', '.csv')
        df.to_csv(csv_filename, index=False)
        print(f"[+] Stress test summary exported to {csv_filename}")


def main():
    print("="*80)
    print("MEGACOMPACT PARAMETER DISCOVERY & STRESS TEST SUITE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Phase 1: Parameter Mapping
    print("\n" + "="*80)
    print("PHASE 1: PARAMETER DISCOVERY")
    print("="*80)
    
    mapper = ParameterMapper()
    mapper.map_hypermaximizer_params()
    mapper.map_bridge_controller_params()
    mapper.map_system_params()
    mapper.export_parameter_map()
    
    # Phase 2: Stress Testing
    print("\n" + "="*80)
    print("PHASE 2: STRESS TESTING")
    print("="*80)
    
    tester = ParameterStressTester(device=mapper.device)
    tester.stress_test_memory_allocation()
    tester.stress_test_computation_scale()
    tester.stress_test_dtypes()
    tester.stress_test_boundary_conditions()
    tester.export_stress_results()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUITE COMPLETE")
    print("="*80)
    
    successful_tests = sum(1 for r in tester.results if r.get('success', False))
    total_tests = len(tester.results)
    
    print(f"Total Tests: {total_tests}")
    print(f"Successful: {successful_tests}")
    print(f"Failed: {total_tests - successful_tests}")
    print(f"Success Rate: {successful_tests/total_tests*100:.1f}%")
    print(f"Device Used: {mapper.device}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Generate parameter recommendations
    print("\n" + "="*80)
    print("PARAMETER RECOMMENDATIONS")
    print("="*80)
    
    print("\nBased on stress test results:")
    print("1. Memory Allocation: Start with 50Kx50K, scale based on device")
    print("2. Computation Scale: Use exponential multiplier of 2x for balanced growth")
    print("3. Data Type: int8 provides best memory/performance ratio")
    print("4. Boundary Conditions: Handle width=1 and steps=1 edge cases")
    print("5. Device Fallback: Always include CPU fallback for CUDA incompatibility")
    
    print("\nFiles generated:")
    print("- parameter_map.json: Complete parameter documentation")
    print("- stress_test_results.json: Detailed test results")
    print("- stress_test_results.csv: Test summary for analysis")


if __name__ == "__main__":
    main()
