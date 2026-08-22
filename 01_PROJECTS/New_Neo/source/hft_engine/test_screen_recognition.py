"""
Simple test of advanced screen recognition system
"""
import numpy as np
import cv2
from advanced_screen_recognition import AdvancedScreenRecognition

def test_components():
    """Test individual components"""
    print("Testing Advanced Screen Recognition Components")
    print("=" * 60)
    
    # Create test screen data
    test_screen = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    print(f"Created test screen: {test_screen.shape}")
    
    # Test visual compressor
    print("\n1. Testing Visual Context Compressor...")
    from advanced_screen_recognition import VisualContextCompressor
    compressor = VisualContextCompressor()
    compressed = compressor.compress(test_screen)
    print(f"   Original: {test_screen.shape}")
    print(f"   Compressed: {compressed.shape}")
    print(f"   Compression ratio: {1 - compressed.size/test_screen.size:.2f}")
    
    # Test token selector
    print("\n2. Testing FocusUI Token Selector...")
    from advanced_screen_recognition import FocusUITokenSelector
    selector = FocusUITokenSelector()
    selected = selector.select(compressed, "describe the screen")
    print(f"   Selected shape: {selected.shape}")
    print(f"   Selection ratio: {selected.size/compressed.size:.2f}")
    
    # Test Re-Prefill optimizer
    print("\n3. Testing Re-Prefill Optimizer...")
    from advanced_screen_recognition import RePrefillOptimizer
    optimizer = RePrefillOptimizer()
    optimized = optimizer.optimize(selected, "describe the screen")
    print(f"   Optimized shape: {optimized.shape}")
    
    # Test OmniParser integration
    print("\n4. Testing OmniParser Integration...")
    from advanced_screen_recognition import OmniParserIntegration
    parser = OmniParserIntegration()
    parsed = parser.parse(test_screen)
    print(f"   Interactable regions: {len(parsed['interactable_regions'])}")
    print(f"   Icon descriptions: {len(parsed['icon_descriptions'])}")
    print(f"   Text elements: {len(parsed['text_elements'])}")
    print(f"   UI elements: {len(parsed['ui_elements'])}")
    
    print("\n" + "=" * 60)
    print("Component tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_components()