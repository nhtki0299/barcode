import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw
import io

from ui.tabs import setup_encode_tab, setup_decode_tab, setup_doc_tab, setup_process_tab
from core.encode import generate_barcode, generate_qrcode, generate_datamatrix, build_log
from core.decode import run_decode
from core.image_processing import apply_image_processing
from explorers.datamatrix import open_datamatrix_explorer
from explorers.qr import open_qr_explorer

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class CodeGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Pro Barcode Studio")
        self.geometry("1100x750")

        # Layout chính: 2 cột (Sidebar và Main Content)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ----------------------------------------------------
        # SIDEBAR (LEFT)
        # ----------------------------------------------------
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color="#18181B")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Barcode Studio", font=ctk.CTkFont(family="Roboto", size=20, weight="bold"), text_color="#0EA5E9")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 30))

        # Nút điều hướng
        self.nav_btn_encode = ctk.CTkButton(self.sidebar_frame, text="✨ TẠO MÃ", corner_radius=8, height=40, border_spacing=10, text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", font=ctk.CTkFont(size=14, weight="bold"), command=lambda: self.select_frame("encode"))
        self.nav_btn_encode.grid(row=1, column=0, padx=15, pady=5, sticky="ew")

        self.nav_btn_decode = ctk.CTkButton(self.sidebar_frame, text="🔍 GIẢI MÃ", corner_radius=8, height=40, border_spacing=10, text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", font=ctk.CTkFont(size=14, weight="bold"), command=lambda: self.select_frame("decode"))
        self.nav_btn_decode.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.nav_btn_process = ctk.CTkButton(self.sidebar_frame, text="🛠️ XỬ LÝ ẢNH", corner_radius=8, height=40, border_spacing=10, text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", font=ctk.CTkFont(size=14, weight="bold"), command=lambda: self.select_frame("process"))
        self.nav_btn_process.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        self.nav_btn_doc = ctk.CTkButton(self.sidebar_frame, text="📚 TÀI LIỆU", corner_radius=8, height=40, border_spacing=10, text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"), anchor="w", font=ctk.CTkFont(size=14, weight="bold"), command=lambda: self.select_frame("doc"))
        self.nav_btn_doc.grid(row=4, column=0, padx=15, pady=5, sticky="ew")
        
        # ----------------------------------------------------
        # MAIN CONTENT (RIGHT)
        # ----------------------------------------------------
        self.encode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.decode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.process_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.doc_frame = ctk.CTkFrame(self, fg_color="transparent")

        # Setup Nội dung
        setup_encode_tab(self.encode_frame, self)
        setup_decode_tab(self.decode_frame, self)
        setup_process_tab(self.process_frame, self)
        setup_doc_tab(self.doc_frame, self)

        # Trạng thái ban đầu
        self.generated_image = None
        self.generated_image_ctk = None
        self.loaded_decode_image = None
        self.loaded_decode_image_path = None
        self.decoded_results = []
        
        self.raw_process_image = None
        self.processed_image = None
        
        self.select_frame("encode")

    def select_frame(self, name):
        # Reset màu nút
        default_color = "transparent"
        active_color = "#0EA5E9"
        
        self.nav_btn_encode.configure(fg_color=default_color)
        self.nav_btn_decode.configure(fg_color=default_color)
        self.nav_btn_process.configure(fg_color=default_color)
        self.nav_btn_doc.configure(fg_color=default_color)
        
        # Ẩn tất cả frame
        self.encode_frame.grid_forget()
        self.decode_frame.grid_forget()
        self.process_frame.grid_forget()
        self.doc_frame.grid_forget()
        
        # Hiện frame được chọn và đổi màu
        if name == "encode":
            self.nav_btn_encode.configure(fg_color=active_color)
            self.encode_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        elif name == "decode":
            self.nav_btn_decode.configure(fg_color=active_color)
            self.decode_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        elif name == "process":
            self.nav_btn_process.configure(fg_color=active_color)
            self.process_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        elif name == "doc":
            self.nav_btn_doc.configure(fg_color=active_color)
            self.doc_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def update_config_ui(self, value=None):
        enc_type = self.encoding_var.get()
        self.barcode_config.pack_forget()
        self.qr_config.pack_forget()
        self.datamatrix_config.pack_forget()

        if enc_type == "barcode":
            self.barcode_config.pack(side="left", fill="x", expand=True)
        elif enc_type == "qrcode":
            self.qr_config.pack(side="left", fill="x", expand=True)
        elif enc_type == "datamatrix":
            self.datamatrix_config.pack(side="left", fill="x", expand=True)

    def generate_code(self):
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text or text == "Nhập text cần mã hóa...":
            messagebox.showwarning("Lỗi", "Vui lòng nhập text!")
            return

        enc_type = self.encoding_var.get()
        self.log_textbox.delete("1.0", "end")

        try:
            if enc_type == "barcode":
                barcode_type = self.barcode_type_var.get()
                img = generate_barcode(text, barcode_type)
                log = build_log(text, "barcode")
            elif enc_type == "qrcode":
                error_val = self.qr_error_var.get()
                img = generate_qrcode(text, error_val)
                log = build_log(text, "qrcode", error_val=error_val)
            elif enc_type == "datamatrix":
                img = generate_datamatrix(text)
                log = build_log(text, "datamatrix")
                
            self.log_textbox.insert("end", log)
            self.update_preview(img)
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
            self.log_textbox.insert("end", f"\n[ERROR] {str(e)}")

    def update_preview(self, img: Image.Image):
        self.generated_image = img
        
        img_copy = img.copy()
        img_copy.thumbnail((300, 300), Image.Resampling.LANCZOS)
        
        self.generated_image_ctk = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=(img_copy.width, img_copy.height))
        self.preview_label.configure(image=self.generated_image_ctk, text="")
        
        self.save_image_btn.configure(state="normal")
        self.save_log_btn.configure(state="normal")

    def save_image(self):
        if self.generated_image:
            import datetime
            import re
            
            raw_text = self.text_input.get("1.0", "end-1c").strip()
            safe_text = re.sub(r'[^a-zA-Z0-9]', '_', raw_text)[:20]
            if not safe_text:
                safe_text = "code"
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"{safe_text}_{current_time}.png"
            
            filepath = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=".png", filetypes=[("PNG files", "*.png")])
            if filepath:
                self.generated_image.save(filepath)
                messagebox.showinfo("Thành công", "Đã lưu ảnh!")

    def save_log(self):
        log_text = self.log_textbox.get("1.0", "end-1c")
        if log_text:
            import datetime
            import re
            
            raw_text = self.text_input.get("1.0", "end-1c").strip()
            safe_text = re.sub(r'[^a-zA-Z0-9]', '_', raw_text)[:20]
            if not safe_text:
                safe_text = "log"
            current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"log_{safe_text}_{current_time}.txt"
            
            filepath = filedialog.asksaveasfilename(initialfile=default_name, defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if filepath:
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(log_text)
                messagebox.showinfo("Thành công", "Đã lưu file log!")

    def load_decode_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")])
        if filepath:
            self.loaded_decode_image_path = filepath
            img = Image.open(filepath).convert("RGB")
            self.loaded_decode_image = img
            
            img_copy = img.copy()
            img_copy.thumbnail((400, 400), Image.Resampling.LANCZOS)
            self.decode_image_ctk = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=(img_copy.width, img_copy.height))
            self.decode_preview_label.configure(image=self.decode_image_ctk, text="")
            
            self.btn_run_decode.configure(state="normal")
            self.btn_open_explorer.configure(state="disabled")
            
            self.decode_log_textbox.delete("1.0", "end")
            self.decode_log_textbox.insert("end", f"Đã tải ảnh: {filepath}\nKích thước: {img.width}x{img.height} px\nSẵn sàng giải mã...\n")

    def run_decode(self):
        self.decode_log_textbox.delete("1.0", "end")
        log, results = run_decode(self.loaded_decode_image)
        self.decode_log_textbox.insert("end", log)
        self.decoded_results = results
        
        if results:
            img_copy = self.loaded_decode_image.copy()
            draw = ImageDraw.Draw(img_copy)
            has_datamatrix = False
            for res in results:
                rect = res["rect"]
                draw.rectangle([rect.left, rect.top, rect.left + rect.width, rect.top + rect.height], outline="#8b5cf6", width=4)
                if res["type"] == "DataMatrix":
                    has_datamatrix = True
                    
            img_copy.thumbnail((400, 400), Image.Resampling.LANCZOS)
            self.decode_image_ctk = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=(img_copy.width, img_copy.height))
            self.decode_preview_label.configure(image=self.decode_image_ctk)
            
            if has_datamatrix:
                self.btn_open_explorer.configure(state="normal")
            else:
                self.btn_open_explorer.configure(state="disabled")

    def open_datamatrix_explorer(self):
        if hasattr(self, "dm_explorer_window") and self.dm_explorer_window is not None and self.dm_explorer_window.winfo_exists():
            self.dm_explorer_window.lift()
            self.dm_explorer_window.focus()
            return
            
        text = self.text_input.get("1.0", "end-1c").strip()
        win = open_datamatrix_explorer(text, self)
        if win:
            self.dm_explorer_window = win

    def open_qr_explorer(self):
        if hasattr(self, "qr_explorer_window") and self.qr_explorer_window is not None and self.qr_explorer_window.winfo_exists():
            self.qr_explorer_window.lift()
            self.qr_explorer_window.focus()
            return
            
        text = self.text_input.get("1.0", "end-1c").strip()
        error_val = self.qr_error_var.get()
        win = open_qr_explorer(text, error_val, self)
        if win:
            self.qr_explorer_window = win
        
    def open_decoded_explorer(self):
        if not hasattr(self, "decoded_results") or not self.decoded_results:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu giải mã.")
            return

        for res in self.decoded_results:
            if res.get("type") == "DataMatrix":
                text = res.get("data", "")
                
                if hasattr(self, "dm_explorer_window") and self.dm_explorer_window is not None and self.dm_explorer_window.winfo_exists():
                    self.dm_explorer_window.destroy()
                    
                win = open_datamatrix_explorer(text, self)
                if win:
                    self.dm_explorer_window = win
                return
                
        messagebox.showinfo("Thông báo", "Không tìm thấy DataMatrix trong kết quả giải mã để trích xuất.")

    def load_process_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp"), ("All files", "*.*")])
        if filepath:
            img = Image.open(filepath).convert("RGB")
            self.raw_process_image = img
            self.update_processed_preview()
            self.btn_send_decode.configure(state="normal")

    def update_processed_preview(self):
        if not self.raw_process_image:
            return
            
        params = {
            'invert': self.proc_invert_var.get(),
            'contrast': self.proc_contrast_var.get(),
            'brightness': self.proc_brightness_var.get(),
            'grayscale': self.proc_gray_var.get(),
            'sharpen': self.proc_sharpen_var.get(),
            'blur_kernel': self.proc_blur_var.get(),
            'threshold_type': self.proc_thresh_type_var.get(),
            'threshold_val': self.proc_thresh_val_var.get(),
            'adaptive_block': self.proc_adaptive_block_var.get(),
            'adaptive_c': self.proc_adaptive_c_var.get(),
            'morph_type': self.proc_morph_type_var.get(),
            'morph_iter': self.proc_morph_iter_var.get()
        }
        
        try:
            self.processed_image = apply_image_processing(self.raw_process_image, params)
            
            img_copy = self.processed_image.copy()
            img_copy.thumbnail((500, 500), Image.Resampling.LANCZOS)
            self.process_image_ctk = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=(img_copy.width, img_copy.height))
            self.process_preview_label.configure(image=self.process_image_ctk, text="")
        except Exception as e:
            self.process_preview_label.configure(text=f"Lỗi: {str(e)}", image="")

    def send_to_decode(self):
        if self.processed_image:
            self.loaded_decode_image = self.processed_image
            
            img_copy = self.processed_image.copy()
            img_copy.thumbnail((400, 400), Image.Resampling.LANCZOS)
            self.decode_image_ctk = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=(img_copy.width, img_copy.height))
            self.decode_preview_label.configure(image=self.decode_image_ctk, text="")
            
            self.btn_run_decode.configure(state="normal")
            self.btn_open_explorer.configure(state="disabled")
            
            self.decode_log_textbox.delete("1.0", "end")
            self.decode_log_textbox.insert("end", f"Đã nhận ảnh từ Tab Xử Lý Ảnh.\nSẵn sàng giải mã...\n")
            
            self.select_frame("decode")
            self.run_decode()

if __name__ == "__main__":
    app = CodeGeneratorApp()
    app.mainloop()
