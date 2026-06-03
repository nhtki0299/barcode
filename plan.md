# Barcode / DataMatrix / QR Code Generator App (Python)

Xây dựng một desktop app bằng Python cho phép người dùng nhập text, chọn loại mã hóa (Barcode, DataMatrix, QR Code), hiển thị **kết quả thực tế của từng bước biến đổi** từ text sang mã hoàn chỉnh, hiển thị ảnh mã, và lưu ảnh/log.

---

## 1. Tổng quan kiến trúc

| Thành phần | Công nghệ |
|------------|-----------|
| **Ngôn ngữ** | Python |
| **GUI Framework** | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — Dark mode, TabView |
| **Barcode (1D)** | `python-barcode` + `Pillow` (Code 128, Code 39, EAN-13) |
| **QR Code** | `qrcode` + `Pillow` (Tuỳ chọn Mức sửa lỗi L/M/Q/H) |
| **DataMatrix** | `pystrich` + `Pillow` (Mã hoá), `pylibdmtx` (Giải mã) |
| **Giải mã (Decode)**| `pyzbar` (QR/Barcode) + `pylibdmtx` (DataMatrix) |
| **Xử lý ảnh** | `Pillow` (PIL) |

### Cài đặt dependencies

```bash
pip install customtkinter pillow python-barcode qrcode pystrich pyzbar pylibdmtx setuptools
```

> **Lưu ý Cài đặt Thư viện Lõi C:** 
> - macOS: `brew install zbar libdmtx` (cần symlink vào `~/lib` đối với chip Apple Silicon)
> - Ubuntu: `sudo apt install libzbar0 libdmtx0b`
> - Windows: Thông thường đi kèm sẵn DLL trong pip packages.

---

## 2. Cấu trúc file

```
/Users/macos/Documents/barcode/
├── plan.md         ← File plan (tài liệu này)
└── app.py          ← File duy nhất, chạy: python app.py
```

---

## 3. Giao diện ứng dụng (UI Layout)

Giao diện chia làm 4 chế độ chính qua thanh Sidebar: **Mã Hoá (Encode)**, **Giải Mã (Decode)**, **Xử Lý Ảnh (Process)** và **Tài Liệu (Docs)**.

### Tab: Mã Hoá (Encode)
```
┌─────────────────────────────────────────────────────────┐
│              🔲 Code Generator                          │
│              Barcode • DataMatrix • QR Code             │
├─────────────────────────────────────────────────────────┤
│ [ Sidebar: Mã Hoá / Giải Mã / Xử Lý Ảnh / Tài Liệu ]    │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────┐    │
│  │  📝 Nhập text cần mã hóa...                     │    │
│  └─────────────────────────────────────────────────┘    │
│                                                         │
│  ◉ Barcode (Dropdown)  ○ DataMatrix  ○ QR Code (L/M/Q/H)│
│  [ 🔍 Khám phá DataMatrix Explorer (chỉ DataMatrix) ]   │
│                                                         │
│            [ ⚡ GENERATE CODE ]                          │
├──────────────────────┬──────────────────────────────────┤
│  📋 Transformation   │  🖼️ Code Preview                 │
│  Log                 │                                  │
│ ─────────────────── │  ┌──────────────────────────┐    │
│  [Log chi tiết]      │  │    [Generated Code      │    │
│  [Bitstream]         │  │     Image Here]         │    │
│  [Raw Codewords]     │  └──────────────────────────┘    │
│                      │  [ 💾 Save Image ] [ 📄 Save Log]│
└──────────────────────┴──────────────────────────────────┘
```

### Tab: Giải Mã (Decode)
```
┌─────────────────────────────────────────────────────────┐
│  [ 🖼️ Tải Ảnh Cần Dịch ]    [ 🔍 GIẢI MÃ TỰ ĐỘNG ]       │
│  [ 🧩 Trích xuất lưới 8-bit (nếu có DataMatrix) ]       │
├──────────────────────┬──────────────────────────────────┤
│  📋 Decoding Log     │  🖼️ Image Output                 │
│ ─────────────────── │  ┌──────────────────────────┐    │
│  [Tiền xử lý ảnh]    │  │    [Ảnh với Bounding Box│    │
│  [Pattern Recognize] │  │     màu xanh bao quanh] │    │
│  [Grid Sampling]     │  └──────────────────────────┘    │
│  [Trích xuất 8-bit]  │                                  │
└──────────────────────┴──────────────────────────────────┘
```

