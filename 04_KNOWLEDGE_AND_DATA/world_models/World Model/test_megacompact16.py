#!/usr/bin/env python3
"""
Test suite for MegaCompact16.

Tests core functionality including:
- Deterministic synthetic generation
- Time-causal feature construction
- No future leakage
- Constant-product AMM math
- Split integrity
- Audit checks
- Smoke test execution
"""

import sys
import os
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import numpy as np
    import pandas as pd
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("WARNING: numpy/pandas not available. Tests will be limited.")

try:
    import pytest
    PYTEST_AVAILABLE = True
except ImportError:
    PYTEST_AVAILABLE = False

try:
    from megacompact16 import (
        Config, SyntheticMarketGenerator, DataValidator,
        TimeCausalFeatureStore, DecisionPacketBuilder,
        ConstantProductAMM, MarketReplay, WalkForwardSplitter,
        AuditEngine, set_seed, sha256_hash, ArtifactStore,
        NormalizedEvent, DecisionPacket, EventType
    )
except ImportError as e:
    print(f"Failed to import megacompact16: {e}")
    sys.exit(1)


def test_deterministic_generation():
    """Test that identical seed creates identical synthetic events."""
    print("Testing deterministic synthetic generation...")

    config = Config()
    config.synthetic.seed = 42
    config.synthetic.days = 1
    config.synthetic.blocks_per_day = 10

    set_seed(42)
    generator1 = SyntheticMarketGenerator(config.synthetic)
    events1 = generator1.generate()

    set_seed(42)
    generator2 = SyntheticMarketGenerator(config.synthetic)
    events2 = generator2.generate()

    assert len(events1) == len(events2), "Event count should match"
    assert len(events1) > 0, "Should generate events"

    # Check that first events match
    assert events1[0].event_type == events2[0].event_type, "Event types should match"
    assert events1[0].block_number == events2[0].block_number, "Block numbers should match"

    print("[PASS] Deterministic generation test passed")


def test_time_causal_features():
    """Test that feature snapshots reject future event availability."""
    print("Testing time-causal feature construction...")

    config = Config()
    config.synthetic.seed = 42
    config.synthetic.days = 1
    config.synthetic.blocks_per_day = 10

    set_seed(42)
    generator = SyntheticMarketGenerator(config.synthetic)
    events = generator.generate()

    feature_store = TimeCausalFeatureStore(events, max_age_ms=5000)

    # Build snapshot at block 5
    decision_block = 5
    decision_time_ms = decision_block * 1200  # 1.2s per block
    features = feature_store.build_snapshot(decision_time_ms, decision_block)

    # Check that no features come from future blocks
    for feature_name, feature in features.items():
        assert feature.max_source_block <= decision_block, \
            f"Feature {feature_name} comes from block {feature.max_source_block} > decision block {decision_block}"

    print("[PASS] Time-causal features test passed")


def test_no_future_leakage():
    """Test that packets don't contain future data."""
    print("Testing no future leakage...")

    config = Config()
    config.synthetic.seed = 42
    config.synthetic.days = 1
    config.synthetic.blocks_per_day = 10

    set_seed(42)
    generator = SyntheticMarketGenerator(config.synthetic)
    events = generator.generate()

    feature_store = TimeCausalFeatureStore(events, max_age_ms=5000)
    packet_builder = DecisionPacketBuilder(config, feature_store)
    packets = packet_builder.build_packets(events)

    assert len(packets) > 0, "Should generate packets"

    # Check each packet
    for packet in packets:
        decision_block = packet.as_of["block_number"]
        decision_time = packet.as_of["decision_timestamp_ms"]

        # Check provenance
        source_timestamps = packet.provenance.get("feature_source_timestamps_ms", {})
        for feature_name, timestamp in source_timestamps.items():
            assert timestamp <= decision_time, \
                f"Feature {feature_name} has timestamp {timestamp} > decision time {decision_time}"

        source_blocks = packet.provenance.get("feature_source_blocks", {})
        for feature_name, block in source_blocks.items():
            assert block <= decision_block, \
                f"Feature {feature_name} comes from block {block} > decision block {decision_block}"

    print("[PASS] No future leakage test passed")


def test_constant_product_amm():
    """Test constant-product AMM math."""
    print("Testing constant-product AMM math...")

    amm = ConstantProductAMM()

    # Test case: 1000 ETH, 2,000,000 USDC, swap 100 ETH
    reserve_in = 1000.0
    reserve_out = 2000000.0
    amount_in = 100.0
    fee = 0.003  # 0.3%

    amount_out = amm.calculate_amount_out(reserve_in, reserve_out, amount_in, fee)

    # Manual calculation:
    # amount_in_after_fee = 100 * (1 - 0.003) = 99.7
    # amount_out = 2,000,000 * 99.7 / (1000 + 99.7) = 2,000,000 * 99.7 / 1099.7 ≈ 181,468.49
    expected_amount_out = 2000000.0 * (amount_in * (1 - fee)) / (reserve_in + amount_in * (1 - fee))

    assert abs(amount_out - expected_amount_out) < 0.01, \
        f"Amount out {amount_out} doesn't match expected {expected_amount_out}"

    # Test price impact
    price_impact = amm.calculate_price_impact(reserve_in, reserve_out, amount_in, fee)
    assert price_impact > 0, "Price impact should be positive"
    assert price_impact < 1, "Price impact should be less than 100%"

    print("[PASS] Constant-product AMM test passed")


