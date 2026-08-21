"""
Test script to verify HFT engine components
"""
import sys
import asyncio
from order_book import OrderBook
from microstructure_features import MicrostructureFeatures
from ml_pipeline import MLPipeline
from stochastic_bridge import StochasticBridge
from error_handler import ErrorHandler, HealthChecker


def test_order_book():
    """Test order book functionality"""
    print("Testing Order Book...")
    book = OrderBook("BTC-USD")
    
    # Add some orders
    book.process_received("order1", 50000.0, 1.5, 'buy')
    book.process_received("order2", 50001.0, 2.0, 'buy')
    book.process_received("order3", 50002.0, 1.0, 'sell')
    book.process_received("order4", 50003.0, 3.0, 'sell')
    
    # Test basic functionality
    bid_price, bid_size = book.get_best_bid()
    ask_price, ask_size = book.get_best_ask()
    mid_price = book.get_mid_price()
    spread = book.get_spread()
    
    print(f"  Best Bid: ${bid_price} (size: {bid_size})")
    print(f"  Best Ask: ${ask_price} (size: {ask_size})")
    print(f"  Mid Price: ${mid_price}")
    print(f"  Spread: ${spread}")
    
    # Test order removal
    book.process_done("order1")
    bid_price, bid_size = book.get_best_bid()
    print(f"  After removal - Best Bid: ${bid_price} (size: {bid_size})")
    
    assert bid_price == 50001.0, "Order book test failed"
    print("  [PASS] Order book test passed")
    return True


def test_microstructure_features():
    """Test microstructure feature calculation"""
    print("\nTesting Microstructure Features...")
    features = MicrostructureFeatures()
    
    # Create a mock order book
    from order_book import OrderBook
    book = OrderBook("BTC-USD")
    
    # Add some orders
    book.process_received("order1", 50000.0, 1.5, 'buy')
    book.process_received("order2", 50001.0, 2.0, 'buy')
    book.process_received("order3", 50002.0, 1.0, 'sell')
    book.process_received("order4", 50003.0, 3.0, 'sell')
    
    # Update features
    feature_dict = features.update_features(book, 'received', {'type': 'received'})
    
    print(f"  Features calculated: {len(feature_dict)} features")
    print(f"  Sample features: {list(feature_dict.keys())[:5]}")
    
    # Test signal interpretation
    signals = features.get_signal_interpretation(feature_dict)
    print(f"  OFI Signal: {signals['ofi_signal']}")
    print(f"  Momentum: {signals['momentum']}")
    
    assert len(feature_dict) > 0, "Feature calculation failed"
    print("  [PASS] Microstructure features test passed")
    return True


def test_ml_pipeline():
    """Test ML pipeline"""
    print("\nTesting ML Pipeline...")
    ml = MLPipeline()
    
    # Test model initialization
    assert ml.model is not None, "Model initialization failed"
    print("  Model initialized successfully")
    
    # Test feature preprocessing
    test_features = {
        'ofi_1.0s': 0.5,
        'micro_price_1.0s': 50000.0,
        'realized_volatility_1.0s': 0.001
    }
    
    features_vector = ml.preprocess_features(test_features, time_remaining=600)
    print(f"  Feature vector shape: {features_vector.shape}")
    
    # Test prediction (should return neutral since model not trained)
    prediction = ml.predict(test_features, time_remaining=600)
    print(f"  Prediction: {prediction['prediction']}")
    print(f"  Confidence: {prediction['confidence']}")
    
    assert prediction['prediction'] == 'NEUTRAL', "Untrained model should return NEUTRAL"
    print("  [PASS] ML pipeline test passed")
    return True


def test_stochastic_bridge():
    """Test stochastic bridge"""
    print("\nTesting Stochastic Bridge...")
    bridge = StochasticBridge(initial_price=50000.0, window_duration=900)
    
    # Test parameter update
    bridge.update_parameters(current_price=50100.0, volatility_estimate=0.001)
    print(f"  Current price: ${bridge.current_price}")
    print(f"  Volatility: {bridge.volatility}")
    
    # Test price distribution calculation
    elapsed = 300  # 5 minutes
    distribution = bridge.calculate_price_distribution(elapsed)
    print(f"  Expected price: ${distribution['expected_price']:.2f}")
    print(f"  Std deviation: ${distribution['std_dev']:.2f}")
    
    # Test forecast range
    forecast = bridge.generate_forecast_range(elapsed, current_price=50100.0)
    print(f"  Predicted high: ${forecast['predicted_high']:.2f}")
    print(f"  Predicted low: ${forecast['predicted_low']:.2f}")
    print(f"  Expected close: ${forecast['expected_close']:.2f}")
    
    assert distribution['expected_price'] > 0, "Price calculation failed"
    print("  [PASS] Stochastic bridge test passed")
    return True


def test_error_handler():
    """Test error handler"""
    print("\nTesting Error Handler...")
    error_handler = ErrorHandler()
    
    # Record some errors
    error_handler.record_error("test_component", Exception("Test error"))
    error_handler.record_error("test_component", ValueError("Test value error"))
    
    stats = error_handler.get_error_stats()
    print(f"  Error counts: {stats['error_counts']}")
    print(f"  Last errors: {list(stats['last_errors'].keys())}")
    
    # Test circuit breaker
    for i in range(6):
        error_handler.record_error("circuit_test", Exception("Repeated error"))
    
    is_active = error_handler.is_circuit_breaker_active("circuit_test")
    print(f"  Circuit breaker active: {is_active}")
    
    assert is_active, "Circuit breaker should be active"
    print("  [PASS] Error handler test passed")
    return True


def test_health_checker():
    """Test health checker"""
    print("\nTesting Health Checker...")
    health_checker = HealthChecker()
    
    # Test component health check
    def healthy_component():
        return True
    
    def unhealthy_component():
        raise Exception("Component error")
    
    health_checker.check_component("healthy", healthy_component)
    health_checker.check_component("unhealthy", unhealthy_component)
    
    status = health_checker.get_health_status()
    print(f"  Overall healthy: {status['overall_healthy']}")
    print(f"  Healthy components: {status['healthy_components']}/{status['total_components']}")
    
    assert status['healthy_components'] == 1, "Health check failed"
    print("  [PASS] Health checker test passed")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("HFT Engine Component Tests")
    print("=" * 60)
    
    tests = [
        test_order_book,
        test_microstructure_features,
        test_ml_pipeline,
        test_stochastic_bridge,
        test_error_handler,
        test_health_checker
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  [FAIL] Test failed with error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("[SUCCESS] All tests passed successfully!")
        return 0
    else:
        print("[FAILURE] Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())