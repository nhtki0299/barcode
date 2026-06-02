import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

def open_qr_explorer(text: str, error_val: str, parent=None):
    if not text or text == "Nhập text cần mã hóa...":
        messagebox.showwarning("Lỗi", "Vui lòng nhập text!")
        return

    import qrcode
    import qrcode.util
    
    orig_map_data = qrcode.QRCode.map_data
    
    class Tracker:
        cw_map = []
        cw_anchors = {}
        data_cache = []
        
    def new_map_data(self, data, mask_pattern):
        Tracker.data_cache = data
        Tracker.cw_map = [[None for _ in row] for row in self.modules]
        
        inc = -1
        row = self.modules_count - 1
        bitIndex = 7
        byteIndex = 0
        
        mask_func = qrcode.util.mask_func(mask_pattern)
        data_len = len(data)
        
        for col in range(self.modules_count - 1, 0, -2):
            if col <= 6:
                col -= 1
                
            col_range = (col, col - 1)
            
            while True:
                for c in col_range:
                    if self.modules[row][c] is None:
                        if byteIndex < data_len:
                            raw_bit = ((data[byteIndex] >> bitIndex) & 1) == 1
                            Tracker.cw_map[row][c] = (byteIndex + 1, bitIndex, int(raw_bit))
                            
                            if bitIndex == 7:
                                Tracker.cw_anchors[byteIndex + 1] = (row, c)
                        
                        bitIndex -= 1
                        if bitIndex == -1:
                            byteIndex += 1
                            bitIndex = 7
                            
                row += inc
                if row < 0 or self.modules_count <= row:
                    row -= inc
                    inc = -inc
                    break
                    
        orig_map_data(self, data, mask_pattern)
        
    qrcode.QRCode.map_data = new_map_data
    
    try:
        error_dict = {"L": qrcode.constants.ERROR_CORRECT_L, "M": qrcode.constants.ERROR_CORRECT_M, "Q": qrcode.constants.ERROR_CORRECT_Q, "H": qrcode.constants.ERROR_CORRECT_H}
        # In the original app.py, error_val was like 'M (15%)', so we take the first char
        error_val_char = error_val[0] if error_val else "M"
        
        qr = qrcode.QRCode(error_correction=error_dict.get(error_val_char, qrcode.constants.ERROR_CORRECT_M), border=0)
        qr.add_data(text)
        qr.make(fit=True)
        
        import qrcode.base
        rs_blocks = qrcode.base.rs_blocks(qr.version, qr.error_correction)
        data_len = sum(block.data_count for block in rs_blocks)
        
        show_qr_explorer(qr.modules, Tracker.cw_map, data_len, Tracker.cw_anchors, Tracker.data_cache, parent)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")
    finally:
        qrcode.QRCode.map_data = orig_map_data

