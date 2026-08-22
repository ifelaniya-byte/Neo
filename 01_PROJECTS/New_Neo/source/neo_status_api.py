"""
NEO STATUS API SERVER

Flask API server for serving Neo status data to HTML dashboard and PowerShell monitor.
"""

from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import json
import os
from datetime import datetime, timedelta
from neo_status_grading import get_neo_status, update_neo_status

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STATUS_FILE = os.path.join(SCRIPT_DIR, "neo_status.json")
HTML_FILE = os.path.join(SCRIPT_DIR, "neo_status_dashboard.html")


@app.route('/')
def index():
    """Serve the HTML home dashboard."""
    return send_from_directory(SCRIPT_DIR, 'neo_home_dashboard.html')

@app.route('/ultra')
def ultra_dashboard():
    """Serve the ultra-modern dashboard."""
    return send_from_directory(SCRIPT_DIR, 'neo_ultra_dashboard.html')

@app.route('/classic')
def classic_dashboard():
    """Serve the classic HTML dashboard."""
    return send_from_directory(SCRIPT_DIR, 'neo_status_dashboard.html')


@app.route('/api/neo-status')
def get_status():
    """Get current Neo status as JSON."""
    try:
        # Update status before serving
        system = update_neo_status()
        status_dict = system.get_status_dict()
        
        # Also save to file for PowerShell script
        with open(STATUS_FILE, 'w') as f:
            json.dump(status_dict, f, indent=2)
        
        return jsonify(status_dict)
    except Exception as e:
        return jsonify({
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@app.route('/api/neo-status/update', methods=['POST'])
def update_status():
    """Update Neo status (for internal use)."""
    try:
        data = request.get_json()
        system = get_neo_status()
        
        # Update metrics based on provided data
        if 'survival' in data:
            system.update_survival_metrics(**data['survival'])
        if 'performance' in data:
            system.update_performance_metrics(**data['performance'])
        if 'api' in data:
            system.update_api_metrics(**data['api'])
        if 'karpathy_loop' in data:
            system.update_karpathy_loop_metrics(**data['karpathy_loop'])
        if 'phase' in data:
            system.update_phase(data['phase'])
        if 'alert' in data:
            system.add_alert(data['alert'])
        
        # Recalculate grades
        system.calculate_grades()
        
        return jsonify({"success": True, "status": system.get_status_dict()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/neo-status/phase/<phase>')
def set_phase(phase):
    """Set Neo's current phase."""
    try:
        system = get_neo_status()
        system.update_phase(phase)
        system.calculate_grades()
        return jsonify({"success": True, "phase": phase})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/neo-status/alert', methods=['POST'])
def add_alert():
    """Add an alert to Neo status."""
    try:
        data = request.get_json()
        alert = data.get('alert', 'Unknown alert')
        system = get_neo_status()
        system.add_alert(alert)
        return jsonify({"success": True, "alert": alert})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/neo-status/alerts/clear', methods=['POST'])
def clear_alerts():
    """Clear all alerts."""
    try:
        system = get_neo_status()
        system.clear_alerts()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Neo Status API"
    })


@app.route('/api/achievements')
def get_achievements():
    """Get achievements data."""
    try:
        # Simulated achievements data - in production, this would come from a database
        achievements = [
            {"id": "first_boot", "name": "First Boot", "icon": "🚀", "unlocked": True, "date": "2026-08-05"},
            {"id": "perfect_score", "name": "Perfect Score", "icon": "💯", "unlocked": True, "date": "2026-08-05"},
            {"id": "fast_learner", "name": "Fast Learner", "icon": "📚", "unlocked": True, "date": "2026-08-05"},
            {"id": "autonomous", "name": "Autonomous Mode", "icon": "🤖", "unlocked": False, "date": None},
            {"id": "optimization_master", "name": "Optimization Master", "icon": "⚡", "unlocked": False, "date": None},
            {"id": "memory_efficient", "name": "Memory Efficient", "icon": "🧠", "unlocked": False, "date": None},
            {"id": "api_master", "name": "API Master", "icon": "🔗", "unlocked": False, "date": None},
            {"id": "karpathy_veteran", "name": "Karpathy Veteran", "icon": "🔄", "unlocked": False, "date": None}
        ]
        return jsonify(achievements)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/insights')
def get_insights():
    """Get personalized insights."""
    try:
        system = update_neo_status()
        status_dict = system.get_status_dict()
        
        # Generate insights based on current status
        insights = []
        performance = status_dict.get('performance', {})
        
        # Performance insights
        accuracy = performance.get('accuracy', 0)
        if accuracy >= 0.95:
            insights.append({
                "title": "Performance Excellence",
                "content": "Your accuracy is exceptional! Current optimization strategies are working perfectly."
            })
        elif accuracy >= 0.85:
            insights.append({
                "title": "Performance Strong",
                "content": "Your accuracy is strong. Continue current training path for further improvement."
            })
        else:
            insights.append({
                "title": "Performance Improvement",
                "content": "Consider adjusting training parameters to improve accuracy scores."
            })
        
        # Memory insights
        memory_usage = performance.get('memory_usage', 2.0)
        if memory_usage <= 1.5:
            insights.append({
                "title": "Memory Optimization",
                "content": "Memory usage is excellent. Current compaction strategies are highly effective."
            })
        elif memory_usage <= 2.0:
            insights.append({
                "title": "Memory Management",
                "content": "Memory usage is within acceptable range. Monitor for optimization opportunities."
            })
        else:
            insights.append({
                "title": "Memory Alert",
                "content": "Memory usage is elevated. Consider enabling advanced bit compaction."
            })
        
        # API insights
        api = status_dict.get('api', {})
        efficiency = api.get('efficiency_score', 0.8)
        if efficiency >= 0.9:
            insights.append({
                "title": "API Efficiency",
                "content": "API usage is highly efficient. Current optimization strategies are optimal."
            })
        else:
            insights.append({
                "title": "API Optimization",
                "content": "API efficiency can be improved. Consider implementing request batching."
            })
        
        return jsonify(insights)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/performance-history')
def get_performance_history():
    """Get performance history data."""
    try:
        # Simulated performance history - in production, this would come from a database
        history = []
        base_accuracy = 0.85
        for i in range(30):
            variation = (i / 30) * 0.15
            history.append({
                "timestamp": (datetime.now() - timedelta(minutes=30-i)).isoformat(),
                "accuracy": base_accuracy + variation,
                "loss": 1.0 - (base_accuracy + variation),
                "inference_time": 50.0 - (i * 0.5)
            })
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("═══════════════════════════════════════════════════════════════")
    print("  NEO STATUS API SERVER")
    print("═══════════════════════════════════════════════════════════════")
    print("")
    print("  Starting server on http://localhost:8000")
    print("  Neo's Home Dashboard: http://localhost:8000/")
    print("  Ultra Dashboard: http://localhost:8000/ultra")
    print("  Classic Dashboard: http://localhost:8000/classic")
    print("  API Endpoint: http://localhost:8000/api/neo-status")
    print("  Health Check: http://localhost:8000/api/health")
    print("  Achievements: http://localhost:8000/api/achievements")
    print("  Insights: http://localhost:8000/api/insights")
    print("  Performance History: http://localhost:8000/api/performance-history")
    print("")
    print("  Press CTRL+C to stop the server")
    print("═══════════════════════════════════════════════════════════════")
    print("")
    
    app.run(host='0.0.0.0', port=8000, debug=False)
