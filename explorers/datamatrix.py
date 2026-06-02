import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

def open_datamatrix_explorer(text: str, parent=None):
    if not text or text == "Nhập text cần mã hóa...":
        messagebox.showwarning("Lỗi", "Vui lòng nhập text!")
        return

    import pystrich.datamatrix.placement as plc
    from pystrich.datamatrix import DataMatrixEncoder
    
    orig_place = plc.DataMatrixPlacer.place
    orig_ps = plc.DataMatrixPlacer.place_standard_shape
    orig_s1 = plc.DataMatrixPlacer.place_special_1
    orig_s2 = plc.DataMatrixPlacer.place_special_2
    orig_s3 = plc.DataMatrixPlacer.place_special_3
    orig_s4 = plc.DataMatrixPlacer.place_special_4
    orig_pb = plc.DataMatrixPlacer.place_bit

    class Tracker:
        cw_map = []
        cw_anchors = {}

    def new_place(self, codewords, matrix):
        Tracker.cw_map = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        Tracker.cw_anchors = {}
        return orig_place(self, codewords, matrix)

    def new_ps(self, position, codeword):
        Tracker.cw_anchors[codeword] = position
        return orig_ps(self, position, codeword)

    def new_s1(self, cw): 
        Tracker.cw_anchors[cw] = (self.rows-1, 0)
        return orig_s1(self, cw)

    def new_s2(self, cw): 
        Tracker.cw_anchors[cw] = (self.rows-3, 0)
        return orig_s2(self, cw)

    def new_s3(self, cw): 
        Tracker.cw_anchors[cw] = (self.rows-2, 0)
        return orig_s3(self, cw)

    def new_s4(self, cw): 
        Tracker.cw_anchors[cw] = (self.rows-1, 0)
        return orig_s4(self, cw)

    def new_pb(self, position, bit):
        r, c = position
        if r < 0:
            r += self.rows
            c += 4 - ((self.rows + 4) % 8)
        if c < 0:
            c += self.cols
            r += 4 - ((self.cols + 4) % 8)
        
        cw_id = self.cw
        bit_idx = bit
        if 0 <= r < self.rows and 0 <= c < self.cols:
            raw_bit = ((self.codewords[cw_id-1] >> bit_idx) & 1) if cw_id > 0 else 0
            Tracker.cw_map[r][c] = (cw_id, bit_idx, raw_bit)
            
        return orig_pb(self, position, bit)

    plc.DataMatrixPlacer.place = new_place
    plc.DataMatrixPlacer.place_standard_shape = new_ps
    plc.DataMatrixPlacer.place_special_1 = new_s1
    plc.DataMatrixPlacer.place_special_2 = new_s2
    plc.DataMatrixPlacer.place_special_3 = new_s3
    plc.DataMatrixPlacer.place_special_4 = new_s4
    plc.DataMatrixPlacer.place_bit = new_pb

    try:
        encoder = DataMatrixEncoder(text)
        matrix = encoder.matrix
        
        from pystrich.datamatrix.textencoder import TextEncoder
        import pystrich.datamatrix.textencoder as te
        txt_enc = TextEncoder()
        data_cws = txt_enc.encode(text)
        data_len = te.data_word_length[txt_enc.size_index]
        
        show_datamatrix_explorer(matrix, Tracker.cw_map, data_len, Tracker.cw_anchors, data_cws, parent)
    except Exception as e:
        messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {e}")
    finally:
        plc.DataMatrixPlacer.place = orig_place
        plc.DataMatrixPlacer.place_standard_shape = orig_ps
        plc.DataMatrixPlacer.place_bit = orig_pb
        plc.DataMatrixPlacer.place_special_1 = orig_s1
        plc.DataMatrixPlacer.place_special_2 = orig_s2
        plc.DataMatrixPlacer.place_special_3 = orig_s3
        plc.DataMatrixPlacer.place_special_4 = orig_s4


