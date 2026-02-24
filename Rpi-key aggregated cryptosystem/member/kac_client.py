from Cryptodome.Random import get_random_bytes
import json, os

class KACClient:
    def __init__(self, agg_file="/etc/kac_agg.json"):
        self.path = agg_file
        self.key = None
        self.classes = []
        try:
            d = json.load(open(self.path))
            self.key = bytes.fromhex(d["key"])
            self.classes = d["classes"]
        except Exception as e:
            raise RuntimeError(f"Cannot load aggregate key {agg_file}: {e}")

    def authorized(self, cls): 
        return cls in self.classes

    def wrap(self, aes_key: bytes) -> str:
        return bytes(a ^ b for a, b in zip(aes_key, self.key[:len(aes_key)])).hex()

    def unwrap(self, wrap_hex: str) -> bytes:
        w = bytes.fromhex(wrap_hex)
        return bytes(a ^ b for a, b in zip(w, self.key[:len(w)]))
