import sys
import traceback

def try_import(name):
    print(f"--- Importing {name} ---")
    try:
        if name == "ai_engine":
            from a2ui_integration.a2ui_orchestrator import A2UIOrchestrator
        elif name == "marketing_manager":
            from marketing_manager import marketing_manager
        print(f"✅ {name}: Success")
    except Exception as e:
        print(f"❌ {name}: Failed")
        traceback.print_exc()

if __name__ == "__main__":
    try_import("ai_engine")
    try_import("marketing_manager")
