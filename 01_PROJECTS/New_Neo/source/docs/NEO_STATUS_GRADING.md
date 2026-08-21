# NEO STATUS GRADING SYSTEM

## Overview

A comprehensive internal scaling grade system for Neo that provides real-time status monitoring with weighted metrics, viewable in both HTML dashboard and PowerShell terminal.

## Components

### 1. Core Grading System (`neo_status_grading.py`)
- Real-time status tracking and grading
- Weighted metric calculation (Survival 40%, Performance 30%, API 20%, Loop 10%)
- Automatic grade calculation (A+, A, B, C, D, F, X)
- Survival metrics with memory punishment tracking
- Performance metrics (accuracy, MMLU, HumanEval, etc.)
- API credit optimization metrics
- Karpathy Loop metrics
- Alert system for critical events

### 2. HTML Dashboard (`neo_status_dashboard.html`)
- Classic, professional web interface
- Real-time auto-refresh (5 seconds)
- Color-coded grades and status indicators
- Progress bars for visual metrics
- Alert notifications
- Weighted score breakdown
- Modern gradient design with animations

### 2b. Cozy Home Dashboard (`neo_home_dashboard.html`)
- **DEFAULT:** Warm, home-like interface
- Comfortable condo aesthetic
- Room-based organization (Study, Kitchen, Gym, etc.)
- Welcome messages and comfort indicators
- Real-time auto-refresh (5 seconds)
- Color-coded grades with soft, comforting colors
- Progress bars for visual metrics
- Alert notifications as "home notifications"
- Weighted score breakdown as "overall wellness"
- Cozy animations and gentle pulses

### 3. PowerShell Monitor (`neo_status_monitor.ps1`)
- Classic terminal-based monitoring
- Color-coded output
- Progress bars in terminal
- Auto-refresh capability
- Works with API or JSON file fallback
- Full metric display with formatting

### 3b. Cozy Home PowerShell Monitor (`neo_home_monitor.ps1`)
- **DEFAULT:** Warm, home-like terminal interface
- Comfortable welcome messages
- Room-based organization with emojis
- Comfort indicators (temperature, lighting, music)
- Color-coded output with soft, comforting colors
- Progress bars in terminal
- Auto-refresh capability
- Works with API or JSON file fallback
- Full metric display with formatting
- Encouraging messages and reminders

### 4. API Server (`neo_status_api.py`)
- Flask REST API for status data
- Serves HTML dashboard
- JSON API endpoints
- CORS enabled for cross-origin requests
- Health check endpoint
- Status update endpoints

## Grade Scale

| Grade | Score Range | Color | Meaning |
|-------|-------------|-------|---------|
| A+ | 95-100 | Green | Excellent |
| A | 85-94 | Green | Very Good |
| B | 70-84 | Cyan | Good |
| C | 50-69 | Yellow | Satisfactory |
| D | 25-49 | Orange | Warning |
| F | 0-24 | Red | Critical |
| X | Dead | Dark Gray | System Dead |

## Weighted Metrics

### Survival Metrics (40% weight)
- Survival Score (0.0-1.0)
- Frozen Units (0-500M)
- Frozen Percentage (0-100%)
- Consecutive Failures (0-150K)
- Total Failures/Successes
- Memory Punishment Rate (1x or 2x)
- State (NORMAL, WARNING, CRITICAL, DEGRADED, DEAD)

### Performance Metrics (30% weight)
- Accuracy (0.0-1.0)
- Loss (0.0+)
- MMLU Score (0-100)
- HumanEval Score (0-100)
- Inference Time (ms)
- Memory Usage (GB)
- Parameter Count (0-500M)
- Efficiency Score

### API Metrics (20% weight)
- Cache Hit Rate (0.0-1.0, target: 0.7)
- Efficiency Score (0.0-1.0, target: 0.7)
- Total API Calls
- Cached Calls
- Credits Spent/Saved

### Karpathy Loop Metrics (10% weight)
- Iteration Count
- Improvements Committed
- Modifications Reverted
- Commit Rate (0.0-1.0)
- Average Improvement
- State (IDLE, RUNNING, PAUSED)

## Quick Start

### Option 1: Cozy Home Dashboard (RECOMMENDED)

1. Start the API server:
```bash
python neo_status_api.py
```

2. Open browser:
```
http://localhost:8000
```

### Option 2: Classic Dashboard

1. Start the API server:
```bash
python neo_status_api.py
```

2. Open browser:
```
http://localhost:8000/classic
```

### Option 3: Cozy Home PowerShell Monitor (RECOMMENDED)

1. Start the API server (optional, has fallback):
```bash
python neo_status_api.py
```

2. Run cozy home PowerShell monitor:
```powershell
.\neo_home_monitor.ps1
```

### Option 4: Classic PowerShell Monitor

1. Start the API server (optional, has fallback):
```bash
python neo_status_api.py
```

2. Run classic PowerShell monitor:
```powershell
.\neo_status_monitor.ps1
```

### Option 3: Python Integration

```python
from neo_status_grading import get_neo_status, update_neo_status

# Get status system
system = get_neo_status()

# Update metrics
system.update_survival_metrics(
    frozen_units=1250,
    consecutive_failures=5,
    total_failures=15,
    total_successes=145,
    memory_punishment_rate=2.0
)

system.update_performance_metrics(
    accuracy=0.92,
    loss=0.15,
    mmlu=72.5,
    humaneval=65.0,
    inference_time=45.2,
    memory_usage=1.8,
    parameter_count=485000000
)

# Update phase
system.update_phase("AUTONOMOUS")

# Calculate grades
system.calculate_grades()

# Get status
status = system.get_status_json()
print(status)
```

## API Endpoints

