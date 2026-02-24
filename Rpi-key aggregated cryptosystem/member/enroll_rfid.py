#!/usr/bin/env python3
import os, json, argparse, sys, time
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

# Optional OLED + LEDs
OLED_OK = False
try:
    from hardware_io import show, LED_GREEN, LED_RED
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_GREEN, GPIO.OUT)
    GPIO.setup(LED_RED, GPIO.OUT)
    OLED_OK = True
except Exception:
    pass

AUTH_FILE = os.path.join(os.path.dirname(__file__), "authorized_tags.json")

def _load():
    if os.path.exists(AUTH_FILE):
        try:
            d = json.load(open(AUTH_FILE))
            return {int(k): v for k, v in d.items()}
        except Exception:
            pass
    return {}

def _save(d):
    os.makedirs(os.path.dirname(AUTH_FILE), exist_ok=True)
    json.dump({str(k): v for k, v in d.items()}, open(AUTH_FILE, "w"), indent=2)

def _blink(ok=True, sec=0.8):
    if not OLED_OK:
        time.sleep(sec); return
    GPIO.output(LED_GREEN, 1 if ok else 0)
    GPIO.output(LED_RED,   0 if ok else 1)
    time.sleep(sec)
    GPIO.output(LED_GREEN, 0)
    GPIO.output(LED_RED,   0)

def enroll(name=None, force=False, write_back=False):
    db = _load()
    rdr = SimpleMFRC522()
    try:
        if OLED_OK: show(["RFID Enroll", "Tap card...", "(Ctrl+C=quit)"])
        print("Tap card to ENROLL (Ctrl+C to exit)...")
        uid, text = rdr.read()
        uid = int(uid)
        print(f"Read UID: {uid}")
        if OLED_OK: show(["Card read", f"UID: {uid}"])

        if name is None:
            name = input("Enter name for this tag: ").strip() or "User"

        if uid in db and not force:
            print(f"UID {uid} already exists for '{db[uid]}'. Use --force to overwrite.")
            if OLED_OK: show(["Already enrolled", f"UID: {uid}"])
            _blink(ok=False)
            return 1

        db[uid] = name
        _save(db)
        print(f"✅ Enrolled UID {uid} -> {name}")
        if OLED_OK: show(["Enroll OK", f"{name}", f"UID:{uid}"])
        _blink(ok=True)

        if write_back:
            try:
                rdr.write(name)
                print("(Wrote name onto tag data area)")
            except Exception:
                print("(Could not write name to tag data; continuing)")

        return 0
    finally:
        try: GPIO.cleanup()
        except Exception: pass

def remove(uid: int):
    db = _load()
    if uid not in db:
        print(f"UID {uid} not found.")
        return 1
    who = db.pop(uid)
    _save(db)
    print(f"🗑️ Removed UID {uid} ({who})")
    return 0

def list_all():
    db = _load()
    if not db:
        print("(no tags enrolled yet)")
        return 0
    print("Authorized tags:")
    for u, n in sorted(db.items()):
        print(f"  {u}  ->  {n}")
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="RFID auto-enroll tool")
    sub = ap.add_subparsers(dest="cmd")

    ap.add_argument("--name", "-n", help="Name to bind to this tag (else prompt)")
    ap.add_argument("--force", "-f", action="store_true", help="Overwrite if UID exists")
    ap.add_argument("--write-back", action="store_true", help="Also write name onto tag's data")

    p_rm = sub.add_parser("remove", help="Remove a UID")
    p_rm.add_argument("uid", type=int)

    sub.add_parser("list", help="List enrolled tags")

    args = ap.parse_args()

    if args.cmd == "list":
        sys.exit(list_all())
    elif args.cmd == "remove":
        sys.exit(remove(args.uid))
    else:
        sys.exit(enroll(name=args.name, force=args.force, write_back=args.write_back))
