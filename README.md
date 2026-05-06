# 🔒 Cross-Platform LSB Steganography Tool

Educational cybersecurity project demonstrating how hidden data can
exist inside digital images using Least Significant Bit (LSB)
steganography techniques.

![Python](https://img.shields.io/badge/Python-3.8+-brightgreen?style=flat-square)
![License](https://img.shields.io/github/license/mahi-cyberaware/STEGANOGRAPHY-TOOL?style=flat-square)
![Stars](https://img.shields.io/github/stars/mahi-cyberaware/STEGANOGRAPHY-TOOL?style=flat-square)
![Forks](https://img.shields.io/github/forks/mahi-cyberaware/STEGANOGRAPHY-TOOL?style=flat-square)

![Platform](https://img.shields.io/badge/Platform-Kali%20Linux%20%7C%20Termux%20%7C%20Windows%20%7C%20macOS-blue?style=flat-square)
![Purpose](https://img.shields.io/badge/Purpose-Educational-orange?style=flat-square)
![Security](https://img.shields.io/badge/Security-Research-red?style=flat-square)


**Hide any file inside an image** using **Least Significant Bit (LSB)** steganography, with **encryption**, **compression**, and **password‑based random pixel order**.

# Cross-Platform LSB Steganography Tool

> ⚠️ Educational Use Only
>
> This project is intended strictly for cybersecurity education,
> digital forensics awareness, and authorized research environments.
>
> Do not use this software for illegal activities or unauthorized access.

Designed for:
- students
- cybersecurity learners
- digital forensics awareness
- ethical security research
> ✅ Works on **Kali Linux** (full GUI), **Termux** (Android CLI), **iOS iSH** (CLI), **Windows**, **macOS**, and any Linux desktop.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **LSB embedding** | Changes only the last bit of each RGB channel – invisible to the human eye |
| **Password protection** | Encrypts your secret data using **Fernet (AES‑128)** before hiding |
| **Compression** | Uses **zlib** to shrink data, increasing capacity |
| **Random pixel order** | Shuffles embedding order using your password as seed – defeats statistical detection |
| **Cross‑platform UI** | Auto‑detects display: launches **Tkinter GUI** on desktops, **text menu** on Termux/iSH |
| **Progress indicator** | Shows encoding/decoding progress (CLI progress bar or GUI meter) |
| **Multiple input formats** | Accepts PNG, BMP, TIFF, JPEG (always saves as **PNG** – lossless) |
| **File type agnostic** | Hide any file: text, image, PDF, ZIP, audio, 

## 📦 Quick Installation (One-Command)

### Recommended: use the auto-install script

```bash
git clone https://github.com/mahi-cyberaware/STEGANOGRAPHY-TOOL.git
cd STEGANOGRAPHY-TOOL
chmod +x install.sh
./install.sh
```

### ▶ Run the tool

```bash
python3 stego_crossplatform.py
```

---

## 📦 Manual Installation (by platform)

If the auto-script fails, follow these platform-specific steps:

### 1. Kali Linux / Debian / Ubuntu (Desktop)

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-tk
pip3 install pillow numpy cryptography
```

---

### 2. Termux (Android)

```bash
pkg update && pkg install -y python clang libjpeg-turbo
pip install pillow numpy cryptography
```

---

### 3. iOS (iSH Shell)

```bash
apk update && apk add python3 py3-pip gcc musl-dev python3-dev libffi-dev openssl-dev
pip3 install pillow numpy cryptography
```

---

### 4. Windows (native)

Download Python from https://www.python.org  
(check **"Add to PATH"**), then:

```powershell
pip install pillow numpy cryptography
```

---

### 5. macOS

```bash
brew install python python-tk
pip3 install pillow numpy cryptography
```

---

## 🚀 Usage (same on all platforms)

```bash
python3 stego_crossplatform.py
```
