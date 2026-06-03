import os
import customtkinter as ctk

# Cấu hình UI chuyên nghiệp
FONT_TITLE = ("Roboto", 16, "bold")
FONT_NORMAL = ("Roboto", 14)
FONT_CODE = ("Consolas", 13)
ACCENT_COLOR = "#0EA5E9" 
CARD_BG = "#27272A"

def setup_encode_tab(parent, app):
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_columnconfigure(1, weight=1)
    parent.grid_rowconfigure(1, weight=1)

    # Input Section (Card)
    input_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=CARD_BG)
    input_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=(0, 15), sticky="ew")
    input_frame.grid_columnconfigure(0, weight=1)

    app.text_input = ctk.CTkTextbox(input_frame, height=80, font=FONT_NORMAL, corner_radius=8, border_width=1, border_color="#3F3F46", fg_color="#18181B")
    app.text_input.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
    app.text_input.insert("1.0", "Nhập text cần mã hóa...")
    app.text_input.bind("<Button-1>", lambda e: app.text_input.delete("1.0", "end") if app.text_input.get("1.0", "end-1c") == "Nhập text cần mã hóa..." else None)

    # Segmented Button (Animated)
    app.encoding_var = ctk.StringVar(value="barcode")
    app.seg_button = ctk.CTkSegmentedButton(input_frame, variable=app.encoding_var, values=["barcode", "qrcode", "datamatrix"], font=FONT_NORMAL, command=app.update_config_ui, selected_color=ACCENT_COLOR, selected_hover_color="#0284C7")
    app.seg_button.grid(row=1, column=0, padx=20, pady=10)
    # Ghi đè label hiển thị (ctksegmentedbutton không support text alias natively, ta sửa label trực tiếp)
    # Do CTkSegmentedButton values là giá trị thật luôn, nên ta dùng dictionary ánh xạ ở main, hoặc dùng value tiếng anh.
    # Để đẹp, ta dùng ["Mã vạch 1D", "QR Code 2D", "DataMatrix 2D"]
    app.encoding_var.set("Mã vạch 1D")
    app.seg_button.configure(values=["Mã vạch 1D", "QR Code 2D", "DataMatrix 2D"])

    # Config Frame
    app.config_frame = ctk.CTkFrame(input_frame, fg_color="#18181B", corner_radius=8)
    app.config_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

    # Barcode Config
    app.barcode_config = ctk.CTkFrame(app.config_frame, fg_color="transparent")
    ctk.CTkLabel(app.barcode_config, text="Loại Barcode:", font=FONT_NORMAL).pack(side="left", padx=10, pady=10)
    app.barcode_type_var = ctk.StringVar(value="code128")
    app.barcode_dropdown = ctk.CTkOptionMenu(app.barcode_config, variable=app.barcode_type_var, values=["code128", "code39", "ean13"], font=FONT_NORMAL, fg_color=CARD_BG, button_color=CARD_BG, button_hover_color="#3F3F46")
    app.barcode_dropdown.pack(side="left", padx=10)

    # QR Config
    app.qr_config = ctk.CTkFrame(app.config_frame, fg_color="transparent")
    ctk.CTkLabel(app.qr_config, text="Mức sửa lỗi (ECC):", font=FONT_NORMAL).pack(side="left", padx=10, pady=10)
    app.qr_error_var = ctk.StringVar(value="M (15%)")
    app.qr_dropdown = ctk.CTkOptionMenu(app.qr_config, variable=app.qr_error_var, values=["L (7%)", "M (15%)", "Q (25%)", "H (30%)"], font=FONT_NORMAL, fg_color=CARD_BG, button_color=CARD_BG, button_hover_color="#3F3F46")
    app.qr_dropdown.pack(side="left", padx=10)
    
    app.qr_explorer_btn = ctk.CTkButton(app.qr_config, text="🔍 Khám phá Masking", font=FONT_NORMAL, command=app.open_qr_explorer, fg_color="#8B5CF6", hover_color="#7C3AED")
    app.qr_explorer_btn.pack(side="left", padx=20)

    # DataMatrix Config
    app.datamatrix_config = ctk.CTkFrame(app.config_frame, fg_color="transparent")
    app.explorer_btn = ctk.CTkButton(app.datamatrix_config, text="🔍 Khám phá Snake Path", font=FONT_NORMAL, command=app.open_datamatrix_explorer, fg_color="#8B5CF6", hover_color="#7C3AED")
    app.explorer_btn.pack(side="left", padx=10, pady=10)

    # Thay vì check biến "barcode" cũ, ta tạo wrapper để map biến
    def custom_update_config_ui(value):
        app.barcode_config.pack_forget()
        app.qr_config.pack_forget()
        app.datamatrix_config.pack_forget()
        if value == "Mã vạch 1D":
            app.barcode_config.pack(side="left", fill="x", expand=True)
            app.encoding_var_mapped = "barcode"
        elif value == "QR Code 2D":
            app.qr_config.pack(side="left", fill="x", expand=True)
            app.encoding_var_mapped = "qrcode"
        elif value == "DataMatrix 2D":
            app.datamatrix_config.pack(side="left", fill="x", expand=True)
            app.encoding_var_mapped = "datamatrix"
            
    app.update_config_ui = custom_update_config_ui
    app.seg_button.configure(command=app.update_config_ui)
    app.update_config_ui("Mã vạch 1D")
    
    # Overwrite generate_code in main app to use app.encoding_var_mapped instead
    orig_generate_code = app.generate_code
    def mapped_generate_code():
        # Temporarily mock the stringvar to return mapped value for original method
        old_get = app.encoding_var.get
        app.encoding_var.get = lambda: getattr(app, "encoding_var_mapped", "barcode")
        orig_generate_code()
        app.encoding_var.get = old_get
    app.generate_code = mapped_generate_code

    app.generate_btn = ctk.CTkButton(input_frame, text="⚡ TẠO MÃ NGAY", font=("Roboto", 16, "bold"), command=app.generate_code, height=50, fg_color=ACCENT_COLOR, hover_color="#0284C7")
    app.generate_btn.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

    # Log Panel
    log_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=CARD_BG)
    log_frame.grid(row=1, column=0, padx=(0, 7.5), pady=0, sticky="nsew")
    log_frame.grid_rowconfigure(1, weight=1)
    log_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(log_frame, text="📋 Nhật Ký Mã Hoá", font=FONT_TITLE).grid(row=0, column=0, pady=10)
    app.log_textbox = ctk.CTkTextbox(log_frame, font=FONT_CODE, corner_radius=8, fg_color="#18181B", border_width=1, border_color="#3F3F46")
    app.log_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

    # Preview Panel
    preview_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=CARD_BG)
    preview_frame.grid(row=1, column=1, padx=(7.5, 0), pady=0, sticky="nsew")
    preview_frame.grid_rowconfigure(1, weight=1)
    preview_frame.grid_columnconfigure(0, weight=1)
    preview_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(preview_frame, text="🖼️ Hình Ảnh Kết Quả", font=FONT_TITLE).grid(row=0, column=0, columnspan=2, pady=10)
    
    app.preview_label = ctk.CTkLabel(preview_frame, text="[Ảnh sẽ xuất hiện ở đây]", font=FONT_NORMAL, fg_color="#18181B", corner_radius=8)
    app.preview_label.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 15), sticky="nsew")

    app.save_image_btn = ctk.CTkButton(preview_frame, text="💾 Lưu Ảnh", font=FONT_NORMAL, command=app.save_image, state="disabled", fg_color="#3F3F46", hover_color="#52525B")
    app.save_image_btn.grid(row=2, column=0, padx=(15, 7.5), pady=(0, 15), sticky="ew")

    app.save_log_btn = ctk.CTkButton(preview_frame, text="📄 Lưu Log", font=FONT_NORMAL, command=app.save_log, state="disabled", fg_color="#3F3F46", hover_color="#52525B")
    app.save_log_btn.grid(row=2, column=1, padx=(7.5, 15), pady=(0, 15), sticky="ew")