def test_split_integrity():
    """Test that splits have no overlap."""
    print("Testing split integrity...")

    config = Config()
    config.splits.train_fraction = 0.4
    config.splits.validation_fraction = 0.2
    config.splits.calibration_fraction = 0.2
    config.splits.test_fraction = 0.2

    config.synthetic.seed = 42
    config.synthetic.days = 1
    config.synthetic.blocks_per_day = 10

    set_seed(42)
    generator = SyntheticMarketGenerator(config.synthetic)
    events = generator.generate()

    feature_store = TimeCausalFeatureStore(events, max_age_ms=5000)
    packet_builder = DecisionPacketBuilder(config, feature_store)
    packets = packet_builder.build_packets(events)

    splitter = WalkForwardSplitter(config)
    splits = splitter.split_packets(packets)

    # Check no overlap
    train_blocks = [p.as_of["block_number"] for p in splits["train"]]
    val_blocks = [p.as_of["block_number"] for p in splits["validation"]]
    cal_blocks = [p.as_of["block_number"] for p in splits["calibration"]]
    test_blocks = [p.as_of["block_number"] for p in splits["test"]]

    assert len(set(train_blocks) & set(val_blocks)) == 0, "Train and validation should not overlap"
    assert len(set(val_blocks) & set(cal_blocks)) == 0, "Validation and calibration should not overlap"
    assert len(set(cal_blocks) & set(test_blocks)) == 0, "Calibration and test should not overlap"

    # Check chronological ordering
    if train_blocks and val_blocks:
        assert max(train_blocks) < min(val_blocks), "Train should come before validation"
    if val_blocks and cal_blocks:
        assert max(val_blocks) < min(cal_blocks), "Validation should come before calibration"
    if cal_blocks and test_blocks:
        assert max(cal_blocks) < min(test_blocks), "Calibration should come before test"

    print("[PASS] Split integrity test passed")


def test_audit_checks():
    """Test audit engine functionality."""
    print("Testing audit checks...")

    config = Config()
    config.synthetic.seed = 42
    config.synthetic.days = 1
    config.synthetic.blocks_per_day = 10

    set_seed(42)
    generator = SyntheticMarketGenerator(config.synthetic)
    events = generator.generate()

    feature_store = TimeCausalFeatureStore(events, max_age_ms=5000)
    packet_builder = DecisionPacketBuilder(config, feature_store)
    packets = packet_builder.build_packets(events)

    # Create dummy labels
    from megacompact16 import OutcomeLabel
    labels = []
    for packet in packets[:5]:  # Create labels for first 5 packets
        label = OutcomeLabel(
            decision_id=packet.decision_id,
            action_id=packet.action_candidates[0].action_id if packet.action_candidates else "",
            quoted_output_usd=100.0,
            realized_output_usd=100.0,
            input_cost_usd=100.0,
            gas_usd=1.0,
            protocol_fees_usd=0.3,
            borrow_fees_usd=0.0,
            bridge_fees_usd=0.0,
            slippage_cost_usd=0.5,
            revert_cost_usd=0.0,
            other_costs_usd=0.0,
            gross_pnl_usd=0.0,
            net_pnl_usd=-1.8,
            reverted=False,
            included_before_deadline=True,
            inclusion_delay_blocks=1,
            outcome_timestamp_ms=packet.as_of["decision_timestamp_ms"] + 5000,
            outcome_block=packet.as_of["block_number"] + 5
        )
        labels.append(label)

    # Create temporary artifact store
    temp_dir = tempfile.mkdtemp()
    try:
        artifact_store = ArtifactStore(temp_dir)
        audit_engine = AuditEngine(artifact_store)
        audit_results = audit_engine.run_all_audits(packets, labels, config)

        # Check that audits ran
        assert "feature_timing" in audit_results, "Feature timing audit should exist"
        assert "block_timing" in audit_results, "Block timing audit should exist"
        assert "label_separation" in audit_results, "Label separation audit should exist"
        assert "split_integrity" in audit_results, "Split integrity audit should exist"

        # Check that audits pass (with proper construction)
        assert audit_results["feature_timing"]["passed"], "Feature timing audit should pass"
        assert audit_results["block_timing"]["passed"], "Block timing audit should pass"

        print("[PASS] Audit checks test passed")
    finally:
        import time
        time.sleep(0.5)
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            print(f"[WARN] Could not clean up temp directory {temp_dir}")


