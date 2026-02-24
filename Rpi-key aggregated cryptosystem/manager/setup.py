#!/usr/bin/env python3
import os, json
from Cryptodome.Random import get_random_bytes

os.makedirs("keys", exist_ok=True)

def setup():
    params = {
        "system_id": os.urandom(4).hex(),
        "master_secret": get_random_bytes(32).hex(),
        "public_params": {
            "algo": "AES-GCM",
            "classes_supported": ["finance", "iot", "hr", "security"]
        }
    }
    with open("keys/system_params.json", "w") as f:
        json.dump(params, f, indent=2)
    print("✅ KAC system setup complete.")
    print(" System ID:", params["system_id"])

if __name__ == "__main__":
    setup()
