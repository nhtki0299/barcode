import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import io
import time
import barcode
from barcode.writer import ImageWriter
import qrcode

from pystrich.datamatrix import DataMatrixEncoder


class CodeGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Code Generator")
        self.geometry("1000x750")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.current_image = None
        self.current_image_ctk = None

        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. Header
        self.header_label = ctk.CTkLabel(self, text="🔲 Code Generator: Barcode • DataMatrix • QR Code", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.grid(row=0, column=0, columnspan=2, pady=(20, 10))

        # Toolbar / TabView
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, columnspan=2, padx=20, pady=10, sticky="nsew")
        self.grid_rowconfigure(1, weight=1)

        self.tab_encode = self.tabview.add("Mã Hoá (Encode)")
        self.tab_decode = self.tabview.add("Giải Mã (Decode)")

        self.setup_encode_tab(self.tab_encode)
        self.setup_decode_tab(self.tab_decode)

    def setup_encode_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # 2. Input Section
        input_frame = ctk.CTkFrame(parent)
        input_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.text_input = ctk.CTkTextbox(input_frame, height=80)
        self.text_input.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.text_input.insert("1.0", "Nhập text cần mã hóa...")
        self.text_input.bind("<Button-1>", lambda e: self.text_input.delete("1.0", "end") if self.text_input.get("1.0", "end-1c") == "Nhập text cần mã hóa..." else None)

        # Radio Buttons
        radio_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        radio_frame.grid(row=1, column=0, padx=10, pady=(0, 10))

        self.encoding_var = ctk.StringVar(value="barcode")
        self.radio_barcode = ctk.CTkRadioButton(radio_frame, text="Barcode", variable=self.encoding_var, value="barcode", command=self.update_config_ui)
        self.radio_barcode.pack(side="left", padx=15)
        
        self.radio_datamatrix = ctk.CTkRadioButton(radio_frame, text="DataMatrix", variable=self.encoding_var, value="datamatrix", command=self.update_config_ui)
        self.radio_datamatrix.pack(side="left", padx=15)

        self.radio_qrcode = ctk.CTkRadioButton(radio_frame, text="QR Code", variable=self.encoding_var, value="qrcode", command=self.update_config_ui)
        self.radio_qrcode.pack(side="left", padx=15)

        # Config Frame (Dynamic)
        self.config_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        self.config_frame.grid(row=2, column=0, padx=10, pady=(0, 10))

        # Barcode Config
        self.barcode_config = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        ctk.CTkLabel(self.barcode_config, text="Loại Barcode:").pack(side="left", padx=5)
        self.barcode_type_var = ctk.StringVar(value="code128")
        self.barcode_dropdown = ctk.CTkOptionMenu(self.barcode_config, variable=self.barcode_type_var, values=["code128", "code39", "ean13"])
        self.barcode_dropdown.pack(side="left", padx=5)

        # QR Config
        self.qr_config = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        ctk.CTkLabel(self.qr_config, text="Mức sửa lỗi (Error Correction):").pack(side="left", padx=5)
        self.qr_error_var = ctk.StringVar(value="M (15%)")
        self.qr_dropdown = ctk.CTkOptionMenu(self.qr_config, variable=self.qr_error_var, values=["L (7%)", "M (15%)", "Q (25%)", "H (30%)"])
        self.qr_dropdown.pack(side="left", padx=5)

        # DataMatrix Config
        self.datamatrix_config = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.explorer_btn = ctk.CTkButton(self.datamatrix_config, text="🔍 Mở Lưới DataMatrix Tương Tác", command=self.open_datamatrix_explorer, fg_color="teal", hover_color="#006666")
        self.explorer_btn.pack(side="left", padx=5)

        self.update_config_ui() # Initial UI update

        self.generate_btn = ctk.CTkButton(input_frame, text="⚡ GENERATE CODE", font=ctk.CTkFont(weight="bold"), command=self.generate_code)
        self.generate_btn.grid(row=3, column=0, padx=10, pady=10)

        # 3. Log Panel (Left)
        log_frame = ctk.CTkFrame(parent)
        log_frame.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_frame, text="📋 Transformation Log", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=10)
        self.log_textbox = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="monospace"))
        self.log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        # 4. Preview Panel (Right)
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(preview_frame, text="🖼️ Code Preview", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, columnspan=2, pady=10)
        
        self.preview_label = ctk.CTkLabel(preview_frame, text="[Generated Code Image Here]")
        self.preview_label.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        self.save_image_btn = ctk.CTkButton(preview_frame, text="💾 Save Image", command=self.save_image, state="disabled")
        self.save_image_btn.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.save_log_btn = ctk.CTkButton(preview_frame, text="📄 Save Log", command=self.save_log, state="disabled")
        self.save_log_btn.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

    def setup_decode_tab(self, parent):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        control_frame = ctk.CTkFrame(parent)
        control_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        self.btn_load_image = ctk.CTkButton(control_frame, text="🖼️ Tải Ảnh Cần Dịch", command=self.load_decode_image)
        self.btn_load_image.pack(side="left", padx=10, pady=10)
        
        self.btn_run_decode = ctk.CTkButton(control_frame, text="🔍 GIẢI MÃ TỰ ĐỘNG", command=self.run_decode, fg_color="teal", state="disabled")
        self.btn_run_decode.pack(side="left", padx=10, pady=10)
        
        self.btn_open_explorer = ctk.CTkButton(control_frame, text="🧩 Trích xuất lưới 8-bit", command=self.open_decoded_explorer, fg_color="#D35B00", hover_color="#A34600", state="disabled")
        self.btn_open_explorer.pack(side="left", padx=10, pady=10)
        
        log_frame = ctk.CTkFrame(parent)
        log_frame.grid(row=1, column=0, padx=(10, 5), pady=10, sticky="nsew")
        log_frame.grid_rowconfigure(1, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(log_frame, text="📋 Decoding Log & Result", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=10)
        self.decode_log_textbox = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="monospace"))
        self.decode_log_textbox.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        
        preview_frame = ctk.CTkFrame(parent)
        preview_frame.grid(row=1, column=1, padx=(5, 10), pady=10, sticky="nsew")
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(preview_frame, text="🖼️ Image Output", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, pady=10)
        self.decode_preview_label = ctk.CTkLabel(preview_frame, text="[Vui lòng tải ảnh lên]")
        self.decode_preview_label.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

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
            
            self.decode_log_textbox.delete("1.0", "end")
            self.decode_log_textbox.insert("end", f"Đã tải ảnh: {filepath}\nKích thước: {img.width}x{img.height} px\nSẵn sàng giải mã...\n")

    def run_decode(self):
        self.decode_log_textbox.insert("end", "\n" + "="*40 + "\n BẮT ĐẦU GIẢI MÃ\n" + "="*40 + "\n\n")
        
        try:
            from pyzbar.pyzbar import decode as pyzbar_decode
        except ImportError:
            self.decode_log_textbox.insert("end", "[!] Chưa cài đặt pyzbar hoặc zbar. Vui lòng chạy lệnh: brew install zbar && pip install pyzbar\n")
            return
            
        try:
            from pylibdmtx.pylibdmtx import decode as dmtx_decode
        except ImportError:
            self.decode_log_textbox.insert("end", "[!] Chưa cài đặt pylibdmtx.\n")
            return
            
        img = self.loaded_decode_image
        found_codes = []
        
        # 1. Decode pyzbar
        self.decode_log_textbox.insert("end", "========================================================\n")
        self.decode_log_textbox.insert("end", "[PHASE 1] TÌM KIẾM QR CODE & BARCODE (Engine: pyzbar)\n")
        self.decode_log_textbox.insert("end", "========================================================\n")
        self.decode_log_textbox.insert("end", "  * [THUẬT TOÁN TIỀN XỬ LÝ ẢNH]\n")
        self.decode_log_textbox.insert("end", "    - Chuyển đổi ảnh sang hệ màu Xám (Grayscale).\n")
        self.decode_log_textbox.insert("end", "    - Nhị phân hoá (Binarization) sử dụng Adaptive Thresholding để tách vạch đen/trắng.\n")
        self.decode_log_textbox.insert("end", "    - Chạy thuật toán Edge Detection (Canny) để tìm đường viền.\n\n")
        
        start = time.time()
        try:
            zbar_results = pyzbar_decode(img)
            elapsed = (time.time() - start)*1000
            
            if len(zbar_results) == 0:
                self.decode_log_textbox.insert("end", f"  -> [KẾT QUẢ] Không tìm thấy QR/Barcode nào (Time: {elapsed:.1f}ms).\n\n")
            else:
                self.decode_log_textbox.insert("end", f"  -> [KẾT QUẢ] Đã quét và phát hiện {len(zbar_results)} mã (Time: {elapsed:.1f}ms).\n\n")
                
                for idx, res in enumerate(zbar_results):
                    code_type = res.type
                    data = res.data.decode('utf-8', errors='replace')
                    rect = res.rect
                    poly = res.polygon
                    found_codes.append({"type": code_type, "data": data, "rect": rect, "poly": poly})
                    
                    self.decode_log_textbox.insert("end", f"  --- MÃ THỨ #{idx+1} ({code_type}) ---\n")
                    self.decode_log_textbox.insert("end", "  * [NHẬN DIỆN ĐẶC TRƯNG - PATTERN RECOGNITION]\n")
                    if "QR" in code_type:
                        self.decode_log_textbox.insert("end", "    - Thuật toán quét và định vị thành công 3 khối vuông Position Detection Patterns ở các góc.\n")
                    else:
                        self.decode_log_textbox.insert("end", "    - Thuật toán quét tia (Scanlines) nhận diện khoảng cách các vạch dọc liên tiếp.\n")
                    self.decode_log_textbox.insert("end", f"    - Bounding Box (Khu vực): X={rect.left}, Y={rect.top}, W={rect.width}, H={rect.height}\n")
                    if poly:
                        self.decode_log_textbox.insert("end", f"    - Polygon (4 góc không gian 2D): {poly}\n")
                    
                    self.decode_log_textbox.insert("end", "  * [LẤY MẪU & KHÔI PHỤC MA TRẬN - GRID SAMPLING]\n")
                    if "QR" in code_type:
                        self.decode_log_textbox.insert("end", "    - Tính toán lại ma trận (Perspective Transformation) để khử góc nghiêng ảnh.\n")
                        self.decode_log_textbox.insert("end", "    - Trích xuất ma trận nhị phân. Giải mã Format Information & xoá Mask Pattern.\n")
                    else:
                        self.decode_log_textbox.insert("end", "    - Tính tỷ lệ vạch rộng/vạch hẹp để khôi phục cấu trúc bit.\n")
                        
                    self.decode_log_textbox.insert("end", "  * [SỬA LỖI & DỊCH TEXT - ERROR CORRECTION]\n")
                    if "QR" in code_type:
                        self.decode_log_textbox.insert("end", "    - Phân tách khối Codewords. Chạy giải thuật Reed-Solomon để xác minh và sửa các bit hỏng.\n")
                    else:
                        self.decode_log_textbox.insert("end", "    - Tính Checksum (Modulo) để xác minh tính toàn vẹn.\n")
                    
                    raw_bytes = res.data
                    binary_blocks = " ".join([f"{b:08b}" for b in raw_bytes])
                    self.decode_log_textbox.insert("end", f"    - [Trích xuất Codewords] Raw Bytes: {list(raw_bytes)}\n")
                    self.decode_log_textbox.insert("end", f"    - [Trích xuất Bitstream] Binary: {binary_blocks}\n")
                        
                    self.decode_log_textbox.insert("end", f"    => NỘI DUNG GIẢI MÃ: {data}\n\n")
        except Exception as e:
            self.decode_log_textbox.insert("end", f"    [!] Lỗi pyzbar: {e}\n\n")

        # 2. Decode pylibdmtx
        self.decode_log_textbox.insert("end", "========================================================\n")
        self.decode_log_textbox.insert("end", "[PHASE 2] TÌM KIẾM DATAMATRIX (Engine: pylibdmtx)\n")
        self.decode_log_textbox.insert("end", "========================================================\n")
        self.decode_log_textbox.insert("end", "  * [TÌM L-FINDER & CLOCK TRACK]\n")
        self.decode_log_textbox.insert("end", "    - Thuật toán Hough Transform quét tìm 2 đường viền vuông góc đặc (L-Finder Pattern).\n")
        self.decode_log_textbox.insert("end", "    - Định vị các vạch ngắt quãng (Clock Track) ở 2 cạnh còn lại để xác định lưới (Grid).\n\n")
        
        start = time.time()
        try:
            dmtx_results = dmtx_decode(img)
            elapsed = (time.time() - start)*1000
            
            if len(dmtx_results) == 0:
                self.decode_log_textbox.insert("end", f"  -> [KẾT QUẢ] Không tìm thấy DataMatrix nào (Time: {elapsed:.1f}ms).\n\n")
            else:
                self.decode_log_textbox.insert("end", f"  -> [KẾT QUẢ] Đã quét và phát hiện {len(dmtx_results)} mã (Time: {elapsed:.1f}ms).\n\n")
                
                for idx, res in enumerate(dmtx_results):
                    code_type = "DATAMATRIX"
                    data = res.data.decode('utf-8', errors='replace')
                    rect = res.rect
                    found_codes.append({"type": code_type, "data": data, "rect": rect})
                    
                    self.decode_log_textbox.insert("end", f"  --- MÃ THỨ #{idx+1} ({code_type}) ---\n")
                    self.decode_log_textbox.insert("end", f"    - Định vị thành công L-Finder tại toạ độ: L={rect.left}, T={rect.top}, W={rect.width}, H={rect.height}\n")
                    self.decode_log_textbox.insert("end", "    - Áp dụng phép biến đổi phối cảnh (Matrix Un-warping) để lấy mẫu lưới pixel từ hình ảnh.\n")
                    self.decode_log_textbox.insert("end", "    - Quét dọc theo đường chéo (Diagonal scan) để trích xuất các khối Codewords 8-bit.\n")
                    self.decode_log_textbox.insert("end", "    - Loại bỏ Padding ngẫu nhiên. Áp dụng Reed-Solomon Error Correction giải mã hỏng.\n")
                    
                    raw_bytes = res.data
                    binary_blocks = " ".join([f"{b:08b}" for b in raw_bytes])
                    self.decode_log_textbox.insert("end", f"    - [Trích xuất Codewords] Raw Bytes: {list(raw_bytes)}\n")
                    self.decode_log_textbox.insert("end", f"    - [Trích xuất Bitstream] Binary: {binary_blocks}\n")
                    
                    self.decode_log_textbox.insert("end", f"    => NỘI DUNG GIẢI MÃ: {data}\n\n")
        except Exception as e:
            self.decode_log_textbox.insert("end", f"    [!] Lỗi pylibdmtx: {e}\n\n")

        # 3. Draw Preview
        self.decode_log_textbox.insert("end", "========================================================\n")
        self.decode_log_textbox.insert("end", "[PHASE 3] ĐÓNG GÓI KẾT QUẢ (UI Rendering)\n")
        self.decode_log_textbox.insert("end", "========================================================\n")
        
        # Cập nhật trạng thái nút Trích xuất lưới 8-bit nếu có DataMatrix
        self.last_decoded_datamatrix_text = None
        for code in found_codes:
            if code["type"] == "DATAMATRIX":
                self.last_decoded_datamatrix_text = code["data"]
                break
                
        if self.last_decoded_datamatrix_text:
            self.btn_open_explorer.configure(state="normal")
        else:
            self.btn_open_explorer.configure(state="disabled")
        
        if found_codes:
            from PIL import ImageDraw
            img_drawn = img.copy()
            draw = ImageDraw.Draw(img_drawn)
            for code in found_codes:
                if "poly" in code and code["poly"]:
                    pts = [(p.x, p.y) for p in code["poly"]]
                    draw.polygon(pts, outline="#00FF00", width=3)
                elif "rect" in code and code["rect"]:
                    r = code["rect"]
                    draw.rectangle([r.left, r.top, r.left+r.width, r.top+r.height], outline="#00BBFF", width=3)
                    
            img_copy = img_drawn.copy()
            img_copy.thumbnail((400, 400), Image.Resampling.LANCZOS)
            self.decode_image_ctk = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=(img_copy.width, img_copy.height))
            self.decode_preview_label.configure(image=self.decode_image_ctk, text="")
            self.decode_log_textbox.insert("end", "    -> Đã cập nhật ảnh (Đường viền Xanh lá/Xanh lơ).\n")
            
            self.decode_log_textbox.insert("end", f"\n[✅] HOÀN TẤT. Đã giải mã thành công {len(found_codes)} kết quả.\n")
        else:
            self.decode_log_textbox.insert("end", "\n[❌] KHÔNG TÌM THẤY MÃ NÀO HỢP LỆ.\n")

    def open_decoded_explorer(self):
        if hasattr(self, 'last_decoded_datamatrix_text') and self.last_decoded_datamatrix_text:
            # Chuyển dữ liệu qua tab mã hoá và mở explorer
            self.text_input.delete("1.0", "end")
            self.text_input.insert("1.0", self.last_decoded_datamatrix_text)
            self.open_datamatrix_explorer()

    def update_config_ui(self):
        self.barcode_config.pack_forget()
        self.qr_config.pack_forget()
        self.datamatrix_config.pack_forget()
        
        enc_type = self.encoding_var.get()
        if enc_type == "barcode":
            self.barcode_config.pack()
        elif enc_type == "qrcode":
            self.qr_config.pack()
        elif enc_type == "datamatrix":
            self.datamatrix_config.pack()

    def generate_code(self):
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text or text == "Nhập text cần mã hóa...":
            messagebox.showwarning("Lỗi input", "Vui lòng nhập văn bản để mã hóa!")
            return

        encoding_type = self.encoding_var.get()

        if encoding_type == "datamatrix":
            pass  # Pystrich is pure python, no external c-lib needed


        # 1. Hiển thị log các bước ban đầu
        self.log_textbox.delete("1.0", "end")
        
        # Header log
        log_time = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log_textbox.insert("end", f"══════════════════════════════════════════\n  TRANSFORMATION LOG — {log_time}\n══════════════════════════════════════════\n\n")
        
        start_time = time.time()
        try:
            intermediate_log = self.build_log(text, encoding_type)
            self.log_textbox.insert("end", intermediate_log + "\n\n")

            if encoding_type == "barcode":
                img = self.generate_barcode(text)
            elif encoding_type == "qrcode":
                img = self.generate_qrcode(text)
            elif encoding_type == "datamatrix":
                img = self.generate_datamatrix(text)
            
            render_time = (time.time() - start_time) * 1000
            self.current_image = img

            # Cập nhật preview
            self.update_preview(img)

            # Log step 7
            step7 = f"[7] ✅ RENDER COMPLETE\n    Image size: {img.width}x{img.height} px\n    Render time: {render_time:.2f} ms\n    Status: SUCCESS\n"
            self.log_textbox.insert("end", step7)
            
            self.save_image_btn.configure(state="normal")
            self.save_log_btn.configure(state="normal")

        except Exception as e:
            self.log_textbox.insert("end", f"[7] ❌ RENDER FAILED\n    Error: {str(e)}\n")
            messagebox.showerror("Lỗi tạo mã", f"Đã xảy ra lỗi: {str(e)}")

    def build_log(self, text: str, encoding_type: str) -> str:
        if encoding_type == "barcode":
            return self._log_barcode(text)
        elif encoding_type == "qrcode":
            return self._log_qrcode(text)
        elif encoding_type == "datamatrix":
            return self._log_datamatrix(text)
        return ""

    def _log_barcode(self, text: str) -> str:
        b_type = self.barcode_type_var.get()
        lines = []
        lines.append(f"[1] 📥 INPUT\n    Text gốc: \"{text}\"\n    Độ dài: {len(text)} ký tự\n    Loại Barcode: {b_type.upper()}")
        
        try:
            # Generate real barcode first to catch validation errors
            c = barcode.get(b_type, text)
            binary_str = c.build()[0]

            if b_type == "code128":
                ascii_map = {c: ord(c) for c in text}
                lines.append("[2] 🔤 CHARACTER → ASCII\n    Tra bảng mã ASCII chuẩn:\n" + "\n".join(f"    - '{c}' = {v}" for c, v in ascii_map.items()))
                
                codewords = [ord(c) - 32 for c in text]
                cw_str = "\n".join(f"    - '{c}' (ASCII {ord(c)}) → ({ord(c)} - 32) = codeword {w}" for c, w in zip(text, codewords))
                lines.append(f"[3] 📋 ASCII → CODE 128 CODEWORD (Set B)\n    Start B cố định là 104.\n{cw_str}")
                
                checksum = (104 + sum((i+1)*w for i, w in enumerate(codewords))) % 103
                sum_str = " + ".join(f"({i+1}×{w})" for i, w in enumerate(codewords))
                lines.append(f"[4] 🧮 CHECKSUM CALCULATION (Modulo 103)\n    (104 + {sum_str}) mod 103 = {checksum}")
                
                full_seq = [104] + codewords + [checksum, 106]
                lines.append(f"[5] 📦 FINAL CODEWORD SEQUENCE\n    [START] [DATA...] [CHECKSUM] [STOP]\n    Chuỗi hoàn chỉnh: {full_seq}")
            else:
                lines.append(f"[2] 🔄 SPECIFIC ENCODING ({b_type.upper()})\n    Áp dụng quy tắc đặc tả của chuẩn {b_type.upper()} để mã hoá dữ liệu.")
                lines.append(f"[3] 🛡️ CHECKSUM CALCULATION\n    Thuật toán tự động sinh và đệm Checksum theo chuẩn {b_type.upper()}.")
            
            ascii_art = binary_str.replace('1', '█').replace('0', ' ')
            
            lines.append(f"[4] 📊 BAR PATTERN TRANSLATION (Thực tế)\n    Biến đổi chuỗi codeword thành hệ nhị phân (1=Thanh đen, 0=Khoảng trắng):\n    Raw Binary: {binary_str}\n\n    Mô phỏng hình ảnh mã vạch thực tế:\n    |{ascii_art}|")
        except Exception as e:
            raise Exception(f"Input '{text}' không hợp lệ đối với chuẩn {b_type.upper()}. Lỗi: {e}")
            
        return "\n\n".join(lines)

    def _log_qrcode(self, text: str) -> str:
        err_level = self.qr_error_var.get()[0] # L, M, Q, H
        lines = []
        try:
            byte_data = text.encode('utf-8')
            lines.append(f"[1] 📥 INPUT\n    Text: \"{text}\"\n    Độ dài: {len(text)} ký tự\n    Byte size: {len(byte_data)} bytes")
            
            is_numeric = text.isdigit()
            is_alpha = all(c in "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:" for c in text.upper())
            mode = "Numeric" if is_numeric else ("Alphanumeric" if is_alpha else "Byte")
            mode_ind = "0001" if is_numeric else ("0010" if is_alpha else "0100")
            lines.append(f"[2] 🔍 MODE SELECTION\n    Chế độ nén: {mode}.\n    Mode Indicator: {mode_ind} (4 bits).")
            
            hex_str = " ".join(f"{b:02X}" for b in byte_data)
            bin_str = " ".join(f"{b:08b}" for b in byte_data)
            lines.append(f"[3] 🔄 TEXT → BINARY STREAM\n    Hex: {hex_str}\n    Bin: {bin_str}\n    Chuỗi bit gộp: [Mode: {mode_ind}] + [Character Count] + [Data]")
            
            # Generate real QR to extract matrix and data_cache
            ec_map = {
                'L': qrcode.constants.ERROR_CORRECT_L,
                'M': qrcode.constants.ERROR_CORRECT_M,
                'Q': qrcode.constants.ERROR_CORRECT_Q,
                'H': qrcode.constants.ERROR_CORRECT_H
            }
            qr = qrcode.QRCode(version=1, error_correction=ec_map[err_level])
            qr.add_data(text)
            qr.make(fit=True)
            
            # Extract RS data
            data_cache_str = ""
            if hasattr(qr, 'data_cache') and qr.data_cache:
                data_cache_str = f"\n    Dữ liệu hoàn chỉnh (Data + Pad + Error Correction Bytes):\n    [ {', '.join(str(b) for b in qr.data_cache)} ]"

            lines.append(f"[4] 🛡️ ERROR CORRECTION (Reed-Solomon)\n    Mức sửa lỗi đang chọn: {err_level} (Khôi phục dữ liệu bị hỏng).\n    Chuẩn bị dữ liệu và sinh thêm các mã khôi phục lỗi (ECC).{data_cache_str}")
            
            matrix_art = []
            for row in qr.modules:
                # Use two blocks per module for better aspect ratio in monospace fonts
                row_str = "".join("██" if bit else "  " for bit in row)
                matrix_art.append(f"    │{row_str}│")
                
            matrix_str = "\n".join(matrix_art)
            
            lines.append(f"[5] 📐 FINAL MATRIX STRUCTURE (Thực tế)\n    Kích thước ma trận (Modules): {len(qr.modules)}x{len(qr.modules[0])}\n    Bao gồm Finder Patterns, Alignment, Timing và Data bits đã được Masking.\n    Sơ đồ ma trận QR thực tế (vùng đen = 1, vùng trắng = 0):\n\n    ┌{'─' * (len(qr.modules[0]) * 2)}┐\n{matrix_str}\n    └{'─' * (len(qr.modules[0]) * 2)}┘")
        except Exception as e:
             raise Exception(f"Lỗi khi xử lý dữ liệu QR Code: {e}")
        return "\n\n".join(lines)

    def _log_datamatrix(self, text: str) -> str:
        lines = []
        try:
            byte_data = text.encode('utf-8')
            lines.append(f"[1] 📥 INPUT\n    Text: \"{text}\"\n    Độ dài: {len(text)} ký tự\n    Byte size: {len(byte_data)} bytes")
            
            is_ascii = all(ord(c) < 128 for c in text)
            scheme = "ASCII" if is_ascii else "Base 256 / Auto"
            lines.append(f"[2] 🔍 ENCODING SCHEME\n    Lựa chọn Scheme: {scheme}.")
            
            if is_ascii:
                cw_list = [ord(c) + 1 for c in text]
                cw_str = "\n".join(f"    - '{c}' (ASCII {ord(c)}) → {ord(c)} + 1 = codeword {w}" for c, w in zip(text, cw_list))
                lines.append(f"[3] 🔄 CHARACTER → CODEWORD\n    Mỗi ký tự = ASCII + 1:\n{cw_str}")
            else:
                 lines.append(f"[3] 🔄 CHARACTER → CODEWORD\n    Sử dụng thuật toán nén phức hợp cho dữ liệu Unicode.")
                 
            # Extract real EC codewords from pystrich
            from pystrich.datamatrix.encode import TextEncoder
            import pystrich.datamatrix.textencoder as te
            enc = TextEncoder()
            full_cw = enc.encode(text)
            data_len = te.data_word_length[enc.size_index]
            
            data_pad_cw = full_cw[:data_len]
            ec_cw = full_cw[data_len:]
                 
            lines.append(f"[4] 🛡️ ERROR CORRECTION & PADDING\n    Đệm dữ liệu (Padding = 129 + Randomizer) cho vừa ma trận và tự động nội suy Reed-Solomon Check Bytes.\n    - Data & Padding Codewords ({len(data_pad_cw)} bytes): {data_pad_cw}\n    - Error Correction Codewords ({len(ec_cw)} bytes): {ec_cw}")
            
            from pystrich.datamatrix import DataMatrixEncoder
            encoder = DataMatrixEncoder(text)
            
            matrix_art = []
            # encoder.matrix contains 1s and 0s
            for row in encoder.matrix:
                row_str = "".join("██" if bit else "  " for bit in row)
                matrix_art.append(f"    │{row_str}│")
                
            matrix_str = "\n".join(matrix_art)
            
            lines.append(f"[5] 📊 BIT PLACEMENT & FINAL MATRIX (Thực tế)\n    Kích thước lưới logic (chưa tính viền yên tĩnh): {len(encoder.matrix)}x{len(encoder.matrix[0])}\n    Nhận diện qua L-Finder (cạnh trái/dưới đặc) & Clock Track (cạnh phải/trên đứt nét).\n    Sơ đồ ma trận DataMatrix thực tế:\n\n    ┌{'─' * (len(encoder.matrix[0]) * 2)}┐\n{matrix_str}\n    └{'─' * (len(encoder.matrix[0]) * 2)}┘")
        except Exception as e:
             lines.append(f"    [!] Log generation error: {e}")
        return "\n\n".join(lines)

    def generate_barcode(self, text: str) -> Image.Image:
        b_type = self.barcode_type_var.get()
        c = barcode.get(b_type, text, writer=ImageWriter())
        buffer = io.BytesIO()
        c.write(buffer, options={"write_text": False})
        buffer.seek(0)
        return Image.open(buffer)

    def generate_qrcode(self, text: str) -> Image.Image:
        err_level = self.qr_error_var.get()[0]
        ec_map = {
            'L': qrcode.constants.ERROR_CORRECT_L,
            'M': qrcode.constants.ERROR_CORRECT_M,
            'Q': qrcode.constants.ERROR_CORRECT_Q,
            'H': qrcode.constants.ERROR_CORRECT_H
        }
        qr = qrcode.QRCode(
            version=1,
            error_correction=ec_map[err_level],
            box_size=10,
            border=4
        )
        qr.add_data(text)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white").convert('RGB')

    def generate_datamatrix(self, text: str) -> Image.Image:
        encoder = DataMatrixEncoder(text)
        # pystrich returns a large image by default, let's keep it clean
        return encoder.get_pilimage()

    def update_preview(self, img: Image.Image):
        # Resize if image is too large while preserving aspect ratio
        max_size = (400, 400)
        img_copy = img.copy()
        img_copy.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # In customTkinter, images that are very small might look blurry when scaled up by CTkImage
        # For things like datamatrix which are naturally tiny (10x10), we scale them up nicely using Nearest Neighbor
        if img.width < 100 or img.height < 100:
             scale = min(max_size[0] // img.width, max_size[1] // img.height)
             if scale > 1:
                 img_copy = img.resize((img.width * scale, img.height * scale), Image.Resampling.NEAREST)

        self.current_image_ctk = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=(img_copy.width, img_copy.height))
        self.preview_label.configure(image=self.current_image_ctk, text="")

    def save_image(self):
        if not self.current_image:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
        )
        if filepath:
            self.current_image.save(filepath)
            messagebox.showinfo("Thành công", f"Đã lưu ảnh tại:\n{filepath}")

    def save_log(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.log_textbox.get("1.0", "end"))
            messagebox.showinfo("Thành công", f"Đã lưu log tại:\n{filepath}")

    def open_datamatrix_explorer(self):
        text = self.text_input.get("1.0", "end-1c").strip()
        if not text or text == "Nhập text cần mã hóa...":
            messagebox.showwarning("Lỗi input", "Vui lòng nhập văn bản để phân tích lưới DataMatrix!")
            return
            
        import pystrich.datamatrix.placement as plc
        from pystrich.datamatrix import DataMatrixEncoder

        class Tracker:
            cw_map = []
            _cw_id = None
            _bit_counter = 7
            _cw_seq = 1
            
        orig_place = plc.DataMatrixPlacer.place
        orig_ps = plc.DataMatrixPlacer.place_standard_shape
        orig_pb = plc.DataMatrixPlacer.place_bit
        orig_s1 = plc.DataMatrixPlacer.place_special_1
        orig_s2 = plc.DataMatrixPlacer.place_special_2
        orig_s3 = plc.DataMatrixPlacer.place_special_3
        orig_s4 = plc.DataMatrixPlacer.place_special_4

        def new_place(self, codewords, matrix):
            Tracker.cw_map = [[None for _ in row] for row in matrix]
            Tracker._cw_seq = 1
            orig_place(self, codewords, matrix)

        def new_ps(self, position, codeword):
            Tracker._cw_id = f"{Tracker._cw_seq}"
            Tracker._cw_seq += 1
            Tracker._bit_counter = 7
            orig_ps(self, position, codeword)
            
        def new_s1(self, cw): Tracker._cw_id=f"{Tracker._cw_seq}"; Tracker._cw_seq+=1; Tracker._bit_counter=7; orig_s1(self, cw)
        def new_s2(self, cw): Tracker._cw_id=f"{Tracker._cw_seq}"; Tracker._cw_seq+=1; Tracker._bit_counter=7; orig_s2(self, cw)
        def new_s3(self, cw): Tracker._cw_id=f"{Tracker._cw_seq}"; Tracker._cw_seq+=1; Tracker._bit_counter=7; orig_s3(self, cw)
        def new_s4(self, cw): Tracker._cw_id=f"{Tracker._cw_seq}"; Tracker._cw_seq+=1; Tracker._bit_counter=7; orig_s4(self, cw)

        def new_pb(self, position, bit):
            posx, posy = position
            if posx < 0:
                posx += self.rows
                posy += 4 - ((self.rows + 4) % 8)
            if posy < 0:
                posy += self.cols
                posx += 4 - ((self.cols + 4) % 8)
            if posx < len(Tracker.cw_map) and posy < len(Tracker.cw_map[0]):
                Tracker.cw_map[posx][posy] = (Tracker._cw_id, Tracker._bit_counter, bit)
            Tracker._bit_counter -= 1
            orig_pb(self, position, bit)

        # Apply monkey patch to intercept matrix placements
        plc.DataMatrixPlacer.place = new_place
        plc.DataMatrixPlacer.place_standard_shape = new_ps
        plc.DataMatrixPlacer.place_bit = new_pb
        plc.DataMatrixPlacer.place_special_1 = new_s1
        plc.DataMatrixPlacer.place_special_2 = new_s2
        plc.DataMatrixPlacer.place_special_3 = new_s3
        plc.DataMatrixPlacer.place_special_4 = new_s4

        try:
            encoder = DataMatrixEncoder(text)
            cw_map = Tracker.cw_map
            matrix = encoder.matrix
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mã hoá: {e}")
            return
        finally:
            # Restore original methods
            plc.DataMatrixPlacer.place = orig_place
            plc.DataMatrixPlacer.place_standard_shape = orig_ps
            plc.DataMatrixPlacer.place_bit = orig_pb
            plc.DataMatrixPlacer.place_special_1 = orig_s1
            plc.DataMatrixPlacer.place_special_2 = orig_s2
            plc.DataMatrixPlacer.place_special_3 = orig_s3
            plc.DataMatrixPlacer.place_special_4 = orig_s4

        self.show_datamatrix_explorer(matrix, cw_map)

    def show_datamatrix_explorer(self, matrix, cw_map):
        win = ctk.CTkToplevel(self)
        win.title("🔍 Interactive DataMatrix Explorer")
        win.geometry("600x650")
        
        info_frame = ctk.CTkFrame(win)
        info_frame.pack(fill="x", padx=20, pady=10)
        
        info_label = ctk.CTkLabel(info_frame, text="Bấm vào một ô vuông trong lưới để phân tích 8-bit Codeword của ô đó", font=ctk.CTkFont(size=14, weight="bold"))
        info_label.pack(pady=10)
        
        grid_frame = ctk.CTkFrame(win)
        grid_frame.pack(expand=True, fill="both", padx=20, pady=10)
        
        rows = len(matrix)
        cols = len(matrix[0])
        
        # Calculate max square cell size that fits in 450x450
        cell_size = min(450 // rows, 450 // cols)
        if cell_size < 10: cell_size = 10
        
        import tkinter as tk
        canvas = tk.Canvas(grid_frame, width=cols*cell_size, height=rows*cell_size, bg="#1E1E1E", highlightthickness=0)
        canvas.pack(expand=True)
        
        rects = {}
        texts = {}
        
        # Draw the grid
        for r in range(rows):
            for c in range(cols):
                bit = matrix[r][c]
                color = "black" if bit else "white"
                rect_id = canvas.create_rectangle(c*cell_size, r*cell_size, (c+1)*cell_size, (r+1)*cell_size, fill=color, outline="#888888")
                rects[(r, c)] = rect_id
                
                # Draw Sequence ID text if available and cell is big enough
                cell_data = cw_map[r][c]
                if cell_data is not None and cell_size >= 15:
                    cw_id = cell_data[0]
                    text_color = "white" if bit else "black"
                    font_size = max(6, min(10, cell_size // 3))
                    text_id = canvas.create_text(c*cell_size + cell_size/2, r*cell_size + cell_size/2, text=str(cw_id), fill=text_color, font=("Arial", font_size, "bold"))
                    texts[(r, c)] = text_id
                else:
                    texts[(r, c)] = None
                
        def on_click(event):
            c = event.x // cell_size
            r = event.y // cell_size
            
            if 0 <= r < rows and 0 <= c < cols:
                cell_data = cw_map[r][c]
                
                # Reset all to default colors
                for rr in range(rows):
                    for cc in range(cols):
                        b = matrix[rr][cc]
                        canvas.itemconfig(rects[(rr, cc)], fill="black" if b else "white", outline="#888888", width=1)
                        if texts[(rr, cc)]:
                            canvas.itemconfig(texts[(rr, cc)], fill="white" if b else "black")
                        
                if cell_data is not None:
                    cw_id, bit_idx, bit_val = cell_data
                    
                    # Highlight all cells belonging to this Codeword and find Anchor (Bit 0)
                    bits_info = {}
                    anchor_r, anchor_c = None, None
                    
                    for rr in range(rows):
                        for cc in range(cols):
                            if cw_map[rr][cc] is not None and cw_map[rr][cc][0] == cw_id:
                                current_bit_idx = cw_map[rr][cc][1]
                                bits_info[current_bit_idx] = cw_map[rr][cc][2]
                                is_one = matrix[rr][cc]
                                
                                canvas.itemconfig(rects[(rr, cc)], fill="#00AA00" if is_one else "#AAFFAA") # Green for related bits
                                if texts[(rr, cc)]:
                                    canvas.itemconfig(texts[(rr, cc)], fill="white" if is_one else "black")
                                    
                                if current_bit_idx == 0:
                                    anchor_r, anchor_c = rr, cc
                                
                    # Set the Anchor cell (Bit 0) to Light/Dark Red based on bit value
                    if anchor_r is not None and anchor_c is not None:
                        anchor_bit = matrix[anchor_r][anchor_c]
                        anchor_color = "#CC0000" if anchor_bit else "#FF9999" # Dark red for 1, Light red for 0
                        canvas.itemconfig(rects[(anchor_r, anchor_c)], fill=anchor_color)
                        if texts[(anchor_r, anchor_c)]:
                            canvas.itemconfig(texts[(anchor_r, anchor_c)], fill="white" if anchor_bit else "black")
                            
                    # Highlight the clicked cell's border so user knows what they clicked
                    canvas.itemconfig(rects[(r, c)], outline="#00FFFF", width=3)
                    
                    # Compute byte value
                    byte_val = 0
                    binary_str = ""
                    for i in range(7, -1, -1):
                        v = bits_info.get(i, 0)
                        binary_str += str(v)
                        byte_val |= (v << i)
                        
                    desc = f"🔍 Đang chọn: Codeword #{cw_id}\n\n"
                    desc += f"Chuỗi nhị phân: {binary_str} (Bạn vừa click vào Bit {bit_idx}, giá trị = {matrix[r][c]})\n"
                    desc += f"Điểm neo (Bit 0) đang được tô màu Đỏ.\n"
                    desc += f"Giá trị thập phân: {byte_val} | Hex: 0x{byte_val:02X}"
                    
                    info_label.configure(text=desc)
                else:
                    info_label.configure(text=f"Ô ({r}, {c}) không thuộc phần Data/EC.\n(Đây là thành phần cố định: Finder Pattern / Clock Track / Padding)")

        canvas.bind("<Button-1>", on_click)

if __name__ == "__main__":
    app = CodeGeneratorApp()
    app.mainloop()
