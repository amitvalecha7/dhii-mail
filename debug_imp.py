import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(f"Files in CWD: {os.listdir('.')}")

print(f"CWD: {os.getcwd()}")
print(f"sys.path: {sys.path}")

try:
    import auth_api
    print("Successfully imported auth_api")
except Exception:
    traceback.print_exc()