def test_smoke_execution():
    """Test that smoke test can execute."""
    print("Testing smoke test execution...")

    # Create temporary directory for artifacts
    temp_dir = tempfile.mkdtemp()
    try:
        # Create minimal config
        config_data = {
            "mode": "synth",
            "preset": "smoke",
            "synthetic": {
                "days": 1,
                "blocks_per_day": 10,
                "num_tokens": 2,
                "num_pools": 3,
                "seed": 42
            },
            "splits": {
                "train_fraction": 0.4,
                "validation_fraction": 0.2,
                "calibration_fraction": 0.2,
                "test_fraction": 0.2
            },
            "output": {
                "root": temp_dir
            },
            "seed": 42
        }

        config = Config(**config_data)
        set_seed(42)

        artifact_store = ArtifactStore(temp_dir)

        # Generate synthetic data
        generator = SyntheticMarketGenerator(config.synthetic)
        events = generator.generate()

        assert len(events) > 0, "Should generate events"

        # Save events
        events_df = pd.DataFrame([e.model_dump() for e in events])
        artifact_store.save_parquet(events_df, "data/normalized/events.parquet")

        # Validate
        validator = DataValidator(config)
        valid_events = validator.validate_events(events)

        # Build packets
        feature_store = TimeCausalFeatureStore(valid_events, max_age_ms=5000)
        packet_builder = DecisionPacketBuilder(config, feature_store)
        packets = packet_builder.build_packets(valid_events)

        assert len(packets) > 0, "Should build packets"

        # Save packets
        packets_df = pd.DataFrame([p.model_dump() for p in packets])
        artifact_store.save_parquet(packets_df, "data/packets/packets.parquet")

        # Check artifacts were created
        assert artifact_store.path("data/normalized/events.parquet").exists(), "Events file should exist"
        assert artifact_store.path("data/packets/packets.parquet").exists(), "Packets file should exist"

        print("[PASS] Smoke execution test passed")
    finally:
        # Give Windows time to release file handles
        import time
        time.sleep(0.5)
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            print(f"[WARN] Could not clean up temp directory {temp_dir}")


def test_constraints():
    """Test constraint checking."""
    print("Testing constraint checking...")

    from megacompact16 import ConstraintEngine, Verdict, ReasonCode

    config = Config()
    config.max_feature_age_ms = 5000
    config.constraints.max_price_impact_bps = 50
    config.constraints.max_gas_usd = 5.0

    constraint_engine = ConstraintEngine(config)

    # Create a valid packet
    packet = DecisionPacket(
        decision_id="test",
        as_of={
            "chain_id": 42161,
            "block_number": 100,
            "block_hash": "0x123",
            "decision_timestamp_ms": 120000,
            "max_feature_age_ms": 5000
        },
        objective={"capital_usd": 1000},
        provenance={
            "feature_source_timestamps_ms": {"price": 119000},
            "feature_source_blocks": {"price": 99}
        },
        constraints={}
    )

    # Create a valid candidate
    from megacompact16 import ActionCandidate
    candidate = ActionCandidate(
        action_id="test_action",
        route=[],
        trade_size_usd=100,
        borrow={"asset": "", "amount": 0.0},
        slippage_limit_bps=30,
        gas_policy={},
        deadline_block=105
    )

    # Create a prediction
    from megacompact16 import ModelForecast
    prediction = ModelForecast(
        mean_net_pnl_usd=5.0,
        pnl_q05_usd=2.0,
        pnl_q50_usd=5.0,
        pnl_q95_usd=8.0,
        aleatoric_std=1.0,
        epistemic_std=0.5,
        revert_probability=0.01,
        inclusion_probability=0.95,
        ood_score=0.3,
        regime_score=0.5
    )

    constraints = constraint_engine.check_constraints(packet, candidate, prediction)

    assert len(constraints) > 0, "Should have constraints"
    assert all("name" in c for c in constraints), "Each constraint should have a name"
    assert all("passed" in c for c in constraints), "Each constraint should have passed status"

    print("[PASS] Constraints test passed")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("MegaCompact16 Test Suite")
    print("=" * 60)

    if not NUMPY_AVAILABLE:
        print("WARNING: numpy/pandas not available. Skipping most tests.")
        print("Install requirements with: pip install -r requirements.txt")
        return False

    tests = [
        test_deterministic_generation,
        test_time_causal_features,
        test_no_future_leakage,
        test_constant_product_amm,
        test_split_integrity,
        test_audit_checks,
        test_smoke_execution,
        test_constraints
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} failed: {e}")
            failed += 1
            import traceback
            traceback.print_exc()

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
