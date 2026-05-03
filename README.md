# Steganography Tool – Cross‑Platform LSB

Hide any file inside an image using LSB steganography with **encryption**, **compression**, and **password‑based random pixel order**.  
Works on **Kali Linux (GUI)**, **Termux (CLI)**, **iOS iSH (CLI)**, and any desktop.

## Features
- Encrypt secret data with a password (Fernet/AES‑128)
- Compress before hiding (zlib)
- Randomise pixel embedding order (password‑seeded)
- Auto‑detects GUI vs CLI
- Progress bar & log

## Installation
```bash
pip install -r requirements.txt
