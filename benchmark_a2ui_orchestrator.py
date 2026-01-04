
import time
import json
import uuid
from typing import Dict, Any, List
from a2ui_integration.data_structures import ComponentGraph
from a2ui_integration.a2ui_components_extended import A2UIComponents

def benchmark_direct_dict(iterations: int = 1000):
    """Benchmark creating UI structure using direct dictionary manipulation"""
    start_time = time.time()
    
    for _ in range(iterations):
        # Simulate creating a dashboard structure manually
        layout = {
            "component": {
                "Layout": {
                    "orientation": "horizontal",
                    "id": "layout",
                    "components": [
                        {
                            "component": {
                                "Card": {
                                    "title": {"literalString": "Email Stats"},
                                    "content": {"literalString": "You have 5 unread emails"},
                                    "actions": []
                                }
                            }
                        },
                        {
                            "component": {
                                "Card": {
                                    "title": {"literalString": "Upcoming Meetings"},
                                    "content": {"literalString": "Team Sync at 2:00 PM"},
                                    "actions": []
                                }
                            }
                        },
                        {
                            "component": {
                                "Card": {
                                    "title": {"literalString": "Tasks"},
                                    "content": {"literalString": "3 high priority tasks"},
                                    "actions": []
                                }
                            }
                        }
                    ]
                }
            }
        }
        
        # Serialize to ensure fair comparison (as to_json does serialization/resolution)
        # Although to_json returns a dict, it does processing. 
        # So we should compare the construction + "ready for response" state.
        # Direct dict is already ready.
        pass
        
    end_time = time.time()
    return (end_time - start_time) / iterations

def benchmark_component_graph(iterations: int = 1000):
    """Benchmark creating UI structure using ComponentGraph"""
    start_time = time.time()
    
    for _ in range(iterations):
        graph = ComponentGraph()
        
        # Create root layout
        layout_id = graph.add_node("Layout", {
            "orientation": "horizontal"
        })
        graph.set_root(layout_id)
        
        # Add cards
        card1_id = graph.add_node("Card", {
            "title": "Email Stats",
            "content": "You have 5 unread emails",
            "actions": []
        })
        
        card2_id = graph.add_node("Card", {
            "title": "Upcoming Meetings",
            "content": "Team Sync at 2:00 PM",
            "actions": []
        })
        
        card3_id = graph.add_node("Card", {
            "title": "Tasks",
            "content": "3 high priority tasks",
            "actions": []
        })
        
        # Link components
        graph.add_child(layout_id, card1_id)
        graph.add_child(layout_id, card2_id)
        graph.add_child(layout_id, card3_id)
        
        # Resolve to final structure
        result = graph.to_json()
        
    end_time = time.time()
    return (end_time - start_time) / iterations

def run_benchmark():
    print("Running A2UI Orchestrator Benchmarks...")
    print("-" * 50)
    
    iterations = 10000
    
    print(f"Iterations: {iterations}")
    
    # Warmup
    benchmark_direct_dict(100)
    benchmark_component_graph(100)
    
    # Run benchmarks
    direct_time = benchmark_direct_dict(iterations)
    graph_time = benchmark_component_graph(iterations)
    
    print(f"Direct Dict Method:   {direct_time*1000:.4f} ms/op")
    print(f"Component Graph Method: {graph_time*1000:.4f} ms/op")
    
    diff = graph_time - direct_time
    percent = (diff / direct_time) * 100
    
    print("-" * 50)
    print(f"Difference: {diff*1000:.4f} ms ({percent:+.2f}%)")
    
    if graph_time < direct_time:
        print("RESULT: ComponentGraph is FASTER")
    else:
        print("RESULT: ComponentGraph is SLOWER (Expected due to abstraction overhead)")
        print("Note: The overhead is the cost of flexibility and validation.")

if __name__ == "__main__":
    run_benchmark()
