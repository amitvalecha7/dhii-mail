from typing import Dict, Any, List

# Skill Store UI Helper Functions
def create_kernel_dashboard_ui(dashboard_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create A2UI components for kernel dashboard"""
    return [
        {
            "beginRendering": {
                "surfaceId": "kernel-dashboard",
                "root": "dashboard-container",
                "styles": {"primaryColor": "#3b82f6", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "kernel-dashboard",
                "components": [
                    {
                        "id": "dashboard-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["header-section", "stats-section", "plugins-section"]
                                }
                            }
                        }
                    },
                    {
                        "id": "header-section",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["dashboard-title", "dashboard-subtitle"]
                                }
                            }
                        }
                    },
                    {
                        "id": "dashboard-title",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Kernel Dashboard"},
                                "style": {"fontSize": "24px", "fontWeight": "bold", "color": "#1f2937"}
                            }
                        }
                    },
                    {
                        "id": "dashboard-subtitle",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Plugin Management & System Overview"},
                                "style": {"fontSize": "14px", "color": "#6b7280", "marginTop": "4px"}
                            }
                        }
                    },
                    {
                        "id": "stats-section",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["total-plugins-card", "enabled-plugins-card", "types-card"]
                                }
                            }
                        }
                    },
                    {
                        "id": "total-plugins-card",
                        "component": {
                            "Card": {
                                "child": "total-plugins-content",
                                "style": {"padding": "16px", "margin": "8px", "backgroundColor": "#f8fafc"}
                            }
                        }
                    },
                    {
                        "id": "total-plugins-content",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["total-plugins-number", "total-plugins-label"]
                                }
                            }
                        }
                    },
                    {
                        "id": "total-plugins-number",
                        "component": {
                            "Text": {
                                "text": {"literalString": str(dashboard_data["stats"]["total_plugins"])},
                                "style": {"fontSize": "20px", "fontWeight": "bold", "color": "#3b82f6"}
                            }
                        }
                    },
                    {
                        "id": "total-plugins-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Total Plugins"},
                                "style": {"fontSize": "12px", "color": "#6b7280"}
                            }
                        }
                    },
                    {
                        "id": "enabled-plugins-card",
                        "component": {
                            "Card": {
                                "child": "enabled-plugins-content",
                                "style": {"padding": "16px", "margin": "8px", "backgroundColor": "#f0fdf4"}
                            }
                        }
                    },
                    {
                        "id": "enabled-plugins-content",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["enabled-plugins-number", "enabled-plugins-label"]
                                }
                            }
                        }
                    },
                    {
                        "id": "enabled-plugins-number",
                        "component": {
                            "Text": {
                                "text": {"literalString": str(dashboard_data["stats"]["enabled_plugins"])},
                                "style": {"fontSize": "20px", "fontWeight": "bold", "color": "#10b981"}
                            }
                        }
                    },
                    {
                        "id": "enabled-plugins-label",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Enabled Plugins"},
                                "style": {"fontSize": "12px", "color": "#6b7280"}
                            }
                        }
                    },
                    {
                        "id": "plugins-section",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["plugins-header", "plugins-list"]
                                }
                            }
                        }
                    },
                    {
                        "id": "plugins-header",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Installed Plugins"},
                                "style": {"fontSize": "18px", "fontWeight": "600", "color": "#1f2937", "marginBottom": "12px"}
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "kernel-dashboard",
                "path": "/",
                "contents": dashboard_data
            }
        }
    ]

def create_plugin_store_ui(store_plugins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create A2UI components for plugin store"""
    return [
        {
            "beginRendering": {
                "surfaceId": "plugin-store",
                "root": "store-container",
                "styles": {"primaryColor": "#8b5cf6", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "plugin-store",
                "components": [
                    {
                        "id": "store-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["store-header", "plugins-grid"]
                                }
                            }
                        }
                    },
                    {
                        "id": "store-header",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["store-title", "store-subtitle"]
                                }
                            }
                        }
                    },
                    {
                        "id": "store-title",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Plugin Store"},
                                "style": {"fontSize": "24px", "fontWeight": "bold", "color": "#1f2937"}
                            }
                        }
                    },
                    {
                        "id": "store-subtitle",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Discover and install plugins to extend functionality"},
                                "style": {"fontSize": "14px", "color": "#6b7280", "marginTop": "4px"}
                            }
                        }
                    },
                    {
                        "id": "plugins-grid",
                        "component": {
                            "Grid": {
                                "children": {
                                    "explicitList": [f"plugin-card-{i}" for i in range(len(store_plugins))]
                                },
                                "style": {"gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "gap": "16px"}
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "plugin-store",
                "path": "/",
                "contents": {"plugins": store_plugins}
            }
        }
    ]

def create_skill_store_plugins_ui(plugins: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create A2UI components for skill store plugins list"""
    return [
        {
            "beginRendering": {
                "surfaceId": "skill-store-plugins",
                "root": "plugins-container",
                "styles": {"primaryColor": "#8b5cf6", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "skill-store-plugins",
                "components": [
                    {
                        "id": "plugins-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["header-section", "plugins-list"]
                                }
                            }
                        }
                    },
                    {
                        "id": "header-section",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["header-title", "header-subtitle"]
                                }
                            }
                        }
                    },
                    {
                        "id": "header-title",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Skill Store"},
                                "style": {"fontSize": "24px", "fontWeight": "bold", "color": "#1f2937"}
                            }
                        }
                    },
                    {
                        "id": "header-subtitle",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"{len(plugins)} plugins available"},
                                "style": {"fontSize": "14px", "color": "#6b7280", "marginTop": "4px"}
                            }
                        }
                    },
                    {
                        "id": "plugins-list",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": [f"plugin-item-{i}" for i in range(len(plugins))]
                                }
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "skill-store-plugins",
                "path": "/",
                "contents": {"plugins": plugins}
            }
        }
    ]

def create_plugin_details_ui(plugin_details: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Create A2UI components for plugin details"""
    return [
        {
            "beginRendering": {
                "surfaceId": "plugin-details",
                "root": "details-container",
                "styles": {"primaryColor": "#8b5cf6", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "plugin-details",
                "components": [
                    {
                        "id": "details-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["header-section", "info-section", "capabilities-section", "actions-section"]
                                }
                            }
                        }
                    },
                    {
                        "id": "header-section",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["plugin-icon", "plugin-title-section"]
                                }
                            }
                        }
                    },
                    {
                        "id": "plugin-icon",
                        "component": {
                            "Text": {
                                "text": {"literalString": plugin_details.get("icon", "🔧")},
                                "style": {"fontSize": "32px", "marginRight": "12px"}
                            }
                        }
                    },
                    {
                        "id": "plugin-title-section",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["plugin-name", "plugin-author"]
                                }
                            }
                        }
                    },
                    {
                        "id": "plugin-name",
                        "component": {
                            "Text": {
                                "text": {"literalString": plugin_details["name"]},
                                "style": {"fontSize": "20px", "fontWeight": "bold", "color": "#1f2937"}
                            }
                        }
                    },
                    {
                        "id": "plugin-author",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"by {plugin_details['author']}"},
                                "style": {"fontSize": "14px", "color": "#6b7280"}
                            }
                        }
                    },
                    {
                        "id": "info-section",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["plugin-description", "plugin-version", "plugin-type"]
                                }
                            }
                        }
                    },
                    {
                        "id": "plugin-description",
                        "component": {
                            "Text": {
                                "text": {"literalString": plugin_details["description"]},
                                "style": {"fontSize": "14px", "color": "#374151", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "plugin-version",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Version: {plugin_details['version']}"},
                                "style": {"fontSize": "12px", "color": "#6b7280"}
                            }
                        }
                    },
                    {
                        "id": "plugin-type",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Type: {plugin_details['type']}"},
                                "style": {"fontSize": "12px", "color": "#6b7280"}
                            }
                        }
                    },
                    {
                        "id": "capabilities-section",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["capabilities-header", "capabilities-list"]
                                }
                            }
                        }
                    },
                    {
                        "id": "capabilities-header",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Capabilities"},
                                "style": {"fontSize": "16px", "fontWeight": "600", "color": "#1f2937", "marginTop": "16px", "marginBottom": "8px"}
                            }
                        }
                    },
                    {
                        "id": "actions-section",
                        "component": {
                            "Row": {
                                "children": {
                                    "explicitList": ["enable-button"] if not plugin_details["enabled"] else ["disable-button"]
                                }
                            }
                        }
                    },
                    {
                        "id": "enable-button",
                        "component": {
                            "Button": {
                                "child": "enable-text",
                                "primary": True,
                                "action": {"name": "enable_plugin", "params": {"plugin_id": plugin_details["plugin_id"]}}
                            }
                        }
                    },
                    {
                        "id": "enable-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Enable Plugin"}
                            }
                        }
                    },
                    {
                        "id": "disable-button",
                        "component": {
                            "Button": {
                                "child": "disable-text",
                                "variant": "outline",
                                "action": {"name": "disable_plugin", "params": {"plugin_id": plugin_details["plugin_id"]}}
                            }
                        }
                    },
                    {
                        "id": "disable-text",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Disable Plugin"}
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "plugin-details",
                "path": "/",
                "contents": {"plugin": plugin_details}
            }
        }
    ]

