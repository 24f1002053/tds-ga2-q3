import os
import yaml
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def str_to_bool(val):
    return str(val).lower() in ("true", "1", "yes", "on")

@app.get("/healthz")
async def health_check():
    return {"status": "ok", "redis": "up"}

@app.get("/effective-config")
async def get_effective_config(set: list[str] = []):
    # 1. Defaults
    config = {"port": 8000, "workers": 1, "debug": False, "log_level": "info", "api_key": "default-secret-000"}
    
    # 2. YAML (config.development.yaml)
    if os.path.exists("config.development.yaml"):
        with open("config.development.yaml") as f:
            yaml_config = yaml.safe_load(f) or {}
            config.update(yaml_config)
            
    # 3. .env (and Alias NUM_WORKERS -> workers)
    config["workers"] = int(os.getenv("NUM_WORKERS", config["workers"]))
    if os.getenv("APP_PORT"): config["port"] = int(os.getenv("APP_PORT"))
    if os.getenv("APP_LOG_LEVEL"): config["log_level"] = os.getenv("APP_LOG_LEVEL")
    
    # 4. OS Env (APP_ prefix)
    if os.getenv("APP_PORT"): config["port"] = int(os.getenv("APP_PORT"))
    if os.getenv("APP_WORKERS"): config["workers"] = int(os.getenv("APP_WORKERS"))
    if os.getenv("APP_API_KEY"): config["api_key"] = os.getenv("APP_API_KEY")
    
    # 5. CLI Overrides (?set=key=value)
    for s in set:
        k, v = s.split("=")
        if k in ["port", "workers"]: config[k] = int(v)
        elif k == "debug": config[k] = str_to_bool(v)
        else: config[k] = v
            
    # Masking
    config["api_key"] = "****"
    return config