def show_datamatrix_explorer(matrix, cw_map, data_len, cw_anchors, data_cws, parent):
    win = ctk.CTkToplevel(parent)
    win.title("🔍 Interactive DataMatrix Explorer")
    win.geometry("600x650")
    
    info_frame = ctk.CTkFrame(win)
    info_frame.pack(fill="x", padx=20, pady=10)
    
    info_label = ctk.CTkLabel(info_frame, text="Bấm vào một ô vuông trong lưới để phân tích", font=ctk.CTkFont(size=14, weight="bold"))
    info_label.pack(pady=10)
    
    grid_frame = ctk.CTkFrame(win)
    grid_frame.pack(expand=True, fill="both", padx=20, pady=10)
    
    orig_rows = len(matrix)
    orig_cols = len(matrix[0])
    rows = orig_rows + 2
    cols = orig_cols + 2
    
    expanded_matrix = []
    expanded_cw_map = []
    for r in range(rows):
        expanded_matrix.append([False] * cols)
        expanded_cw_map.append([None] * cols)
        
    for r in range(rows):
        for c in range(cols):
            if c == 0:
                expanded_matrix[r][c] = (r % 2 == rows % 2)
            elif r == rows - 1:
                expanded_matrix[r][c] = True
            elif c == cols - 1:
                expanded_matrix[r][c] = (r % 2 == 0)
            elif r == 0:
                expanded_matrix[r][c] = (c % 2 == 0)
            else:
                expanded_matrix[r][c] = matrix[r-1][c-1]
                if 0 <= r-1 < len(cw_map) and 0 <= c-1 < len(cw_map[0]):
                    expanded_cw_map[r][c] = cw_map[r-1][c-1]
                    
    matrix = expanded_matrix
    cw_map = expanded_cw_map
    
    anchors = {}
    for cw_id, (r, c) in cw_anchors.items():
        anchors[cw_id] = (r + 1, c + 1)
        
    cell_size = min(400 // rows, 400 // cols)
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
                
                byte_val = 0
                binary_str = ""
                for i in range(7, -1, -1):
                    v = bits_info.get(i, 0)
                    binary_str += str(v)
                    byte_val |= (v << i)
                    
                if target_cw_id <= data_len:
                    if target_cw_id <= len(data_cws):
                        try:
                            pad_start = data_cws.index(129)
                        except ValueError:
                            pad_start = len(data_cws)
                            
                        if target_cw_id - 1 >= pad_start:
                            cw_type = "Padding (Ký tự đệm)"
                        else:
                            if byte_val >= 1 and byte_val <= 128:
                                char = chr(byte_val - 1)
                                cw_type = f"Data (Ký tự: '{char}')"
                            elif byte_val >= 130 and byte_val <= 229:
                                digit_pair = f"{byte_val - 130:02d}"
                                cw_type = f"Data (Cặp số nén: '{digit_pair}')"
                            else:
                                cw_type = "Data"
                    else:
                        cw_type = "Padding (Ký tự đệm)"
                else:
                    cw_type = "Error Correction (Mã sửa lỗi Reed-Solomon)"
                    
                desc = f"🔍 Đang chọn: Codeword #{target_cw_id} — {cw_type}\n\n"
                desc += f"Chuỗi nhị phân: {binary_str} (Bạn vừa click vào Bit {target_bit_idx}, giá trị = {matrix[r][c]})\n"
                desc += f"Neo điểm (Trung tâm khối 8-bit theo ISO) đang được tô màu Đỏ.\n"
                desc += f"Giá trị thập phân: {byte_val} | Hex: 0x{byte_val:02X}"
                
                info_label.configure(text=desc)
            else:
                info_label.configure(text=f"Ô ({r}, {c}) không thuộc phần Data/EC.\n(Đây là thành phần cố định: Finder Pattern / Clock Track)")

    canvas.bind("<Button-1>", on_click)
    return win
