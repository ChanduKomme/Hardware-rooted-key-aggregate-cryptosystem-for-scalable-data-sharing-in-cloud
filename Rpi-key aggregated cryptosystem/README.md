# Raspberry Pi KAC Hardware Client (RFID + OLED + ATECC + BME280)

## Hardware (Pi 4B)
- RC522 RFID (SPI)
- SSD1306 OLED 128x64 (I²C, addr 0x3C)
- ATECC608A (I²C, addr 0x60)
- Optional BME280 (I²C, addr 0x76/0x77)
- 2 LEDs: GREEN=GPIO17, RED=GPIO27 (with 330Ω to GND)

## Enable I²C & SPI
Edit `/boot/firmware/config.txt` and add:
```
dtparam=i2c_arm=on
dtparam=spi=on
```
Then:
```
sudo adduser $USER i2c
sudo adduser $USER spi
sudo adduser $USER gpio
sudo apt update && sudo apt install -y i2c-tools fonts-dejavu-core python3-venv git
sudo reboot
```

Confirm devices:
```
sudo i2cdetect -y 1   # expect 0x60 (ATECC), 0x3c (OLED), 0x76/0x77 (BME280)
```

## Setup
Unzip this folder on the Pi, e.g. `/home/pi/rpi-kac`.

### Cloud server
```
cd rpi-kac/cloud
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 server.py
```
Server runs on port 5000.

### Manager
```
cd rpi-kac/manager
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 setup.py
python3 keygen.py pi-client finance iot
# provision to member
sudo cp keys/pi-client_agg.json /etc/kac_agg.json
sudo chmod 600 /etc/kac_agg.json
```

### Member
```
cd rpi-kac/member
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

Enroll an RFID tag (tap when prompted):
```
sudo ./enroll_rfid.py --name "Chandu" --force
```

### Encrypt (on member/producer)
```
source env/bin/activate
python3 encrypt.py /path/to/file.ext finance
```
Creates `enc_report_<file>.json` and `<file>.sha256` and uploads the ciphertext.

### Decrypt (on member/consumer)
```
source env/bin/activate
python3 decrypt.py file.ext
# or using the hash file:
python3 decrypt.py file.ext.sha256
```
- RFID presence required
- Attestation attempted (silent if driver differs)
- If plaintext is UTF‑8, an OLED pager opens (j/k/pgup/pgdn/home/end, s=save, q=quit)
- Plaintext saved as `dec_<file.ext>`

## Notes
- If decrypt ever says MAC check failed, re-encrypt with the same `/etc/kac_agg.json` present on the consumer.
- BME280 readings appear on the “Tap the card” screen if connected.
- To pick up new enrollments without restart, the app hot‑reloads `authorized_tags.json` each tap.