def create_search_results_ui(search_results: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Create A2UI components for search results"""
    return [
        {
            "beginRendering": {
                "surfaceId": "search-results",
                "root": "results-container",
                "styles": {"primaryColor": "#3b82f6", "font": "Inter"}
            }
        },
        {
            "surfaceUpdate": {
                "surfaceId": "search-results",
                "components": [
                    {
                        "id": "results-container",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["search-header", "results-list"]
                                }
                            }
                        }
                    },
                    {
                        "id": "search-header",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": ["search-title", "search-query"]
                                }
                            }
                        }
                    },
                    {
                        "id": "search-title",
                        "component": {
                            "Text": {
                                "text": {"literalString": "Search Results"},
                                "style": {"fontSize": "24px", "fontWeight": "bold", "color": "#1f2937"}
                            }
                        }
                    },
                    {
                        "id": "search-query",
                        "component": {
                            "Text": {
                                "text": {"literalString": f"Found {len(search_results)} results for \"{query}\""},
                                "style": {"fontSize": "14px", "color": "#6b7280", "marginTop": "4px"}
                            }
                        }
                    },
                    {
                        "id": "results-list",
                        "component": {
                            "Column": {
                                "children": {
                                    "explicitList": [f"result-item-{i}" for i in range(len(search_results))]
                                }
                            }
                        }
                    }
                ]
            }
        },
        {
            "dataModelUpdate": {
                "surfaceId": "search-results",
                "path": "/",
                "contents": {"results": search_results, "query": query}
            }
        }
    ]