---

## 4. Chi tiết thiết kế

### 4.1 Class `CodeGeneratorApp(ctk.CTk)`

**Khởi tạo GUI** (`__init__`):
- Window size: `1100x750`, title: `"Pro Barcode Studio"`
- `ctk.set_appearance_mode("dark")`, theme: `"blue"`
- Grid layout responsive: Cột trái (Sidebar) và Cột phải (Main Content)

### 4.2 Danh sách Widgets

| Widget | Type | Mô tả |
|--------|------|--------|
| `header_label` | `CTkLabel` | Tiêu đề app, font lớn + emoji |
| `text_input` | `CTkTextbox` | Ô nhập text, height=80 |
| `encoding_var` | `StringVar` | Giá trị radio: `"barcode"`, `"datamatrix"`, `"qrcode"` |
| `radio_barcode` | `CTkRadioButton` | Chọn Barcode (Code 128) |
| `radio_datamatrix` | `CTkRadioButton` | Chọn DataMatrix |
| `radio_qrcode` | `CTkRadioButton` | Chọn QR Code |
| `generate_btn` | `CTkButton` | Nút "⚡ Generate Code" |
| `log_textbox` | `CTkTextbox` | Panel log biến đổi, monospace, read-only, scrollable |
| `preview_label` | `CTkLabel` | Hiển thị ảnh mã (CTkImage) |
| `save_image_btn` | `CTkButton` | Nút "💾 Save Image" |
| `save_log_btn` | `CTkButton` | Nút "📄 Save Log" |

---

## 5. Các bước biến đổi thực tế (Transformation Engine)

> **Quan trọng:** Log panel phải hiển thị **kết quả tính toán thực** tại mỗi bước, không chỉ mô tả. App tự tính toán và minh hoạ từng bước biến đổi để người dùng thấy quá trình từ text gốc ra mã hoàn chỉnh.

---

### 5A. Barcode – Code 128

**Input ví dụ:** `"Hi9"`

#### Bước 1 — Input nhận được
```
📥 INPUT
   Text gốc : "Hi9"
   Độ dài   : 3 ký tự
   Byte size: 3 bytes
```

#### Bước 2 — Chuyển ký tự → ASCII code
App tính từng ký tự sang giá trị ASCII:
```
🔤 CHARACTER → ASCII
   'H' → 72
   'i' → 105
   '9' → 57
```

#### Bước 3 — Chọn Character Set & Codeword
Code 128 Set B được chọn (hỗ trợ chữ hoa + thường + số).
App ánh xạ từng ASCII sang codeword Code 128:
```
📋 ASCII → CODE 128 CODEWORD (Set B)
   Start B  → codeword 104
   'H'  (72) → codeword 40
   'i' (105) → codeword 73
   '9'  (57) → codeword 25
```

#### Bước 4 — Tính checksum (mod 103)
```
🧮 CHECKSUM CALCULATION
   Công thức: (StartVal + Σ position × codeword) mod 103
   = (104 + 1×40 + 2×73 + 3×25) mod 103
   = (104 + 40 + 146 + 75) mod 103
   = 365 mod 103
   = 53  ← checksum codeword
```

#### Bước 5 — Chuỗi codeword hoàn chỉnh
```
📦 FINAL CODEWORD SEQUENCE
   [START B] [40] [73] [25] [53] [STOP]
   = 104, 40, 73, 25, 53, 106
```

#### Bước 6 — Chuyển codeword → bar pattern
Mỗi codeword ánh xạ thành chuỗi 11 module (bar/space widths):
```
📊 CODEWORD → BAR PATTERN (widths)
   104 (Start B) → 2 1 1 4 1 2
   40  ('H')     → 1 1 1 1 4 1
   73  ('i')     → 1 3 1 3 1 1
   25  ('9')     → 1 2 1 4 1 1
   53  (check)   → 1 1 2 2 1 3
   106 (Stop)    → 2 3 3 1 1 1 2
   Tổng modules  : 67 modules
```