def show_qr_explorer(matrix, cw_map, data_len, cw_anchors, data_cache, parent):
    win = ctk.CTkToplevel(parent)
    win.title("🔍 Interactive QR Code Explorer")
    win.geometry("650x700")
    
    info_frame = ctk.CTkFrame(win)
    info_frame.pack(fill="x", padx=20, pady=10)
    
    info_label = ctk.CTkLabel(info_frame, text="Bấm vào một ô vuông trong lưới để phân tích Codeword", font=ctk.CTkFont(size=14, weight="bold"))
    info_label.pack(pady=10)
    
    grid_frame = ctk.CTkFrame(win)
    grid_frame.pack(expand=True, fill="both", padx=20, pady=10)
    
    orig_rows = len(matrix)
    orig_cols = len(matrix[0])
    
    offset = 4
    rows = orig_rows + 2 * offset
    cols = orig_cols + 2 * offset
    
    new_matrix = []
    new_cw_map = []
    for r in range(rows):
        new_matrix.append([False] * cols)
        new_cw_map.append([None] * cols)
        
    for r in range(orig_rows):
        for c in range(orig_cols):
            new_matrix[r+offset][c+offset] = matrix[r][c]
            new_cw_map[r+offset][c+offset] = cw_map[r][c]
            
    matrix = new_matrix
    cw_map = new_cw_map
    
    anchors = {}
    for cw_id, (r, c) in cw_anchors.items():
        anchors[cw_id] = (r + offset, c + offset)
        
    cell_size = min(450 // rows, 450 // cols)
    if cell_size < 5: cell_size = 5
    
    canvas = tk.Canvas(grid_frame, width=cols*cell_size, height=rows*cell_size, bg="#1E1E1E", highlightthickness=0)
    canvas.pack(expand=True)
    
    rects = {}
    texts = {}
    
    def get_default_colors(r, c):
        bit = matrix[r][c]
        cell_data = cw_map[r][c]
        if cell_data is not None:
            cw_id = int(cell_data[0])
            if cw_id <= data_len:
                fill = "#1565C0" if bit else "#BBDEFB"
                text_fill = "white" if bit else "black"
            else:
                fill = "#6A1B9A" if bit else "#E1BEE7"
                text_fill = "white" if bit else "black"
        else:
            fill = "black" if bit else "white"
            text_fill = "white" if bit else "black"
        return fill, text_fill
        
    for r in range(rows):
        for c in range(cols):
            fill, text_fill = get_default_colors(r, c)
            rect_id = canvas.create_rectangle(c*cell_size, r*cell_size, (c+1)*cell_size, (r+1)*cell_size, fill=fill, outline="#888888")
            rects[(r, c)] = rect_id
            
            cell_data = cw_map[r][c]
            if cell_data is not None and cell_size >= 15:
                cw_id = cell_data[0]
                font_size = max(6, min(10, cell_size // 3))
                text_id = canvas.create_text(c*cell_size + cell_size/2, r*cell_size + cell_size/2, text=str(cw_id), fill=text_fill, font=("Arial", font_size, "bold"), tags="text_tag")
                texts[(r, c)] = text_id
            else:
                texts[(r, c)] = None

    for r in range(rows):
        for c in range(cols):
            cw_id = cw_map[r][c][0] if cw_map[r][c] is not None else None
            
            if c < cols - 1:
                right_cw_id = cw_map[r][c+1][0] if cw_map[r][c+1] is not None else None
                if cw_id != right_cw_id:
                    canvas.create_line((c+1)*cell_size, r*cell_size, (c+1)*cell_size, (r+1)*cell_size, fill="#FFA500", width=2, tags="cw_boundary")
                    
            if r < rows - 1:
                bottom_cw_id = cw_map[r+1][c][0] if cw_map[r+1][c] is not None else None
                if cw_id != bottom_cw_id:
                    canvas.create_line(c*cell_size, (r+1)*cell_size, (c+1)*cell_size, (r+1)*cell_size, fill="#FFA500", width=2, tags="cw_boundary")

    anchor_ids = sorted(anchors.keys())
    anchor_circles = {}
    for i in range(len(anchor_ids)):
        id1 = anchor_ids[i]
        r1, c1 = anchors[id1]
        x1 = c1 * cell_size + cell_size / 2
        y1 = r1 * cell_size + cell_size / 2
        
        if i < len(anchor_ids) - 1:
            id2 = anchor_ids[i+1]
            r2, c2 = anchors[id2]
            x2 = c2 * cell_size + cell_size / 2
            y2 = r2 * cell_size + cell_size / 2
            
            if id1 <= data_len and id2 <= data_len:
                line_color = "#00E5FF"
            elif id1 > data_len:
                line_color = "#EA80FC"
            else:
                line_color = "#FF3D00"
                
            canvas.create_line(x1, y1, x2, y2, fill=line_color, width=2, arrow=tk.LAST, tags="path_line")
        
        radius = max(3, cell_size / 6)
        fill_color = "#FFFF00" if id1 <= data_len else "#FFD54F"
        circle_id = canvas.create_oval(x1-radius, y1-radius, x1+radius, y1+radius, fill=fill_color, outline="black", tags="anchor_circle")
        anchor_circles[id1] = circle_id
            
    def on_click(event):
        c = event.x // cell_size
        r = event.y // cell_size
        
        if 0 <= r < rows and 0 <= c < cols:
            cell_data = cw_map[r][c]
            
            for rr in range(rows):
                for cc in range(cols):
                    fill, text_fill = get_default_colors(rr, cc)
                    canvas.itemconfig(rects[(rr, cc)], fill=fill, outline="#888888", width=1)
                    if texts[(rr, cc)]:
                        canvas.itemconfig(texts[(rr, cc)], fill=text_fill)
                        
            for cw_id_key, circle_id in anchor_circles.items():
                default_fill = "#FFFF00" if cw_id_key <= data_len else "#FFD54F"
                canvas.itemconfig(circle_id, fill=default_fill, outline="black", width=1)
                    
            if cell_data is not None:
                target_cw_id = int(cell_data[0])
                target_bit_idx = cell_data[1]
                
                bits_info = {}
                
                for rr in range(rows):
                    for cc in range(cols):
                        cd = cw_map[rr][cc]
                        if cd is not None and int(cd[0]) == target_cw_id:
                            current_bit_idx = cd[1]
                            bits_info[current_bit_idx] = cd[2]
                            is_one = matrix[rr][cc]
                            
                            canvas.itemconfig(rects[(rr, cc)], fill="#00C853" if is_one else "#B9F6CA")
                            if texts[(rr, cc)]:
                                canvas.itemconfig(texts[(rr, cc)], fill="white" if is_one else "black")
                                
                if target_cw_id in anchor_circles:
                    canvas.itemconfig(anchor_circles[target_cw_id], fill="#FF0000", outline="white", width=2)
                    canvas.tag_raise(anchor_circles[target_cw_id])
                        
                canvas.itemconfig(rects[(r, c)], outline="#00FFFF", width=3)
                
                canvas.tag_raise("cw_boundary")
                canvas.tag_raise("path_line")
                canvas.tag_raise("anchor_circle")
                canvas.tag_raise("text_tag")
                
                byte_val = data_cache[target_cw_id - 1]
                
                binary_str = "".join([str(bits_info.get(i, 0)) for i in range(7, -1, -1)])
                    
                if target_cw_id <= data_len:
                    char = ""
                    if 32 <= byte_val <= 126:
                        char = chr(byte_val)
                        
                    cw_type = f"Data / Padding (Codeword: {byte_val})"
                    if char:
                        cw_type += f" [Ký tự ASCII: '{char}']"
                else:
                    cw_type = "Error Correction (Mã sửa lỗi Reed-Solomon)"
                    
                desc = f"🔍 Đang chọn: Codeword #{target_cw_id} — {cw_type}\n\n"
                desc += f"Chuỗi nhị phân nguyên thuỷ (trước Mask): {binary_str}\n"
                desc += f"Bit bạn vừa click là bit số {target_bit_idx} (0=LSB, 7=MSB), Giá trị sau Mask = {int(matrix[r][c])}\n"
                desc += f"Neo điểm (Bit xuất phát 7) đang được tô màu Đỏ.\n"
                desc += f"Giá trị thập phân: {byte_val} | Hex: 0x{byte_val:02X}"
                
                info_label.configure(text=desc)
            else:
                info_label.configure(text=f"Ô ({r}, {c}) không thuộc phần Data/EC.\n(Đây là thành phần tĩnh: Finder, Alignment, Timing, Version/Format Info, hoặc Mask)")

    canvas.bind("<Button-1>", on_click)
    return win
