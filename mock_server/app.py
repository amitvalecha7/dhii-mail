from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "mock-orchestrator"}), 200

@app.route('/api/v1/orchestrate', methods=['POST'])
def orchestrate():
    """
    Simulates the A2UI Orchestrator response based on the input context.
    """
    data = request.json
    context = data.get('context', {})
    
    # Simple logic to simulate dynamic responses
    if 'dashboard' in context.get('route', ''):
        return jsonify({
            "action": "render_layout",
            "component_id": "root_dashboard",
            "schema": {
                "type": "container",
                "layout": "grid",
                "children": [
                    {
                        "type": "card",
                        "title": "Recent Emails",
                        "data_source": "/api/v1/emails/recent"
                    },
                    {
                        "type": "card",
                        "title": "Upcoming Meetings",
                        "data_source": "/api/v1/calendar/upcoming"
                    }
                ]
            }
        })

    return jsonify({
        "action": "render_message",
        "content": "I'm not sure what to show you for this context yet."
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
