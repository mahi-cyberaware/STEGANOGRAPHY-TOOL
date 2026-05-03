import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image, ImageTk, ImageFile
import numpy as np
import os
import struct
import zlib
import random
import hashlib
from cryptography.fernet import Fernet
import base64
import threading

ImageFile.LOAD_TRUNCATED_IMAGES = True

class StegoFinal:
    def __init__(self, root):
        self.root = root
        root.title("Steganography Pro – Password + Random Order + Preview")
        root.geometry("800x700")
        root.resizable(True, True)

        # ---------- Encode Frame ----------
        encode_frame = tk.LabelFrame(root, text="Encode (hide file in image)", padx=10, pady=10)
        encode_frame.pack(fill="x", padx=10, pady=5)

        # Image selection
        tk.Button(encode_frame, text="Select Cover Image", command=self.select_encode_image).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.encode_image_label = tk.Label(encode_frame, text="No image selected", fg="gray")
        self.encode_image_label.grid(row=0, column=1, sticky="w")

        # File to hide
        tk.Button(encode_frame, text="Select Secret File", command=self.select_secret_file).grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.secret_file_label = tk.Label(encode_frame, text="No file chosen", fg="gray")
        self.secret_file_label.grid(row=1, column=1, sticky="w")

        # Password
        tk.Label(encode_frame, text="Password:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.encode_password = tk.Entry(encode_frame, show="*", width=30)
        self.encode_password.grid(row=2, column=1, sticky="w")

        # Compression checkbox
        self.compress_var = tk.BooleanVar(value=True)
        tk.Checkbutton(encode_frame, text="Compress data (zlib)", variable=self.compress_var).grid(row=3, column=0, columnspan=2, sticky="w", padx=5)

        # Random order checkbox
        self.random_order_var = tk.BooleanVar(value=True)
        tk.Checkbutton(encode_frame, text="Random pixel order (password‑based)", variable=self.random_order_var).grid(row=4, column=0, columnspan=2, sticky="w", padx=5)

        # Encode button
        self.encode_btn = tk.Button(encode_frame, text="Encode & Save as PNG", command=self.start_encode, bg="lightgreen")
        self.encode_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # ---------- Decode Frame ----------
        decode_frame = tk.LabelFrame(root, text="Decode (extract hidden file)", padx=10, pady=10)
        decode_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(decode_frame, text="Select Encoded Image", command=self.select_decode_image).grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.decode_image_label = tk.Label(decode_frame, text="No image selected", fg="gray")
        self.decode_image_label.grid(row=0, column=1, sticky="w")

        tk.Label(decode_frame, text="Password:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.decode_password = tk.Entry(decode_frame, show="*", width=30)
        self.decode_password.grid(row=1, column=1, sticky="w")

        self.decode_btn = tk.Button(decode_frame, text="Decode & Save File", command=self.start_decode, bg="lightblue")
        self.decode_btn.grid(row=2, column=0, columnspan=2, pady=10)

        # ---------- Preview Area ----------
        preview_frame = tk.LabelFrame(root, text="Preview", padx=10, pady=10)
        preview_frame.pack(fill="x", padx=10, pady=5)

        self.preview_left = tk.Label(preview_frame, text="Original image", bg="#f0f0f0", width=40, height=10)
        self.preview_left.pack(side="left", padx=10, expand=True, fill="both")

        self.preview_right = tk.Label(preview_frame, text="Encoded image", bg="#f0f0f0", width=40, height=10)
        self.preview_right.pack(side="right", padx=10, expand=True, fill="both")

        # ---------- Progress Bar & Log ----------
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=5)

        self.status_text = scrolledtext.ScrolledText(root, height=10, state="disabled")
        self.status_text.pack(fill="both", expand=True, padx=10, pady=5)

        # Internal variables
        self.encode_image_path = None
        self.secret_file_path = None
        self.decode_image_path = None
        self.encoded_image_preview = None

    # ------------------ Helper Functions ------------------
    def log(self, msg):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, msg + "\n")
        self.status_text.see(tk.END)
        self.status_text.config(state="disabled")
        self.root.update_idletasks()

    def update_progress(self, value, max_val):
        self.progress["value"] = (value / max_val) * 100
        self.root.update_idletasks()

    def show_preview(self, img_path, side="left"):
        try:
            img = Image.open(img_path)
            img.thumbnail((200, 200))
            photo = ImageTk.PhotoImage(img)
            if side == "left":
                self.preview_left.config(image=photo, text="")
                self.preview_left.image = photo
            else:
                self.preview_right.config(image=photo, text="")
                self.preview_right.image = photo
        except:
            pass

    # ------------------ Encoding Thread ------------------
    def start_encode(self):
        if not self.encode_image_path or not self.secret_file_path:
            messagebox.showerror("Error", "Select image and secret file.")
            return
        password = self.encode_password.get()
        if not password and self.random_order_var.get():
            messagebox.showerror("Error", "Password is required for random order or encryption.")
            return
        self.encode_btn.config(state="disabled")
        threading.Thread(target=self.encode, daemon=True).start()

    def encode(self):
        try:
            # Load image
            img = Image.open(self.encode_image_path)
            if img.mode != "RGB":
                img = img.convert("RGB")
                self.log(f"Converted image to RGB.")

            total_pixels = img.size[0] * img.size[1]
            max_bytes = (total_pixels * 3) // 8 - 8   # reserve 8 bytes for metadata
            secret_size = os.path.getsize(self.secret_file_path)

            # Read file
            with open(self.secret_file_path, "rb") as f:
                secret_data = f.read()

            # Compression
            if self.compress_var.get():
                compressed = zlib.compress(secret_data, level=9)
                if len(compressed) < secret_size:
                    secret_data = compressed
                    self.log(f"Compressed: {secret_size} -> {len(secret_data)} bytes")
                else:
                    self.log("Compression not beneficial; storing uncompressed.")
            else:
                self.log("Compression disabled.")

            # Encryption (if password provided)
            if self.encode_password.get():
                key = self.derive_key(self.encode_password.get())
                f = Fernet(key)
                secret_data = f.encrypt(secret_data)
                self.log(f"Encrypted data with password.")

            # Build payload: [4-byte original size] + [4-byte encrypted size? not needed] + data
            # Actually we store original uncompressed & unencrypted size for later verification.
            original_size = os.path.getsize(self.secret_file_path)  # keep original size
            payload = struct.pack(">I", original_size) + secret_data
            if len(payload) > max_bytes:
                raise Exception(f"Payload too large ({len(payload)} bytes). Max {max_bytes} bytes.")

            # Convert to bits
            payload_bits = []
            for byte in payload:
                for bit in range(7, -1, -1):
                    payload_bits.append((byte >> bit) & 1)

            total_bits = len(payload_bits)
            self.log(f"Total bits to embed: {total_bits}")

            # Get pixel coordinates list
            h, w = img.size[1], img.size[0]
            pixels = np.array(img, dtype=np.uint8)
            coords = [(x, y) for y in range(h) for x in range(w)]

            # Shuffle if random order enabled
            if self.random_order_var.get():
                seed = int(hashlib.sha256(self.encode_password.get().encode()).hexdigest(), 16) % (2**32)
                random.seed(seed)
                random.shuffle(coords)
                self.log("Pixel order randomized (password-based).")

            # Embed bits
            bit_idx = 0
            total_coords = len(coords)
            for idx, (x, y) in enumerate(coords):
                if bit_idx >= total_bits:
                    break
                for c in range(3):  # RGB
                    if bit_idx < total_bits:
                        pixels[y, x, c] = (pixels[y, x, c] & 0xFE) | payload_bits[bit_idx]
                        bit_idx += 1
                self.update_progress(idx, total_coords)
            self.log(f"Embedded {bit_idx} bits.")

            # Save encoded image
            output_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
            if not output_path:
                return
            encoded_img = Image.fromarray(pixels, mode="RGB")
            encoded_img.save(output_path, format="PNG")
            self.log(f"✅ Encoded image saved: {output_path}")
            self.show_preview(output_path, side="right")
            messagebox.showinfo("Success", "Encoding completed!")
        except Exception as e:
            messagebox.showerror("Encoding Error", str(e))
            self.log(f"ERROR: {e}")
        finally:
            self.encode_btn.config(state="normal")
            self.progress["value"] = 0

    # ------------------ Decoding Thread ------------------
    def start_decode(self):
        if not self.decode_image_path:
            messagebox.showerror("Error", "Select an encoded image.")
            return
        password = self.decode_password.get()
        if not password and self.random_order_var.get():
            # We don't know if random order was used; if user gives password but random order off, okay.
            # But we need password for decryption anyway. Better to ask.
            pass
        self.decode_btn.config(state="disabled")
        threading.Thread(target=self.decode, daemon=True).start()

    def decode(self):
        try:
            img = Image.open(self.decode_image_path)
            if img.mode != "RGB":
                img = img.convert("RGB")
                self.log("Converted to RGB for decoding.")

            h, w = img.size[1], img.size[0]
            pixels = np.array(img, dtype=np.uint8)
            coords = [(x, y) for y in range(h) for x in range(w)]

            # If password is provided, assume random order was used with that password
            password = self.decode_password.get()
            if password:
                seed = int(hashlib.sha256(password.encode()).hexdigest(), 16) % (2**32)
                random.seed(seed)
                random.shuffle(coords)
                self.log("Using password-based pixel order for extraction.")
            else:
                self.log("No password – extracting in natural order.")

            # Extract bits in the order defined by coords
            bits = []
            total_coords = len(coords)
            for idx, (x, y) in enumerate(coords):
                for c in range(3):
                    bits.append(pixels[y, x, c] & 1)
                self.update_progress(idx, total_coords)
                if len(bits) >= 32:  # we need at least the length header
                    # Try to parse length after having enough bits
                    pass

            # Convert bits to bytes
            data_bytes = bytearray()
            for k in range(0, len(bits), 8):
                if k+8 > len(bits):
                    break
                byte_bits = bits[k:k+8]
                byte_val = 0
                for bit in byte_bits:
                    byte_val = (byte_val << 1) | bit
                data_bytes.append(byte_val)

            if len(data_bytes) < 4:
                raise ValueError("No hidden data found (too few bytes).")

            original_size = struct.unpack(">I", bytes(data_bytes[:4]))[0]
            hidden_data = bytes(data_bytes[4:])

            # First try decryption if password given
            if password:
                try:
                    key = self.derive_key(password)
                    f = Fernet(key)
                    hidden_data = f.decrypt(hidden_data)
                    self.log("Decryption successful.")
                except Exception as e:
                    self.log(f"Decryption failed (wrong password or no encryption): {e}")

            # Then try decompression if needed (compare size)
            if len(hidden_data) < original_size:
                try:
                    hidden_data = zlib.decompress(hidden_data)
                    self.log("Decompression successful.")
                except:
                    self.log("Not compressed or decompression failed.")
            if len(hidden_data) > original_size:
                hidden_data = hidden_data[:original_size]

            save_path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("All files", "*.*")])
            if not save_path:
                return
            with open(save_path, "wb") as f:
                f.write(hidden_data)
            self.log(f"✅ Extracted {len(hidden_data)} bytes to {save_path}")
            messagebox.showinfo("Success", "Decoding completed!")
        except Exception as e:
            messagebox.showerror("Decoding Error", str(e))
            self.log(f"ERROR: {e}")
        finally:
            self.decode_btn.config(state="normal")
            self.progress["value"] = 0

    # ------------------ Crypto Helpers ------------------
    def derive_key(self, password):
        # Use PBKDF2 to get a 32-byte key, then base64 encode for Fernet
        salt = b"stegosalt2026"  # fixed salt for simplicity
        kdf = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000, dklen=32)
        return base64.urlsafe_b64encode(kdf)

    # ------------------ UI Callbacks ------------------
    def select_encode_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.bmp *.tiff *.tif *.jpg *.jpeg")])
        if path:
            self.encode_image_path = path
            self.encode_image_label.config(text=os.path.basename(path), fg="black")
            self.show_preview(path, side="left")
            if path.lower().endswith(('.jpg','.jpeg')):
                self.log("⚠️ Warning: JPEG as source is lossy – final PNG will be fine, but avoid re‑saving as JPEG.")

    def select_secret_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.secret_file_path = path
            self.secret_file_label.config(text=os.path.basename(path), fg="black")

    def select_decode_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.bmp *.tiff *.tif *.jpg *.jpeg")])
        if path:
            self.decode_image_path = path
            self.decode_image_label.config(text=os.path.basename(path), fg="black")
            self.show_preview(path, side="left")  # show encoded image on left
            # Clear right preview
            self.preview_right.config(image="", text="Encoded image (will appear after encoding)")

if __name__ == "__main__":
    root = tk.Tk()
    app = StegoFinal(root)
    root.mainloop()
