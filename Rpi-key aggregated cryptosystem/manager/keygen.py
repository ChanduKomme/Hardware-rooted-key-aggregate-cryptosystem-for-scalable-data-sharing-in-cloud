#!/usr/bin/env python3
import json, os, sys
from hashlib import sha256

if not os.path.exists("keys/system_params.json"):
    sys.exit("Run setup.py first.")

params = json.load(open("keys/system_params.json"))

def issue(device_name: str, classes):
    master = bytes.fromhex(params["master_secret"])
    digest = sha256(master + ",".join(sorted(classes)).encode()).digest()
    out = {"device": device_name, "classes": classes, "key": digest.hex(), "system_id": params["system_id"]}
    fn = f"keys/{device_name}_agg.json"
    json.dump(out, open(fn, "w"), indent=2)
    print(f"✅ Issued aggregate key for {device_name} -> {fn}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 keygen.py <device_name> <class1> [class2] ..."); sys.exit(1)
    issue(sys.argv[1], sys.argv[2:])