def setup_decode_tab(parent, app):
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_columnconfigure(1, weight=1)
    parent.grid_rowconfigure(1, weight=1)

    control_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=CARD_BG)
    control_frame.grid(row=0, column=0, columnspan=2, padx=0, pady=(0, 15), sticky="ew")
    
    app.btn_load_image = ctk.CTkButton(control_frame, text="🖼️ Tải Ảnh Lên", font=FONT_NORMAL, command=app.load_decode_image, height=40, fg_color="#3F3F46", hover_color="#52525B")
    app.btn_load_image.pack(side="left", padx=20, pady=15)
    
    app.btn_run_decode = ctk.CTkButton(control_frame, text="🔍 GIẢI MÃ TỰ ĐỘNG", font=("Roboto", 14, "bold"), command=app.run_decode, fg_color=ACCENT_COLOR, hover_color="#0284C7", state="disabled", height=40)
    app.btn_run_decode.pack(side="left", padx=10, pady=15)
    
    app.btn_open_explorer = ctk.CTkButton(control_frame, text="🧩 Trích xuất lưới", font=FONT_NORMAL, command=app.open_decoded_explorer, fg_color="#D97706", hover_color="#B45309", state="disabled", height=40)
    app.btn_open_explorer.pack(side="right", padx=20, pady=15)
    
    log_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=CARD_BG)
    log_frame.grid(row=1, column=0, padx=(0, 7.5), pady=0, sticky="nsew")
    log_frame.grid_rowconfigure(1, weight=1)
    log_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(log_frame, text="📋 Kết quả Dịch", font=FONT_TITLE).grid(row=0, column=0, pady=10)
    app.decode_log_textbox = ctk.CTkTextbox(log_frame, font=FONT_CODE, corner_radius=8, fg_color="#18181B", border_width=1, border_color="#3F3F46")
    app.decode_log_textbox.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
    
    preview_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=CARD_BG)
    preview_frame.grid(row=1, column=1, padx=(7.5, 0), pady=0, sticky="nsew")
    preview_frame.grid_rowconfigure(1, weight=1)
    preview_frame.grid_columnconfigure(0, weight=1)
    
    ctk.CTkLabel(preview_frame, text="🖼️ Khu vực Ảnh", font=FONT_TITLE).grid(row=0, column=0, pady=10)
    app.decode_preview_label = ctk.CTkLabel(preview_frame, text="[Chưa tải ảnh]", font=FONT_NORMAL, fg_color="#18181B", corner_radius=8)
    app.decode_preview_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")


