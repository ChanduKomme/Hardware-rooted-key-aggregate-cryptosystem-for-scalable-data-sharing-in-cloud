#!/usr/bin/env python3
import os, sys, json, requests, hashlib, datetime
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from kac_client import KACClient
from hardware_io import feedback
from sensors import read_bme280

def _sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

CONF = json.load(open(os.path.join(os.path.dirname(__file__), "config.json")))
BASE = CONF["cloud_base"].rstrip("/")

def encrypt_file(path, cls):
    kac = KACClient()
    data = open(path, "rb").read()

    # --- AES-GCM encrypt ---
    key = get_random_bytes(32)
    cipher = AES.new(key, AES.MODE_GCM)
    ct, tag = cipher.encrypt_and_digest(data)

    # --- optional env snapshot from BME280 ---
    env = read_bme280()
    if env is not None:
        env_meta = {
            "temp_c": round(env[0], 2),
            "humidity_pct": round(env[1], 1),
            "pressure_hpa": round(env[2], 1)
        }
    else:
        env_meta = None

    # --- header for cloud (no plaintext) ---
    header = {
        "class": cls,
        "nonce": cipher.nonce.hex(),
        "tag": tag.hex(),
        "wrap": kac.wrap(key),
        "pt_sha256": _sha256_hex(data),
        "ct_sha256": _sha256_hex(ct),
        "env": env_meta,
    }

    # --- upload to cloud ---
    filename = os.path.basename(path)
    requests.post(f"{BASE}/upload",
                  files={"file": ct},
                  data={"header": json.dumps(header),
                        "filename": filename})

    # --- write local hash reports (no plaintext) ---
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    report = {
        "timestamp": ts,
        "file": filename,
        "size_bytes": len(data),
        "class": cls,
        "plaintext_sha256": header["pt_sha256"],
        "ciphertext_sha256": header["ct_sha256"],
        "nonce_hex": header["nonce"],
        "tag_hex": header["tag"],
        "wrapped_key_hex": header["wrap"],
        "cloud_base": BASE,
        "env": env_meta,
    }
    rep_name = f"enc_report_{filename}.json"
    with open(rep_name, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(f"{filename}.sha256", "w", encoding="utf-8") as f:
        f.write(f"{header['pt_sha256']}  {filename}\n")

    feedback(True, [f"Encrypted {cls}", filename])
    print(f"[OK] Uploaded {path} (class {cls})")
    print(f"[OK] Wrote {rep_name}")
    print(f"[OK] Wrote {filename}.sha256 (plaintext hash)")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 encrypt.py <file> <class>")
        sys.exit(1)
    encrypt_file(sys.argv[1], sys.argv[2])