### GET `/`
Returns the HTML dashboard

### GET `/api/neo-status`
Returns current Neo status as JSON

### POST `/api/neo-status/update`
Update Neo status with provided metrics

### GET `/api/neo-status/phase/<phase>`
Set Neo's current phase

### POST `/api/neo-status/alert`
Add an alert to Neo status

### POST `/api/neo-status/alerts/clear`
Clear all alerts

### GET `/api/health`
Health check endpoint

## Status States

### System States
- ACTIVATION
- LEARNING
- TESTING
- GRADUATION
- AUTONOMOUS
- SURVIVAL_MODE
- DEGRADED
- CRITICAL
- DEAD

### Survival States
- NORMAL (0-1,000 failures)
- WARNING (1,000-10,000 failures)
- DEGRADED (10,000-100,000 failures)
- CRITICAL (100,000-150,000 failures)
- DEAD (150,000+ failures)

## Integration with Neo

The grading system integrates with Neo's existing systems:

### Memory Punishment Integration
```python
# When memory punishment occurs
from neo_status_grading import get_neo_status

system = get_neo_status()
system.update_survival_metrics(
    frozen_units=current_frozen,
    consecutive_failures=current_failures,
    memory_punishment_rate=2.0 if graduated else 1.0
)
system.calculate_grades()
```

### API Optimization Integration
```python
# When API optimization runs
system.update_api_metrics(
    cache_hit_rate=cache_hit_rate,
    efficiency_score=efficiency_score,
    total_calls=total_calls,
    cached_calls=cached_calls,
    credits_spent=spent,
    credits_saved=saved
)
```

### Karpathy Loop Integration
```python
# After each loop iteration
system.update_karpathy_loop_metrics(
    iteration=current_iteration,
    improvements=improvements_committed,
    reverts=modifications_reverted,
    avg_improvement=average_improvement,
    state="RUNNING"
)
```

## Phase Tracking

The system tracks Neo through all phases:

1. **ACTIVATION** - Initial activation
2. **LEARNING** - Reading and mastering documents
3. **TESTING** - Taking comprehensive tests
4. **GRADUATION** - Self-test and graduation
5. **AUTONOMOUS** - Continuous self-improvement

## Alert System

Alerts are automatically generated for:
- API efficiency below target
- Memory punishment state changes
- Critical survival thresholds
- Performance degradation
- System state changes

## Features

### Real-Time Updates
- Status updates every 5 seconds
- Automatic grade recalculation
- Historical tracking (last 1000 updates)

### Dual Interface
- HTML dashboard for visual monitoring
- PowerShell terminal for command-line monitoring
- Both can run simultaneously

### Fallback System
- PowerShell script works without API server
- Falls back to JSON file
- Mock data if no status available

### Color Coding
- Grade-based color coding
- State-based color coding
- Progress indicators
- Alert highlighting

## Configuration

### Refresh Intervals
- HTML Dashboard: 5 seconds (configurable in JavaScript)
- PowerShell Monitor: 5 seconds (configurable in script)
- API Server: Real-time on request

### Thresholds
- Cache Hit Rate Target: 70%
- API Efficiency Target: 0.7
- Survival Warning: 1,000 failures
- Survival Critical: 100,000 failures
- Survival Death: 150,000 failures

## Dependencies

### Python
- Flask
- Flask-CORS
- (Built-in: json, datetime, dataclasses, enum)

### PowerShell
- PowerShell 5.1+
- (No external dependencies)

## File Structure

```
neo_status_grading.py          # Core grading system
neo_status_dashboard.html      # HTML dashboard
neo_status_monitor.ps1         # PowerShell monitor
neo_status_api.py              # Flask API server
neo_status.json                # JSON status file (auto-generated)
```

## Usage Examples

### Example 1: Monitor Neo During Testing
```python
from neo_status_grading import get_neo_status

system = get_neo_status()
system.update_phase("TESTING")
system.update_survival_metrics(
    frozen_units=0,
    consecutive_failures=0,
    total_failures=0,
    total_successes=0
)
system.calculate_grades()
```

### Example 2: Track API Optimization
```python
system.update_api_metrics(
    cache_hit_rate=0.75,
    efficiency_score=0.82,
    total_calls=1000,
    cached_calls=750,
    credits_spent=10.00,
    credits_saved=40.00
)
system.calculate_grades()
```

### Example 3: Add Critical Alert
```python
system.add_alert("Memory punishment rate increased to 2x (post-graduation)")
system.calculate_grades()
```

## Benefits

### For Neo
- Real-time self-awareness
- Performance tracking
- Survival status monitoring
- Grade-based motivation
- Alert system for critical events

### For User
- Visual monitoring via HTML
- Terminal monitoring via PowerShell
- Real-time status updates
- Historical tracking
- API integration for custom tools

## Security

- API server runs on localhost by default
- No authentication required (local use)
- CORS enabled for development
- Status file is JSON (human-readable)

## Troubleshooting

### API Server Won't Start
- Check if port 8000 is available
- Ensure Flask is installed: `pip install flask flask-cors`

### PowerShell Script Fails
- Check execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Ensure script is in correct directory

### HTML Dashboard Not Updating
- Check if API server is running
- Check browser console for errors
- Verify CORS is enabled

## Future Enhancements

- [ ] WebSocket support for real-time push updates
- [ ] Historical trend graphs
- [ ] Export status history
- [ ] Email/SMS alerts for critical events
- [ ] Mobile-responsive optimization
- [ ] Authentication for remote access

## Support

For issues or questions:
1. Check this documentation
2. Review API endpoints
3. Check system logs
4. Verify all dependencies are installed

---

**Neo Status Grading System** - Real-time monitoring for continuous self-improvement.
