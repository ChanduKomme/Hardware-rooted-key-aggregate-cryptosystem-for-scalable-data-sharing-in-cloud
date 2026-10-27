# Hardware-Rooted KAC for Scalable Data Sharing in Cloud 

![Platform](https://img.shields.io/badge/Platform-KAC-blue)
[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Prototype-red.svg)](https://www.raspberrypi.com/)


*A secure, device-bound data-sharing system for IoT environments using Raspberry Pi and Key-Aggregate Cryptosystem (KAC).*
##  Project Overview
This project implements a hardware-rooted, device-bound data-sharing system designed for scalable cloud collaboration. It solves the problem of secure data sharing by ensuring that decryption occurs only at the "edge" (the device), requires physical user presence, and strictly controls which data classes a device can access.

The prototype demonstrates class-scoped key provisioning alongside AES-GCM file encryption. The manager derives a 32-byte key from a master secret and an authorized class list, and the member uses that key to wrap per-file AES keys. This is a **demonstration of an aggregate-key workflow, not a formal cryptographic KAC construction**. The cloud stores encrypted file bytes and metadata, not plaintext file contents.

##  Key Features

* **Class-Scoped Key Provisioning:** A manager issues one 32-byte derived key and a class allowlist (for example, `finance` and `iot`) to a member. This prototype does not implement cryptographic KAC aggregation or automatic revocation. 
* **Edge-First Processing:** Encryption and decryption run on the Raspberry Pi. The manager provisions the member key, and the cloud receives ciphertext plus headers containing class, hashes, nonce, tag, and wrapped key. 
* **RFID-Gated Application Flow:** The member's decryption script checks an MFRC522 RFID tag before downloading and decrypting a file. This is an application check, not hardware-enforced key release. 
* **Authenticated File Encryption:** AES-GCM verifies the ciphertext against its nonce and tag. Other header fields (such as the class label) are not authenticated as additional associated data in the current code.
* **Visual Feedback:** An SSD1306 OLED display provides explicit state feedback (Ready, Tap, Granted, Denied).
* **Ciphertext Storage Demo:** A lightweight Flask application stores encrypted bytes and headers; the headers also reveal file metadata and plaintext/ciphertext hashes.

## Getting Started

The runnable Python prototype and its detailed Raspberry Pi setup guide live in [`Rpi-key aggregated cryptosystem/`](Rpi-key%20aggregated%20cryptosystem/README.md). The guide covers enabling I²C/SPI, installing each component's requirements, enrolling an RFID tag, and running the encryption/decryption scripts.

| Component | Source | Role |
| --- | --- | --- |
| Manager | [`manager/setup.py` and `manager/keygen.py`](Rpi-key%20aggregated%20cryptosystem/manager/) | Create system parameters and provision a member key |
| Cloud | [`cloud/server.py`](Rpi-key%20aggregated%20cryptosystem/cloud/server.py) | Run a Flask storage service on port 5000 |
| Member | [`member/encrypt.py` and `member/decrypt.py`](Rpi-key%20aggregated%20cryptosystem/member/) | Encrypt, upload, RFID-check, download, and decrypt on Raspberry Pi |

**Before running:** the member reads its key from `/etc/kac_agg.json` and the server address from [`member/config.json`](Rpi-key%20aggregated%20cryptosystem/member/config.json), which defaults to `http://127.0.0.1:5000`. If the server runs on a different machine, update that address to a reachable endpoint. This demo requires compatible Raspberry Pi peripherals; it is not a hardware-free quick start.

# System Architecture

The system consists of three main roles:

1.  **Manager:** Generates system parameters and issues a derived member key with an allowed list of classes.
2.  **Cloud:** A lightweight Flask server that stores ciphertext and headers .
3.  **Member (Raspberry Pi):** Encrypts files, uploads ciphertext and metadata, and decrypts after RFID and class-allowlist checks.

**Encryption**
![Encryption_page-0001](https://github.com/user-attachments/assets/cb2c8da5-2ac9-4eb1-94da-b6a0f5be8077)

**Decryption**
![Decryption_page-0001](https://github.com/user-attachments/assets/db780d65-dfc7-44dd-94ca-b2e3412b96b8)

**Prototype**
![connections](https://github.com/user-attachments/assets/8ec95743-617c-47e0-ad3e-40b1353979fe)

[Raspberry Pi output before RFID tapping](pi-outputs/Berfore-tapping.jpg)

[Raspberry Pi output after RFID tapping](pi-outputs/After-tapping.jpg)

# Results

**Cloud server**
---
<img width="1056" height="583" alt="cloud_server" src="https://github.com/user-attachments/assets/6c6d875f-84f5-4d7f-b3c9-adcb07471ca6" />


**Encryption**
---
<img width="1101" height="649" alt="encrypt" src="https://github.com/user-attachments/assets/c524252a-ea81-4bb8-adb6-1914e55f4ab2" />




**Decryption**
---
<img width="1098" height="211" alt="dcrypt" src="https://github.com/user-attachments/assets/8fca2c20-cf02-4d22-a121-f160274e13e8" />



## Security Model and Prototype Limitations

This is a research/demo implementation, **not a production-ready access-control or key-management system**:

* **Key wrapping:** `member/kac_client.py` XORs a per-file AES key with the derived member key. This is not a standard KAC scheme or a recommended production key-wrap construction. Replacing the provisioned key does **not** automatically rewrap existing encrypted files or revoke previously copied keys.
* **Authenticated encryption:** AES-GCM checks the encrypted file contents and tag, but the class label and other header metadata are not bound to the tag as authenticated associated data.
* **Cloud exposure:** The Flask service stores ciphertext and metadata, including plaintext SHA-256 hashes. Its `/upload` and `/download/<fn>` endpoints do not authenticate callers, and the sample member configuration uses plain HTTP (`127.0.0.1:5000`). Run only in a trusted local test environment.
* **Hardware trust:** The member checks RFID tags in application code. An ATECC608A signing attempt is optional in `member/decrypt.py`, but `cloud/server.py` does not verify the signature; the member key is loaded from `/etc/kac_agg.json`, not released by the secure element.

For a production system, use an established authenticated key-wrap/KEM design, authenticated transport and cloud endpoints, server-verified attestation if required, and a tested key-revocation/re-encryption plan.


## Future Work

* **Post-Quantum Migration:** Hybridizing headers to support post-quantum KEMs and signatures, allowing the system to retain existing roles and workflows .
* **Attestation:** Implementing server-verified default attestation and "policy-as-code" for boot security, including measured boot and anti-rollback mechanisms .
* **Header Optimization:** Reducing header size and compression complexity for environments where mandatory TLS is already provided .



