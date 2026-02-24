# sensors.py
import board, busio
try:
    import adafruit_bme280
except Exception:
    adafruit_bme280 = None

_bme = None

def _get_bme():
    global _bme
    if _bme is not None:
        return _bme
    if adafruit_bme280 is None:
        return None
    i2c = busio.I2C(board.SCL, board.SDA)
    try:
        _bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)
    except Exception:
        try:
            _bme = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)
        except Exception:
            _bme = None
    return _bme

def read_bme280():
    bme = _get_bme()
    if not bme:
        return None
    try:
        t = float(bme.temperature)
        h = float(bme.relative_humidity)
        p = float(bme.pressure)
        return (t, h, p)
    except Exception:
        return None

def lines_for_oled():
    v = read_bme280()
    if not v:
        return []
    t, h, p = v
    return [f"T {t:.1f}°C  H {h:.0f}%", f"P {p:.0f} hPa"]
