# 🔒 Cross‑Platform LSB Steganography Tool

**Hide any file inside an image** using **Least Significant Bit (LSB)** steganography, with **encryption**, **compression**, and **password‑based random pixel order**.

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
| **File type agnostic** | Hide any file: text, image, PDF, ZIP, audio, etc. |

---

## 📦 Full Installation Guide (by platform)

### 1. Kali Linux / Debian / Ubuntu (Desktop)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3, pip, and Tkinter (for GUI)
sudo apt install python3 python3-pip python3-tk -y

# Install required Python libraries
pip3 install pillow numpy cryptography

# Verify installation
python3 -c "import PIL, numpy, cryptography; print('OK')"

# Run the tool
python3 stego_crossplatform.py


