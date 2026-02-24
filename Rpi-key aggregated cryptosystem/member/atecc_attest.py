# member/atecc_attest.py
import hashlib, board, busio
try:
    from adafruit_atecc.adafruit_atecc import ATECC
except ImportError:
    from adafruit_atecc import ATECC

_i2c = None
_chip = None
def _get_chip():
    global _i2c, _chip
    if _chip is None:
        _i2c = busio.I2C(board.SCL, board.SDA)
        _chip = ATECC(_i2c, address=0x60)
    return _chip

def device_serial_hex() -> str:
    chip = _get_chip()
    ser = chip.serial_number
    if isinstance(ser, (bytes, bytearray, memoryview)):
        return bytes(ser).hex()
    if isinstance(ser, str):
        try:
            bytes.fromhex(ser); return ser.lower()
        except ValueError:
            return ser.encode().hex()
    return bytes(ser).hex()

def _der_to_raw(sig: bytes) -> bytes:
    if len(sig) == 64:
        return sig
    if not sig or sig[0] != 0x30:
        return sig
    i = 2
    if sig[1] & 0x80:
        i = 2 + (sig[1] & 0x7F)
    if sig[i] != 0x02: return sig
    i += 1; lr = sig[i]; i += 1; r = sig[i:i+lr]; i += lr
    if sig[i] != 0x02: return sig
    i += 1; ls = sig[i]; i += 1; s = sig[i:i+ls]
    r = r.lstrip(b"\x00")[-32:].rjust(32, b"\x00")
    s = s.lstrip(b"\x00")[-32:].rjust(32, b"\x00")
    return r + s

def sign_challenge(challenge: bytes) -> bytes:
    chip = _get_chip()
    digest = hashlib.sha256(challenge).digest()
    sig = chip.sign(digest)  # one-arg API
    if isinstance(sig, str):
        try:
            sig = bytes.fromhex(sig)
        except ValueError:
            sig = sig.encode()
    elif not isinstance(sig, (bytes, bytearray, memoryview)):
        sig = bytes(sig)
    sig = bytes(sig)
    return _der_to_raw(sig)