def setup_doc_tab(parent, app):
    parent.grid_rowconfigure(0, weight=1)
    parent.grid_columnconfigure(1, weight=1)

    sidebar_frame = ctk.CTkFrame(parent, width=220, corner_radius=12, fg_color=CARD_BG)
    sidebar_frame.grid(row=0, column=0, padx=(0, 15), pady=0, sticky="nsew")
    
    content_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=CARD_BG)
    content_frame.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")
    content_frame.grid_rowconfigure(0, weight=1)
    content_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(sidebar_frame, text="DANH MỤC TÀI LIỆU", font=FONT_TITLE, text_color="#A1A1AA").pack(pady=(20, 10))

    doc_textbox = ctk.CTkTextbox(content_frame, font=FONT_CODE, corner_radius=8, wrap="word", fg_color="#18181B", border_width=1, border_color="#3F3F46")
    doc_textbox.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
    
    app.doc_images = []
    app.doc_buttons = []
    
    def load_doc(filename, active_btn):
        for btn in app.doc_buttons:
            btn.configure(fg_color="transparent")
        active_btn.configure(fg_color="#3F3F46")
        
        try:
            path = os.path.join(os.path.dirname(__file__), "..", "docs", filename)
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            doc_textbox.configure(state="normal")
            doc_textbox.delete("1.0", "end")
            app.doc_images.clear()
            
            from PIL import Image
            
            for line in lines:
                if line.strip().startswith("[IMAGE:") and line.strip().endswith("]"):
                    img_name = line.strip()[7:-1].strip()
                    img_path = os.path.join(os.path.dirname(__file__), "..", "docs", "images", img_name)
                    if os.path.exists(img_path):
                        img = Image.open(img_path)
                        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
                        lbl = ctk.CTkLabel(doc_textbox, text="", image=ctk_img, fg_color="transparent")
                        app.doc_images.append(ctk_img)
                        app.doc_images.append(lbl)
                        
                        doc_textbox.insert("end", "\n")
                        doc_textbox._textbox.window_create("end", window=lbl)
                        doc_textbox.insert("end", "\n\n")
                    else:
                        doc_textbox.insert("end", f"[Lỗi tải ảnh: {img_name}]\n")
                else:
                    doc_textbox.insert("end", line)
                    
            doc_textbox.configure(state="disabled")
        except Exception as e:
            doc_textbox.configure(state="normal")
            doc_textbox.delete("1.0", "end")
            doc_textbox.insert("end", f"Lỗi không thể tải tài liệu: {str(e)}")
            doc_textbox.configure(state="disabled")

    btn1 = ctk.CTkButton(sidebar_frame, text="1. Mã Vạch 1D", font=FONT_NORMAL, fg_color="transparent", hover_color="#3F3F46", anchor="w", command=lambda: load_doc("1_barcode.txt", btn1))
    btn1.pack(pady=5, padx=15, fill="x")
    app.doc_buttons.append(btn1)
    
    btn2 = ctk.CTkButton(sidebar_frame, text="2. Cấu trúc QR Code", font=FONT_NORMAL, fg_color="transparent", hover_color="#3F3F46", anchor="w", command=lambda: load_doc("2_qrcode.txt", btn2))
    btn2.pack(pady=5, padx=15, fill="x")
    app.doc_buttons.append(btn2)
    
    btn3 = ctk.CTkButton(sidebar_frame, text="3. Mask Pattern QR", font=FONT_NORMAL, fg_color="transparent", hover_color="#3F3F46", anchor="w", command=lambda: load_doc("3_qr_mask.txt", btn3))
    btn3.pack(pady=5, padx=15, fill="x")
    app.doc_buttons.append(btn3)
    
    btn4 = ctk.CTkButton(sidebar_frame, text="4. Cấu trúc DataMatrix", font=FONT_NORMAL, fg_color="transparent", hover_color="#3F3F46", anchor="w", command=lambda: load_doc("4_datamatrix.txt", btn4))
    btn4.pack(pady=5, padx=15, fill="x")
    app.doc_buttons.append(btn4)

    load_doc("1_barcode.txt", btn1)