#### Bước 7 — Render ảnh
```
✅ RENDER
   Kích thước   : 284 × 100 px
   Thời gian    : 8ms
   Status       : SUCCESS
```

---

### 5B. QR Code

**Input ví dụ:** `"Hi9"`

#### Bước 1 — Input nhận được
```
📥 INPUT
   Text gốc : "Hi9"
   Độ dài   : 3 ký tự
   Byte size: 3 bytes
```

#### Bước 2 — Phân tích & chọn Mode
App phân tích từng ký tự để chọn mode tối ưu:
```
🔍 MODE SELECTION
   'H' → chữ hoa → Alphanumeric
   'i' → chữ thường → Byte mode
   '9' → số → Numeric
   Mode cuối chọn : Byte (vì có chữ thường)
   Mode indicator : 0100 (4 bits)
```

#### Bước 3 — Mã hoá dữ liệu thành chuỗi bit
Từng ký tự chuyển sang mã UTF-8 rồi sang binary:
```
🔄 TEXT → BINARY
   'H' → 0x48 → 01001000
   'i' → 0x69 → 01101001
   '9' → 0x39 → 00111001
   Character count: 00000011 (3 chars, 8 bits)

   Data bitstream:
   [mode] [count]  [  H  ]  [  i  ]  [  9  ]
   0100   00000011  01001000  01101001  00111001
```

#### Bước 4 — Thêm padding → Data codewords
QR version 1-M cần 16 data codewords (128 bits).
App thêm terminator + padding:
```
📦 DATA CODEWORDS (hex)
   Dữ liệu thực : 40 03 48 69 39
   Terminator   : 0000
   Padding bytes: EC 11 EC 11 EC 11 EC 11 EC 11 EC
   Final 16 codewords: 40 03 48 69 39 00 EC 11 EC 11 EC 11 EC 11 EC 11
```

#### Bước 5 — Reed-Solomon Error Correction
```
🛡️ ERROR CORRECTION (Reed-Solomon, level M)
   EC codewords cần: 10
   RS polynomial   : x^10 + ...
   EC codewords    : A4 B2 3C 7F 1E 9D 55 2A C8 06
```

#### Bước 6 — Sắp xếp matrix & Masking
```
📐 MATRIX & MASKING
   QR version   : 1
   Matrix size  : 21 × 21 modules
   Data modules : 208
   Finder pattern: 3 góc 7×7
   Timing pattern: hàng/cột 6
   Mask pattern  : #2 (i mod 3 = 0) — chọn penalty thấp nhất
   Penalty score : 84
```

#### Bước 7 — Render ảnh
```
✅ RENDER
   Kích thước: 290 × 290 px
   Thời gian : 15ms
   Status    : SUCCESS
```

---

### 5C. DataMatrix (ECC 200)

**Input ví dụ:** `"Hi9"`

#### Bước 1 — Input nhận được
```
📥 INPUT
   Text gốc : "Hi9"
   Độ dài   : 3 ký tự
   Byte size: 3 bytes
```

#### Bước 2 — Chọn encoding scheme
```
🔍 ENCODING SCHEME
   'H' (72),  'i' (105), '9' (57) → toàn ASCII
   Scheme chọn: ASCII (giá trị = ASCII + 1)
```

#### Bước 3 — Chuyển ký tự → ASCII codewords
```
🔄 CHARACTER → CODEWORD
   'H' (ASCII 72) → codeword 73   (= 72 + 1)
   'i' (ASCII 105) → codeword 106 (= 105 + 1)
   '9' (ASCII 57)  → codeword 58  (= 57 + 1)
   Data codewords: [73, 106, 58]
```

#### Bước 4 — Chọn kích thước matrix & Padding
```
📐 MATRIX SELECTION
   Cần 3 data codewords
   Matrix nhỏ nhất phù hợp: 10×10
   Tổng data slots: 3 codewords
   Padding cần thêm: 0 (vừa đủ)
   Padding symbol  : 129 (không cần)
   Final data: [73, 106, 58]
```

