# Hardware-Rooted KAC for Scalable Data Sharing in Cloud 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Platform](https://img.shields.io/badge/Platform-KAC-blue)
[![Raseberry Pi](https://img.shields.io/badge/RaseberryPi-Wiki-red.svg)](https://www.raspberrypi.org/)


*A secure, device-bound data-sharing system for IoT environments using Raspberry Pi and Key-Aggregate Cryptosystem (KAC).*
##  Project Overview
This project implements a hardware-rooted, device-bound data-sharing system designed for scalable cloud collaboration. It solves the problem of secure data sharing by ensuring that decryption occurs only at the "edge" (the device), requires physical user presence, and strictly controls which data classes a device can access.

The core of the design is a Key-Aggregate Cryptosystem (KAC). This allows decryption rights for multiple data classes to be condensed into a single, constant-size aggregate key. Combined with AES-GCM encryption, the system eliminates the need to distribute keys for every single file and keeps the cloud provider completely "blind" to the plaintext data.

##  Key Features

* **Key-Aggregate Cryptosystem (KAC):** Compresses decryption privileges for a group of classes (e.g., "finance", "IoT") into one fixed-size key, allowing instant policy changes via a single key rotation. 
* **Edge-First Security:** Plaintext and long-term keys never leave the Raspberry Pi. The cloud only stores ciphertext and minimal headers. 
* **Presence-Gated Decryption:** Decryption is physically gated. An MFRC522 RFID tap is required before any decryption operation can proceed. 
* **Tamper-Evident Headers:** Each file has a small header containing the KAC wrap, nonce, and authentication tag. Any corruption or tampering causes immediate tag failure, preventing access.
* **Visual Feedback:** An SSD1306 OLED display provides explicit state feedback (Ready, Tap, Granted, Denied).
* **Blind Cloud Storage:** The cloud role is played by a lightweight Flask application that stores bytes but never processes plaintext.

# System Architecture

The system consists of three main roles:

1.  **Manager:** Handles Setup and KeyGen; issues the aggregate key to the device for a specific subset of classes.
2.  **Cloud:** A lightweight Flask server that stores ciphertext and headers .
3.  **Member (Raspberry Pi):** Handles encryption (creation of ciphertext + KAC header) and decryption (RFID-gated unwrap).

**Encryption**
![Encryption_page-0001](https://github.com/user-attachments/assets/cb2c8da5-2ac9-4eb1-94da-b6a0f5be8077)

**Decryption**
![Decryption_page-0001](https://github.com/user-attachments/assets/db780d65-dfc7-44dd-94ca-b2e3412b96b8)

**Prototype**
![connections](https://github.com/user-attachments/assets/8ec95743-617c-47e0-ad3e-40b1353979fe)



# Results

**Cloud server**
---
<img width="1056" height="583" alt="cloud_server" src="https://github.com/user-attachments/assets/6c6d875f-84f5-4d7f-b3c9-adcb07471ca6" />


**Encryption**
---
<img width="1101" height="649" alt="encrypt" src="https://github.com/user-attachments/assets/c524252a-ea81-4bb8-adb6-1914e55f4ab2" />


**Deryption**
---
<img width="1098" height="211" alt="dcrypt" src="https://github.com/user-attachments/assets/8fca2c20-cf02-4d22-a121-f160274e13e8" />

## Security Model

The system architecture prioritizes a "blind" cloud and tamper-evident delivery:

* **No Re-Encryption Needed:** Policy agility is achieved by rotating a single aggregate key.Administrators can switch policies or revoke access without the need to re-encrypt stored data.
* **Integrity:** The system uses AES-GCM for authenticated encryption.Any modification to the header or ciphertext results in a tag failure, ensuring no corrupted plaintext is ever released or displayed.
* **Privacy:** The cloud provider sees only opaque ciphertext and minimal JSON headers.It has no access to keys or plaintext bytes, reducing the impact of a potential cloud breach.


## Future Work

* **Post-Quantum Migration:** Hybridizing headers to support post-quantum KEMs and signatures, allowing the system to retain existing roles and workflows .
* **Attestation:** Implementing server-verified default attestation and "policy-as-code" for boot security, including measured boot and anti-rollback mechanisms .
* **Header Optimization:** Reducing header size and compression complexity for environments where mandatory TLS is already provided .