def setup_process_tab(parent, app):
    parent.grid_columnconfigure(0, weight=1, minsize=350)
    parent.grid_columnconfigure(1, weight=2)
    parent.grid_rowconfigure(0, weight=1)

    # 1. Control Panel (Left)
    control_frame = ctk.CTkScrollableFrame(parent, corner_radius=12, fg_color=CARD_BG)
    control_frame.grid(row=0, column=0, padx=(0, 7.5), pady=0, sticky="nsew")

    ctk.CTkLabel(control_frame, text="Tải Ảnh Lên", font=FONT_TITLE).pack(pady=(10, 5), anchor="w", padx=10)
    app.btn_process_load = ctk.CTkButton(control_frame, text="🖼️ Tải Ảnh Mới", font=FONT_NORMAL, command=app.load_process_image, fg_color="#3F3F46", hover_color="#52525B")
    app.btn_process_load.pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(control_frame, text="1. Màu Sắc & Tương Phản", font=FONT_TITLE, text_color=ACCENT_COLOR).pack(pady=(20, 5), anchor="w", padx=10)
    
    app.proc_invert_var = ctk.BooleanVar(value=False)
    ctk.CTkSwitch(control_frame, text="Invert Colors (Đảo màu)", variable=app.proc_invert_var, command=app.update_processed_preview, font=FONT_NORMAL).pack(pady=5, padx=10, anchor="w")
    
    app.proc_gray_var = ctk.BooleanVar(value=False)
    ctk.CTkSwitch(control_frame, text="Grayscale (Ảnh xám)", variable=app.proc_gray_var, command=app.update_processed_preview, font=FONT_NORMAL).pack(pady=5, padx=10, anchor="w")

    ctk.CTkLabel(control_frame, text="Brightness (Độ sáng)", font=FONT_NORMAL).pack(anchor="w", padx=10, pady=(10, 0))
    app.proc_brightness_var = ctk.DoubleVar(value=0)
    ctk.CTkSlider(control_frame, from_=-100, to=100, variable=app.proc_brightness_var, command=lambda e: app.update_processed_preview()).pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(control_frame, text="Contrast (Độ tương phản)", font=FONT_NORMAL).pack(anchor="w", padx=10)
    app.proc_contrast_var = ctk.DoubleVar(value=1.0)
    ctk.CTkSlider(control_frame, from_=0.1, to=3.0, variable=app.proc_contrast_var, command=lambda e: app.update_processed_preview()).pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(control_frame, text="2. Làm Mờ / Làm Nét", font=FONT_TITLE, text_color=ACCENT_COLOR).pack(pady=(20, 5), anchor="w", padx=10)
    app.proc_sharpen_var = ctk.BooleanVar(value=False)
    ctk.CTkSwitch(control_frame, text="Sharpen (Làm nét)", variable=app.proc_sharpen_var, command=app.update_processed_preview, font=FONT_NORMAL).pack(pady=5, padx=10, anchor="w")

    ctk.CTkLabel(control_frame, text="Blur Kernel Size", font=FONT_NORMAL).pack(anchor="w", padx=10, pady=(10, 0))
    app.proc_blur_var = ctk.IntVar(value=1)
    ctk.CTkSlider(control_frame, from_=1, to=9, number_of_steps=4, variable=app.proc_blur_var, command=lambda e: app.update_processed_preview()).pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(control_frame, text="3. Thresholding (Nhị phân)", font=FONT_TITLE, text_color=ACCENT_COLOR).pack(pady=(20, 5), anchor="w", padx=10)
    app.proc_thresh_type_var = ctk.StringVar(value="None")
    ctk.CTkOptionMenu(control_frame, variable=app.proc_thresh_type_var, values=["None", "Simple", "Adaptive"], command=lambda e: app.update_processed_preview(), font=FONT_NORMAL).pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(control_frame, text="Simple Threshold (Ngưỡng)", font=FONT_NORMAL).pack(anchor="w", padx=10)
    app.proc_thresh_val_var = ctk.IntVar(value=127)
    ctk.CTkSlider(control_frame, from_=0, to=255, variable=app.proc_thresh_val_var, command=lambda e: app.update_processed_preview()).pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(control_frame, text="Adaptive Block Size", font=FONT_NORMAL).pack(anchor="w", padx=10)
    app.proc_adaptive_block_var = ctk.IntVar(value=11)
    ctk.CTkSlider(control_frame, from_=3, to=99, number_of_steps=48, variable=app.proc_adaptive_block_var, command=lambda e: app.update_processed_preview()).pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(control_frame, text="Adaptive C", font=FONT_NORMAL).pack(anchor="w", padx=10)
    app.proc_adaptive_c_var = ctk.IntVar(value=2)
    ctk.CTkSlider(control_frame, from_=0, to=20, variable=app.proc_adaptive_c_var, command=lambda e: app.update_processed_preview()).pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(control_frame, text="4. Morphology (Hình thái học)", font=FONT_TITLE, text_color=ACCENT_COLOR).pack(pady=(20, 5), anchor="w", padx=10)
    app.proc_morph_type_var = ctk.StringVar(value="None")
    ctk.CTkOptionMenu(control_frame, variable=app.proc_morph_type_var, values=["None", "Dilation", "Erosion", "Open (Xóa nhiễu trắng)", "Close (Nối nét đứt)"], command=lambda e: app.update_processed_preview(), font=FONT_NORMAL).pack(pady=5, padx=10, fill="x")

    ctk.CTkLabel(control_frame, text="Số lần lặp (Iterations)", font=FONT_NORMAL).pack(anchor="w", padx=10)
    app.proc_morph_iter_var = ctk.IntVar(value=1)
    ctk.CTkSlider(control_frame, from_=1, to=5, number_of_steps=4, variable=app.proc_morph_iter_var, command=lambda e: app.update_processed_preview()).pack(pady=5, padx=10, fill="x")

    # 2. Preview Panel (Right)
    preview_frame = ctk.CTkFrame(parent, corner_radius=12, fg_color=CARD_BG)
    preview_frame.grid(row=0, column=1, padx=(7.5, 0), pady=0, sticky="nsew")
    preview_frame.grid_rowconfigure(1, weight=1)
    preview_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(preview_frame, text="🖼️ Ảnh Trước Khi Giải Mã", font=FONT_TITLE).grid(row=0, column=0, pady=10)
    
    app.process_preview_label = ctk.CTkLabel(preview_frame, text="[Vui lòng tải ảnh lên]", font=FONT_NORMAL, fg_color="#18181B", corner_radius=8)
    app.process_preview_label.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")

    app.btn_send_decode = ctk.CTkButton(preview_frame, text="🚀 CHUYỂN SANG GIẢI MÃ", font=("Roboto", 16, "bold"), command=app.send_to_decode, state="disabled", height=50, fg_color=ACCENT_COLOR, hover_color="#0284C7")
    app.btn_send_decode.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="ew")
