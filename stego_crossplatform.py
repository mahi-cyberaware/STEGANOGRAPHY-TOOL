#!/usr/bin/env python3
"""
Cross‑Platform LSB Steganography Tool
Supports: Kali Linux (full GUI), Termux (Android CLI), iOS iSH (CLI)
Features: encryption, compression, random pixel order (password‑based)
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
    bar_len = 40
    percent = current / total
    filled = int(bar_len * percent)
    bar = '█' * filled + '░' * (bar_len - filled)
    sys.stdout.write(f'\r[{bar}] {int(percent*100)}%')
    sys.stdout.flush()

def run_cli():
    print("\n🔒 Steganography Tool (CLI mode)")
    print("================================")
    while True:
        print("\n1. Encode (hide file)")
        print("2. Decode (extract file)")
        print("3. Exit")
        choice = input("Choose [1-3]: ").strip()
        if choice == '1':
            img_path = input("Cover image path: ").strip()
            if not os.path.isfile(img_path):
                print("File not found.")
                continue
            secret_path = input("Secret file path: ").strip()
            if not os.path.isfile(secret_path):
                print("File not found.")
                continue
            output_path = input("Output PNG path: ").strip()
            password = input("Password (leave empty for none): ").strip() or None
            compress = input("Compress data? (y/n): ").strip().lower() == 'y'
            random_order = input("Random pixel order? (y/n): ").strip().lower() == 'y'
            if random_order and not password:
                print("Random order requires a password. Enabling anyway but will use natural order.")
                random_order = False
            try:
                with open(secret_path, "rb") as f:
                    secret_data = f.read()
                print("Encoding...")
                out_img = encode_data(img_path, secret_data, password, compress, random_order, cli_progress)
                out_img.save(output_path, "PNG")
                print(f"\n✅ Saved to {output_path}")
            except Exception as e:
                print(f"\n❌ Error: {e}")
        elif choice == '2':
            img_path = input("Encoded image path: ").strip()
            if not os.path.isfile(img_path):
                print("File not found.")
                continue
            output_path = input("Output file path: ").strip()
            password = input("Password (used during encoding): ").strip() or None
            random_order = input("Was random order used? (y/n): ").strip().lower() == 'y'
            if random_order and not password:
                print("Random order requires password. Assuming natural order.")
                random_order = False
            try:
                print("Decoding...")
                extracted = decode_data(img_path, password, random_order, cli_progress)
                with open(output_path, "wb") as f:
                    f.write(extracted)
                print(f"\n✅ Extracted {len(extracted)} bytes to {output_path}")
            except Exception as e:
                print(f"\n❌ Error: {e}")
        elif choice == '3':
            break
        else:
            print("Invalid choice.")

# ---------- GUI (Kali / desktop) ----------
def run_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk
    from PIL import ImageTk
    import threading

    class StegoGUI:
        def __init__(self, root):
            self.root = root
            root.title("Steganography Pro (Cross‑Platform)")
            root.geometry("750x650")
            self.progress = None
            self.status_text = None
            self.encode_image_path = None
            self.secret_file_path = None
            self.decode_image_path = None
            self.build_ui()

        def build_ui(self):
            # Encode frame
            encode_frame = tk.LabelFrame(self.root, text="Encode (hide file in image)", padx=10, pady=10)
            encode_frame.pack(fill="x", padx=10, pady=5)
            tk.Button(encode_frame, text="Select Cover Image", command=self.select_encode_image).grid(row=0, column=0, sticky="w", padx=5)
            self.encode_image_label = tk.Label(encode_frame, text="No image selected", fg="gray")
            self.encode_image_label.grid(row=0, column=1, sticky="w")
            tk.Button(encode_frame, text="Select Secret File", command=self.select_secret_file).grid(row=1, column=0, sticky="w", padx=5)
            self.secret_file_label = tk.Label(encode_frame, text="No file chosen", fg="gray")
            self.secret_file_label.grid(row=1, column=1, sticky="w")
            tk.Label(encode_frame, text="Password:").grid(row=2, column=0, sticky="w", padx=5)
            self.encode_password = tk.Entry(encode_frame, show="*", width=30)
            self.encode_password.grid(row=2, column=1, sticky="w")
            self.compress_var = tk.BooleanVar(value=True)
            tk.Checkbutton(encode_frame, text="Compress data (zlib)", variable=self.compress_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=5)
            self.random_var = tk.BooleanVar(value=True)
            tk.Checkbutton(encode_frame, text="Random pixel order (password‑based)", variable=self.random_var).grid(row=4, column=0, columnspan=2, sticky="w", padx=5)
            self.encode_btn = tk.Button(encode_frame, text="Encode & Save as PNG", command=self.start_encode, bg="lightgreen")
            self.encode_btn.grid(row=5, column=0, columnspan=2, pady=10)

            # Decode frame
            decode_frame = tk.LabelFrame(self.root, text="Decode (extract hidden file)", padx=10, pady=10)
            decode_frame.pack(fill="x", padx=10, pady=5)
            tk.Button(decode_frame, text="Select Encoded Image", command=self.select_decode_image).grid(row=0, column=0, sticky="w", padx=5)
            self.decode_image_label = tk.Label(decode_frame, text="No image selected", fg="gray")
            self.decode_image_label.grid(row=0, column=1, sticky="w")
            tk.Label(decode_frame, text="Password:").grid(row=1, column=0, sticky="w", padx=5)
            self.decode_password = tk.Entry(decode_frame, show="*", width=30)
            self.decode_password.grid(row=1, column=1, sticky="w")
            self.decode_random_var = tk.BooleanVar(value=True)
            tk.Checkbutton(decode_frame, text="Random order was used (password required)", variable=self.decode_random_var).grid(row=2, column=0, columnspan=2, sticky="w", padx=5)
            self.decode_btn = tk.Button(decode_frame, text="Decode & Save File", command=self.start_decode, bg="lightblue")
            self.decode_btn.grid(row=3, column=0, columnspan=2, pady=10)

            # Progress & Log
            self.progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode="determinate")
            self.progress.pack(pady=5)
            self.status_text = scrolledtext.ScrolledText(self.root, height=10, state="disabled")
            self.status_text.pack(fill="both", expand=True, padx=10, pady=5)

        def log(self, msg):
            self.status_text.config(state="normal")
            self.status_text.insert(tk.END, msg + "\n")
            self.status_text.see(tk.END)
            self.status_text.config(state="disabled")

        def update_progress(self, current, total):
            self.progress["value"] = (current / total) * 100
            self.root.update_idletasks()

        def select_encode_image(self):
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.bmp *.tiff *.jpg *.jpeg")])
            if path:
                self.encode_image_path = path
                self.encode_image_label.config(text=os.path.basename(path), fg="black")

        def select_secret_file(self):
            path = filedialog.askopenfilename()
            if path:
                self.secret_file_path = path
                self.secret_file_label.config(text=os.path.basename(path), fg="black")

        def select_decode_image(self):
            path = filedialog.askopenfilename(filetypes=[("PNG images", "*.png")])
            if path:
                self.decode_image_path = path
                self.decode_image_label.config(text=os.path.basename(path), fg="black")

        def start_encode(self):
            if not self.encode_image_path or not self.secret_file_path:
                messagebox.showerror("Error", "Select both image and secret file.")
                return
            if self.random_var.get() and not self.encode_password.get():
                messagebox.showerror("Error", "Random order requires a password.")
                return
            self.encode_btn.config(state="disabled")
            threading.Thread(target=self.encode, daemon=True).start()

        def encode(self):
            try:
                with open(self.secret_file_path, "rb") as f:
                    secret_data = f.read()
                self.log("Encoding started...")
                out_img = encode_data(
                    self.encode_image_path, secret_data,
                    self.encode_password.get() or None,
                    self.compress_var.get(),
                    self.random_var.get(),
                    self.update_progress
                )
                output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
                if output_path:
                    out_img.save(output_path, "PNG")
                    self.log(f"✅ Encoded image saved: {output_path}")
                    messagebox.showinfo("Success", "Encoding completed!")
                else:
                    self.log("Encoding cancelled.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.log(f"ERROR: {e}")
            finally:
                self.encode_btn.config(state="normal")
                self.progress["value"] = 0

        def start_decode(self):
            if not self.decode_image_path:
                messagebox.showerror("Error", "Select an encoded image.")
                return
            self.decode_btn.config(state="disabled")
            threading.Thread(target=self.decode, daemon=True).start()

        def decode(self):
            try:
                self.log("Decoding started...")
                extracted = decode_data(
                    self.decode_image_path,
                    self.decode_password.get() or None,
                    self.decode_random_var.get(),
                    self.update_progress
                )
                output_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("All files", "*.*")])
                if output_path:
                    with open(output_path, "wb") as f:
                        f.write(extracted)
                    self.log(f"✅ Extracted {len(extracted)} bytes to {output_path}")
                    messagebox.showinfo("Success", "Decoding completed!")
                else:
                    self.log("Decoding cancelled.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.log(f"ERROR: {e}")
            finally:
                self.decode_btn.config(state="normal")
                self.progress["value"] = 0

    root = tk.Tk()
    app = StegoGUI(root)
    root.mainloop()

# ---------- Main entry ----------
if __name__ == "__main__":
    if has_display() and not is_termux() and not is_ios_ish():
        try:
            import tkinter
            run_gui()
        except ImportError:
            print("Tkinter missing, falling back to CLI.")
            run_cli()
    else:
        print("No graphical display – running in CLI mode.")
        run_cli()

