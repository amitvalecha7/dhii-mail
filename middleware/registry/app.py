from flask import Flask, jsonify, request
import os
import json

app = Flask(__name__)

# Simple in-memory registry for now
PLUGINS = [
    {
        "id": "com.dhiimail.marketing",
        "name": "Marketing Genius",
        "version": "1.0.0",
        "description": "AI-powered marketing campaign generator",
        "manifest_url": "/plugins/marketing/manifest.json"
    },
    {
        "id": "com.dhiimail.finance",
        "name": "Finance Flow",
        "version": "1.2.0",
        "description": "Invoice processing and expense tracking",
        "manifest_url": "/plugins/finance/manifest.json"
    }
]

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "service": "plugin-registry"}), 200

@app.route('/api/v1/plugins', methods=['GET'])
def list_plugins():
    return jsonify({"plugins": PLUGINS}), 200

@app.route('/api/v1/plugins/<plugin_id>', methods=['GET'])
def get_plugin(plugin_id):
    plugin = next((p for p in PLUGINS if p['id'] == plugin_id), None)
    if plugin:
        return jsonify(plugin), 200
    return jsonify({"error": "Plugin not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