#### Bước 5 — Reed-Solomon Error Correction
```
🛡️ ERROR CORRECTION (Reed-Solomon, tự động)
   Matrix 10×10 cần: 5 EC codewords
   RS polynomial   : GF(2^8) = x^8 + x^5 + x^3 + x^2 + 1
   EC codewords    : 21 E8 4D A3 9F
   Final sequence  : [73, 106, 58, 21, 232, 77, 163, 159]
```

#### Bước 6 — Điền bit vào matrix
```
📊 BIT PLACEMENT
   8 codewords × 8 bits = 64 bits
   Sắp xếp theo quy tắc diagonal fill
   L-finder pattern: cạnh trái + cạnh dưới
   Clock track     : cạnh phải + cạnh trên xen kẽ
   Module count    : 10 × 10 = 100 modules
```

#### Bước 7 — Render ảnh
```
✅ RENDER
   Kích thước: 100 × 100 px (scale 10×)
   Thời gian : 5ms
   Status    : SUCCESS
```

---

## 6. Encoding Functions

### 6.1 Barcode (Code 128)

```python
def generate_barcode(self, text: str) -> Image:
    """Tạo Code 128 barcode bằng python-barcode"""
    code128 = barcode.get('code128', text, writer=ImageWriter())
    buffer = io.BytesIO()
    code128.write(buffer)
    buffer.seek(0)
    return Image.open(buffer)
```

### 6.2 QR Code

```python
def generate_qrcode(self, text: str) -> Image:
    """Tạo QR Code bằng qrcode library"""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert('RGB')
```

### 6.3 DataMatrix

```python
def generate_datamatrix(self, text: str) -> Image:
    """Tạo DataMatrix bằng pylibdmtx"""
    encoded = encode(text.encode('utf-8'))
    return Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
```

---

## 7. Log & Save Functions

### 7.1 `build_log(text, encoding_type)` — Hàm tính toán log

App **tự tính toán** các giá trị trung gian để in ra log:

```python
def build_log(self, text: str, encoding_type: str) -> str:
    """Tính toán và trả về chuỗi log đầy đủ với kết quả thực tế"""
    if encoding_type == "barcode":
        return self._log_barcode(text)
    elif encoding_type == "qrcode":
        return self._log_qrcode(text)
    elif encoding_type == "datamatrix":
        return self._log_datamatrix(text)

def _log_barcode(self, text: str) -> str:
    lines = []
    lines.append(f"[1] 📥 INPUT\n    Text: \"{text}\"\n    Độ dài: {len(text)} ký tự")
    # ASCII codes
    ascii_map = {c: ord(c) for c in text}
    lines.append("[2] 🔤 CHARACTER → ASCII\n" +
                 "\n".join(f"    '{c}' → {v}" for c, v in ascii_map.items()))
    # Codewords (Code128 Set B: codeword = ASCII - 32)
    codewords = [ord(c) - 32 for c in text]
    lines.append("[3] 📋 ASCII → CODEWORD (Set B)\n    Start B → 104\n" +
                 "\n".join(f"    '{c}' ({ord(c)}) → codeword {w}"
                           for c, w in zip(text, codewords)))
    # Checksum
    checksum = (104 + sum((i+1)*w for i, w in enumerate(codewords))) % 103
    lines.append(f"[4] 🧮 CHECKSUM\n    (104 + Σ pos×codeword) mod 103 = {checksum}")
    # Full sequence
    full_seq = [104] + codewords + [checksum, 106]
    lines.append(f"[5] 📦 CODEWORD SEQUENCE\n    {full_seq}")
    # Bar pattern (tính tổng modules)
    total_modules = 11 * len(full_seq) + 2  # ước tính
    lines.append(f"[6] 📊 BAR PATTERN\n    Tổng modules: ~{total_modules}")
    return "\n\n".join(lines)
```

### 7.2 Save Image (PNG)

```python
def save_image(self):
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
    )
    if filepath:
        self.current_image.save(filepath)
```

### 7.3 Save Log (TXT)

```python
def save_log(self):
    filepath = filedialog.asksaveasfilename(
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if filepath:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.log_textbox.get("1.0", "end"))
```

---

## 8. Helper Functions

