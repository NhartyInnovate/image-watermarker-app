import os
from tkinter import Tk, Label, Button, Entry, StringVar, filedialog, messagebox, Frame
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont


class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Watermarker")
        self.root.geometry("900x600")
        self.root.configure(bg="#0f172a")

        # State
        self.original_image = None       # PIL Image
        self.preview_image_tk = None     # ImageTk.PhotoImage
        self.image_path = None

        self.watermark_text_var = StringVar(value="yourwebsite.com")

        # UI
        self._build_ui()

    def _build_ui(self):
        # --------- Left: Controls ----------
        controls_frame = Frame(self.root, bg="#020617")
        controls_frame.pack(side="left", fill="y", padx=10, pady=10)

        title_label = Label(
            controls_frame,
            text="Image Watermarker",
            font=("Segoe UI", 16, "bold"),
            fg="#e5e7eb",
            bg="#020617"
        )
        title_label.pack(pady=(5, 2))

        subtitle_label = Label(
            controls_frame,
            text="Add text watermark to your images.",
            font=("Segoe UI", 9),
            fg="#9ca3af",
            bg="#020617"
        )
        subtitle_label.pack(pady=(0, 10))

        # Choose image button
        choose_btn = Button(
            controls_frame,
            text="Choose Image",
            command=self.load_image,
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6
        )
        choose_btn.pack(pady=6, fill="x")

        # Watermark text input
        wm_label = Label(
            controls_frame,
            text="Watermark Text:",
            font=("Segoe UI", 10),
            fg="#e5e7eb",
            bg="#020617"
        )
        wm_label.pack(pady=(12, 4), anchor="w")

        wm_entry = Entry(
            controls_frame,
            textvariable=self.watermark_text_var,
            font=("Segoe UI", 10),
            relief="solid"
        )
        wm_entry.pack(pady=2, fill="x")

        # Position dropdown
        pos_label = Label(
            controls_frame,
            text="Position:",
            font=("Segoe UI", 10),
            fg="#e5e7eb",
            bg="#020617"
        )
        pos_label.pack(pady=(12, 4), anchor="w")

        self.position_var = StringVar(value="bottom-right")
        pos_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.position_var,
            state="readonly",
            values=[
                "bottom-right",
                "bottom-left",
                "top-right",
                "top-left",
                "center"
            ]
        )
        pos_combo.pack(pady=2, fill="x")

        # Opacity slider
        opacity_label = Label(
            controls_frame,
            text="Opacity:",
            font=("Segoe UI", 10),
            fg="#e5e7eb",
            bg="#020617"
        )
        opacity_label.pack(pady=(12, 0), anchor="w")

        self.opacity_var = StringVar(value="180")

        opacity_scale = ttk.Scale(
            controls_frame,
            from_=50,
            to=255,
            orient="horizontal",
            command=self._on_opacity_change
        )
        opacity_scale.pack(pady=(0, 4), fill="x")

        self.opacity_value_label = Label(
            controls_frame,
            text="180 / 255",
            font=("Segoe UI", 8),
            fg="#9ca3af",
            bg="#020617"
        )
        self.opacity_value_label.pack(anchor="w")

        opacity_scale.set(180)  # ← move this AFTER label creation

        # Preview & Save buttons
        preview_btn = Button(
            controls_frame,
            text="Preview Watermark",
            command=self.preview_watermark,
            bg="#4b5563",
            fg="white",
            activebackground="#374151",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6
        )
        preview_btn.pack(pady=(16, 4), fill="x")

        save_btn = Button(
            controls_frame,
            text="Save Watermarked Image",
            command=self.save_watermarked_image,
            bg="#16a34a",
            fg="white",
            activebackground="#15803d",
            activeforeground="white",
            relief="flat",
            padx=12,
            pady=6
        )
        save_btn.pack(pady=4, fill="x")

        info_label = Label(
            controls_frame,
            text="Tip:\nChoose an image → enter watermark → preview → save.",
            font=("Segoe UI", 8),
            fg="#9ca3af",
            bg="#020617",
            justify="left"
        )
        info_label.pack(pady=(10, 0), anchor="w")

        # --------- Right: Image Preview ----------
        preview_frame = Frame(self.root, bg="#020617")
        preview_frame.pack(side="right", expand=True, fill="both", padx=10, pady=10)

        self.preview_label = Label(
            preview_frame,
            bg="#020617",
            fg="#9ca3af",
            text="No image loaded.\nClick 'Choose Image' to begin.",
            font=("Segoe UI", 11)
        )
        self.preview_label.pack(expand=True)

    # ----- Event Handlers -----

    def _on_opacity_change(self, val):
        v = int(float(val))
        self.opacity_value_label.config(text=f"{v} / 255")
        self.opacity_var.set(str(v))

    def load_image(self):
        file_types = [
            ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp"),
            ("All Files", "*.*")
        ]
        path = filedialog.askopenfilename(title="Select an Image", filetypes=file_types)
        if not path:
            return

        try:
            img = Image.open(path).convert("RGBA")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image:\n{e}")
            return

        self.original_image = img
        self.image_path = path

        self.show_preview(self.original_image)

    def show_preview(self, pil_image):
        """Resize image to fit preview area and show it in the label."""
        if pil_image is None:
            return

        # Get current preview frame size
        preview_width = self.preview_label.winfo_width()
        preview_height = self.preview_label.winfo_height()

        # Fallback if widgets not fully rendered yet
        if preview_width < 50 or preview_height < 50:
            preview_width, preview_height = 600, 500

        # Preserve aspect ratio
        img = pil_image.copy()
        img.thumbnail((preview_width, preview_height))

        self.preview_image_tk = ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.preview_image_tk, text="")

    def apply_watermark(self, base_image):
        """Return a new PIL Image with watermark applied."""
        if base_image is None:
            return None

        text = self.watermark_text_var.get().strip()
        if not text:
            return base_image

        opacity = int(self.opacity_var.get())
        position = self.position_var.get()

        # Create a transparent layer for watermark
        watermark_layer = Image.new("RGBA", base_image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark_layer)

        # Simple font handling
        try:
            # If you have a TTF font, you can use it here:
            # font = ImageFont.truetype("arial.ttf", size=int(base_image.size[1] * 0.04))
            font_size = max(20, base_image.size[1] // 20)
            font = ImageFont.truetype("arial.ttf", size=font_size)
        except:
            # Fallback to default PIL font
            font = ImageFont.load_default()

        # Get text size (Pillow 10+ compatible)
        try:
            # Newer Pillow: use textbbox
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # Older Pillow fallback (if textbbox doesn't exist)
            text_width, text_height = draw.textsize(text, font=font)

        margin = 10
        if position == "bottom-right":
            x = base_image.size[0] - text_width - margin
            y = base_image.size[1] - text_height - margin
        elif position == "bottom-left":
            x = margin
            y = base_image.size[1] - text_height - margin
        elif position == "top-right":
            x = base_image.size[0] - text_width - margin
            y = margin
        elif position == "top-left":
            x = margin
            y = margin
        else:  # center
            x = (base_image.size[0] - text_width) // 2
            y = (base_image.size[1] - text_height) // 2

        # White text with customizable opacity
        fill_color = (255, 255, 255, opacity)

        draw.text((x, y), text, font=font, fill=fill_color)

        # Combine original with watermark layer
        watermarked = Image.alpha_composite(base_image.convert("RGBA"), watermark_layer)
        return watermarked

    def preview_watermark(self):
        if self.original_image is None:
            messagebox.showinfo("No Image", "Please choose an image first.")
            return

        watermarked = self.apply_watermark(self.original_image)
        if watermarked is None:
            return
        self.show_preview(watermarked)

    def save_watermarked_image(self):
        if self.original_image is None:
            messagebox.showinfo("No Image", "Please choose an image first.")
            return

        watermarked = self.apply_watermark(self.original_image)
        if watermarked is None:
            return

        # Ask where to save
        base_name = "watermarked.png"
        if self.image_path:
            name, ext = os.path.splitext(os.path.basename(self.image_path))
            base_name = f"{name}_watermarked.png"

        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=base_name,
            filetypes=[("PNG Image", "*.png"), ("JPEG Image", "*.jpg;*.jpeg"), ("All Files", "*.*")]
        )
        if not save_path:
            return

        try:
            # Convert back to RGB if saving as JPG
            if save_path.lower().endswith((".jpg", ".jpeg")):
                watermarked.convert("RGB").save(save_path, quality=95)
            else:
                watermarked.save(save_path)
            messagebox.showinfo("Success", f"Saved watermarked image:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save image:\n{e}")


if __name__ == "__main__":
    root = Tk()
    app = WatermarkApp(root)
    root.mainloop()