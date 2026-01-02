import os
os.environ.clear()
os.environ['ENVIRONMENT'] = 'production'

from config import Settings
s = Settings()

print("=== Debug Production CORS Config ===")
print(f"Environment: {s.environment}")
print(f"Is production: {s.is_production}")
print(f"CORS_ALLOW_CREDENTIALS env var: {os.getenv('CORS_ALLOW_CREDENTIALS')}")
print(f"Settings cors_allow_credentials: {s.cors_allow_credentials}")
print(f"get_cors_config result: {s.get_cors_config()}")

# Let's trace through the get_cors_config logic
print("\n=== Tracing get_cors_config logic ===")
print(f"s.is_production: {s.is_production}")
print(f"os.getenv('CORS_ALLOW_CREDENTIALS'): {os.getenv('CORS_ALLOW_CREDENTIALS')}")
print(f"os.getenv('CORS_ALLOW_CREDENTIALS') is None: {os.getenv('CORS_ALLOW_CREDENTIALS') is None}")

config = {
    "allow_origins": s.cors_origins_list,
    "allow_credentials": s.cors_allow_credentials,
    "allow_methods": s.cors_methods_list,
    "allow_headers": s.cors_allow_headers.split(",") if s.cors_allow_headers != "*" else ["*"]
}

print(f"Initial config: {config}")

if s.is_production:
    cors_cred_env = os.getenv("CORS_ALLOW_CREDENTIALS")
    print(f"cors_cred_env: {cors_cred_env}")
    print(f"cors_cred_env is None: {cors_cred_env is None}")
    
    if cors_cred_env is None:
        config["allow_credentials"] = False
        print("Setting allow_credentials to False")

print(f"Final config: {config}")