| Hàm | Mô tả |
|-----|--------|
| `build_log(text, type)` | Tính toán và trả về chuỗi log đầy đủ với kết quả thực |
| `_log_barcode(text)` | Tính log 7 bước cho Barcode Code 128 |
| `_log_qrcode(text)` | Tính log 7 bước cho QR Code |
| `_log_datamatrix(text)` | Tính log 7 bước cho DataMatrix |
| `to_hex(text)` | Chuyển text sang hex string (vd: `"48 65 6C 6C 6F"`) |
| `to_binary(text)` | Chuyển text sang binary string |
| `update_preview(image)` | Resize ảnh + hiển thị lên `preview_label` bằng `CTkImage` |
| `show_error(msg)` | Hiển thị messagebox lỗi |

---

## 9. Luồng hoạt động (Workflow)

### Encode Workflow
```
Người dùng                    App
    │                          │
    ├── Nhập text "Hi9" ─────► │
    ├── Chọn loại mã, config ─► │
    ├── Click "Generate" ────► │
    │                          ├── Gọi build_log() → tính toán 7 bước thực tế
    │                          ├── In kết quả từng bước (Codeword, Padding, Matrix)
    │                          ├── Gọi generate_code() (pystrich, qrcode, barcode)
    │                          ├── Nhận PIL Image → update_preview()
    │                          ├── Cập nhật "DataMatrix Explorer" (monkey-patch)
    │                          │
    ├── Click "Khám phá" ────► ├── Bật CTkToplevel Window hiển thị lưới tương tác
```

### Decode Workflow
```
Người dùng                    App
    │                          │
    ├── Tải ảnh lên ─────────► │
    ├── Click "Giải Mã" ─────► │
    │                          ├── Gọi pyzbar_decode(img)
    │                          ├── Gọi pylibdmtx_decode(img)
    │                          ├── In lý thuyết Pipeline xử lý ảnh (Log)
    │                          ├── Lấy dữ liệu Raw Bytes & Binary Stream (Log)
    │                          ├── Dùng PIL ImageDraw vẽ Bounding Box lên Preview
    │                          ├── Kích hoạt nút "Trích xuất lưới 8-bit"
```

---

## 10. Tính năng Nâng cao

### DataMatrix Interactive Explorer
- **Hoạt động**: Thay vì chỉ in ra log tĩnh, khi tạo DataMatrix, app sử dụng kỹ thuật *Monkey Patching* (ghi đè phương thức) lên hàm `place_bit` của `pystrich.datamatrix.placement` để theo dõi chính xác từng Bit được thả vào toạ độ nào trên ma trận.
- **Trải nghiệm**: Một màn hình lưới Grid sẽ hiện ra. Người dùng click vào 1 ô vuông (bit), phần mềm sẽ highlight toàn bộ 7 bit còn lại trong cùng một Codeword 8-bit bằng màu xanh, và làm nổi bật Điểm Neo (Anchor Bit 0) bằng màu đỏ, sau đó tính toán ra giá trị Thập phân (Decimal) ngay lập tức. Tính năng này hỗ trợ cực mạnh cho việc học hỏi thuật toán DataMatrix Placement (Utah Shape / Diagonal Fill).

---

## 11. Verification Plan

### Kiểm thử chức năng
1. Chạy `python app.py` → GUI hiển thị đúng
2. Nhập `"Hi9"` → chọn **Barcode** → Generate → kiểm tra log đủ 7 bước với kết quả thực
3. Nhập `"Hi9"` → chọn **QR Code** → Generate → kiểm tra mode selection, bitstream, EC
4. Nhập `"Hi9"` → chọn **DataMatrix** → Generate → kiểm tra codewords, RS, matrix size
5. Click **Save Image** → lưu PNG → mở kiểm tra đúng ảnh
6. Click **Save Log** → lưu TXT → mở kiểm tra đủ nội dung

### Kiểm thử edge case
- Text rỗng → báo lỗi không crash
- Text tiếng Việt có dấu → QR/DataMatrix encode đúng UTF-8
- Text rất dài → log cuộn được, preview scale đúng

### Kiểm thử thực tế
- Quét mã QR bằng điện thoại → đọc đúng text gốc
- Quét mã DataMatrix bằng app scanner → đọc đúng
- In barcode → scan bằng đầu đọc barcode → đọc đúng
