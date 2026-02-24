#!/usr/bin/env python3
import os, sys, json, requests, hashlib
from Cryptodome.Cipher import AES
from kac_client import KACClient
from hardware_io import feedback, rfid_check
from atecc_attest import sign_challenge

CONF = json.load(open(os.path.join(os.path.dirname(__file__), "config.json")))
BASE = CONF["cloud_base"].rstrip("/")

def _sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _parse_arg_to_filename_and_expected_hash(arg: str):
    arg = os.path.expanduser(arg)
    if arg.endswith(".sha256") and os.path.exists(arg):
        with open(arg, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    exp_hash = parts[0].lower()
                    fn = parts[-1]
                    return (os.path.basename(fn), exp_hash)
        base = os.path.basename(arg[:-8])
        return (base, None)
    else:
        return (os.path.basename(arg), None)

def decrypt_file(argname: str) -> None:
    # 0) Map .sha256 to real file and optional expected hash
    remote_fn, expected_hash = _parse_arg_to_filename_and_expected_hash(argname)

    # 1) RFID 2FA
    ok, name = rfid_check()
    if not ok:
        print(f"Employee: {name} | Access Denied ❌")
        return

    # 2) Attestation (optional; silent if fails)
    headers = {}
    try:
        sig = sign_challenge(b"KAC decrypt auth (demo)")
        if isinstance(sig, (bytes, bytearray, memoryview)):
            headers["X-ATECC-SIG"] = bytes(sig).hex()
    except Exception:
        pass

    # 3) Download
    url = f"{BASE}/download/{remote_fn}"
    try:
        r = requests.get(url, headers=headers, timeout=10)
    except Exception as e:
        feedback(False, ["Cloud error", "Request failed"])
        print("Download failed:", e)
        return
    if r.status_code != 200:
        feedback(False, ["Cloud error", str(r.status_code)])
        print("Download failed:", r.status_code)
        return
    try:
        hdr = json.loads(r.headers["X-KAC-HEADER"])
    except Exception as e:
        feedback(False, ["Header invalid"])
        print("Bad header:", e)
        return

    # 4) Class auth
    cls = hdr.get("class", "")
    kac = KACClient()
    if not kac.authorized(cls):
        feedback(False, [f"Denied {cls}", "Not in key classes"])
        print(f"Employee: {name} | Access Denied ❌")
        return

    # 5) Decrypt
    try:
        key = kac.unwrap(hdr["wrap"])
        cipher = AES.new(key, AES.MODE_GCM, nonce=bytes.fromhex(hdr["nonce"]))
        pt = cipher.decrypt_and_verify(r.content, bytes.fromhex(hdr["tag"]))
    except Exception as e:
        feedback(False, ["Decrypt error"])
        print("Decrypt error:", e)
        return

    # 6) Hash verify
    pt_hash = _sha256_hex(pt)
    hdr_hash = (hdr.get("pt_sha256") or "").lower()
    if hdr_hash and pt_hash != hdr_hash:
        feedback(False, ["Hash mismatch", "header"])
        print("Hash mismatch vs header pt_sha256"); return
    if expected_hash and pt_hash != expected_hash.lower():
        feedback(False, ["Hash mismatch", ".sha256"])
        print("Hash mismatch vs .sha256 file"); return

    # 7) Write plaintext
    out = "dec_" + os.path.basename(remote_fn)
    try:
        with open(out, "wb") as f:
            f.write(pt)
    except Exception as e:
        feedback(False, ["Write error"])
        print("Write error:", e)
        return

    # 8) Success + optional OLED text viewer
    feedback(True, [f"Welcome {name}", f"Class {cls}", "Access Granted ✅"])
    print(f"Employee: {name} | Access Granted ✅")
    print(f"[OK] Wrote {out}")

    # Show text on OLED pager if UTF-8
    try:
        txt = pt.decode("utf-8")
        from text_oled_viewer import view_text_on_oled
        export_dir = os.path.join(os.path.dirname(__file__), "oled_exports")
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, os.path.basename(out))
        view_text_on_oled(txt, title=os.path.basename(remote_fn), export_path=export_path)
    except UnicodeDecodeError:
        pass

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 decrypt.py <file or file.sha256>")
        sys.exit(1)
    decrypt_file(sys.argv[1])
