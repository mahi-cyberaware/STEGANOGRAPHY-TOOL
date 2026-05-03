#!/usr/bin/env python3
"""
Crossb
Supports: Kali Linux (full GUI), Termux (Android CLI), iOS iSH (CLI)
Features: encryption, compression, random pixel order (passwordb
"""

import os
import sys
import struct
import zlib
import random
import hashlib
import base64
from cryptography.fernet import Fernet
from PIL import Image
import numpy as np

# ---------- Platform detection ----------
def has_display():
    return os.environ.get('DISPLAY') is not None and sys.platform not in ('android', 'darwin')

def is_termux():
    return 'com.termux' in os.environ.get('PREFIX', '') or sys.platform == 'android'

def is_ios_ish():
    return hasattr(os, 'uname') and 'iSH' in os.uname().release

# ---------- Core LSB functions ----------
def derive_key(password):
    salt = b"stegocross2026"
    kdf = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000, dklen=32)
    return base64.urlsafe_b64encode(kdf)

def get_pixel_coords(width, height, password=None, random_order=False):
    coords = [(x, y) for y in range(height) for x in range(width)]
    if random_order and password:
        seed = int(hashlib.sha256(password.encode()).hexdigest(), 16) % (2**32)
        random.seed(seed)
        random.shuffle(coords)
    return coords

def encode_data(image_path, secret_data, password, compress, random_order, progress_callback=None):
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    pixels = np.array(img, dtype=np.uint8)

    if compress:
        comp = zlib.compress(secret_data, 9)
        if len(comp) < len(secret_data):
            secret_data = comp
    if password:
        key = derive_key(password)
        f = Fernet(key)
        secret_data = f.encrypt(secret_data)

    original_size = len(secret_data)
    payload = struct.pack(">I", original_size) + secret_data

    bits = []
    for byte in payload:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)

    coords = get_pixel_coords(width, height, password if random_order else None, random_order)
    total_bits = len(bits)
    if total_bits > width * height * 3:
        raise ValueError(f"Payload too big: {total_bits} bits, max {width*height*3} bits.")

    bit_idx = 0
    for idx, (x, y) in enumerate(coords):
        if bit_idx >= total_bits:
            break
        for c in range(3):
            if bit_idx < total_bits:
                pixels[y, x, c] = (pixels[y, x, c] & 0xFE) | bits[bit_idx]
                bit_idx += 1
        if progress_callback:
            progress_callback(idx, len(coords))
    return Image.fromarray(pixels, mode="RGB")

def decode_data(image_path, password, random_order, progress_callback=None):
    img = Image.open(image_path).convert("RGB")
    width, height = img.size
    pixels = np.array(img, dtype=np.uint8)

    coords = get_pixel_coords(width, height, password if random_order else None, random_order)

    bits = []
    total_pixels = len(coords)
    for idx, (x, y) in enumerate(coords):
        for c in range(3):
            bits.append(pixels[y, x, c] & 1)
        if progress_callback:
            progress_callback(idx, total_pixels)

    data_bytes = bytearray()
    for i in range(0, len(bits), 8):
        if i+8 > len(bits):
            break
        byte_val = 0
        for bit in bits[i:i+8]:
            byte_val = (byte_val << 1) | bit
        data_bytes.append(byte_val)

    if len(data_bytes) < 4:
        raise ValueError("No hidden data found (too short).")

    original_size = struct.unpack(">I", bytes(data_bytes[:4]))[0]
    hidden = bytes(data_bytes[4:])

    if password:
        key = derive_key(password)
        f = Fernet(key)
        hidden = f.decrypt(hidden)

    if len(hidden) < original_size:
        try:
            hidden = zlib.decompress(hidden)
        except:
            pass
    return hidden[:original_size]

# ---------- CLI (Termux / iSH) ----------
def cli_progress(current, total):
    bar_l

