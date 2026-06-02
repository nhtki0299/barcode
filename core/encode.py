from PIL import Image
import io
import barcode
from barcode.writer import ImageWriter
import qrcode
from pystrich.datamatrix import DataMatrixEncoder
import pystrich.datamatrix.textencoder as te

def generate_barcode(text: str, barcode_type: str) -> Image.Image:
    if barcode_type == "code128":
        code_class = barcode.get_barcode_class('code128')
    elif barcode_type == "code39":
        code_class = barcode.get_barcode_class('code39')
    elif barcode_type == "ean13":
        if len(text) != 12 and len(text) != 13:
            raise ValueError("EAN-13 yêu cầu chuỗi có 12 hoặc 13 chữ số")
        if not text.isdigit():
            raise ValueError("EAN-13 chỉ hỗ trợ số")
        code_class = barcode.get_barcode_class('ean13')
    else:
        raise ValueError("Loại barcode không được hỗ trợ")

    code = code_class(text, writer=ImageWriter())
    fp = io.BytesIO()
    code.write(fp)
    fp.seek(0)
    return Image.open(fp).convert("RGB")

def generate_qrcode(text: str, error_val: str) -> Image.Image:
    # L(7%), M(15%), Q(25%), H(30%)
    error_dict = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H
    }
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_dict.get(error_val, qrcode.constants.ERROR_CORRECT_M),
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def generate_datamatrix(text: str) -> Image.Image:
    encoder = DataMatrixEncoder(text)
    encoder.cellsize = 10
    encoder.margin = 10
    
    fp = io.BytesIO()
    encoder.save(fp)
    fp.seek(0)
    return Image.open(fp).convert("RGB")

def _log_barcode(text: str) -> str:
    log = ""
    log += "  * [MÃ HOÁ KÝ TỰ - CHARACTER ENCODING]\n"
    log += f"    - Phân tích chuỗi đầu vào: '{text}' (Chiều dài: {len(text)} ký tự)\n"
    log += "    - Chuyển đổi mỗi ký tự thành chuỗi nhị phân (Widths của vạch/khoảng trắng).\n"
    log += "  * [TÍNH TOÁN CHECKSUM]\n"
    log += "    - Thuật toán Modulo (Mod 10 cho EAN/UPC, Mod 103 cho Code128) để sinh ký tự kiểm tra.\n"
    log += "  * [THÊM KÝ TỰ ĐIỀU KHIỂN]\n"
    log += "    - Chèn Start Code ở đầu và Stop Code ở cuối.\n"
    log += "  * [VẼ ĐỒ HOẠ - RENDER]\n"
    log += "    - Ánh xạ 1 -> Vạch Đen (Bar), 0 -> Khoảng Trắng (Space).\n"
    return log

def _log_qrcode(text: str, error_val: str) -> str:
    log = ""
    log += "  * [MÃ HOÁ KÝ TỰ & TỐI ƯU]\n"
    log += f"    - Chọn chế độ mã hoá (Numeric, Alphanumeric, Byte, Kanji) tối ưu nhất cho chuỗi '{text}'.\n"
    log += "    - Thêm Padding bits để lấp đầy khối dữ liệu.\n"
    log += f"  * [SỬA LỖI REED-SOLOMON - ERROR CORRECTION MỨC {error_val}]\n"
    log += "    - Sinh các byte sửa lỗi bằng đa thức Reed-Solomon để đảm bảo khả năng khôi phục khi mã bị mờ/rách.\n"
    log += "  * [ĐẶT DỮ LIỆU & MASKING]\n"
    log += "    - Đặt các Position Detection Patterns (3 hình vuông ở góc) và Timing Patterns.\n"
    log += "    - Thử nghiệm 8 Mask Patterns khác nhau (toán tử XOR) lên ma trận dữ liệu.\n"
    log += "    - Tính điểm phạt (Penalty) để chọn Mask tốt nhất, tránh việc xuất hiện quá nhiều điểm đen/trắng tụ lại.\n"
    log += "  * [VẼ ĐỒ HOẠ]\n"
    log += "    - Ánh xạ ma trận 2D thành các pixel vuông (Modules).\n"
    return log

def _log_datamatrix(text: str) -> str:
    log = ""
    log += "  * [MÃ HOÁ TEXT - TEXT ENCODATION]\n"
    is_ascii = all(ord(c) < 128 for c in text)
    scheme = "ASCII" if is_ascii else "Base 256 / Auto"
    log += f"    - Chọn thuật toán mã hoá: {scheme}\n"
    if is_ascii:
        cw_list = [ord(c) + 1 for c in text]
        log += f"    - Chuỗi Codewords thô: {cw_list}\n"
    log += "  * [SỬA LỖI REED-SOLOMON (ECC200)]\n"
    log += "    - Đệm Padding (129, và các giá trị sinh ngẫu nhiên) để làm đầy vùng dữ liệu.\n"
    log += "    - Tính toán khối Error Correction bằng đa thức Reed-Solomon.\n"
    log += "  * [PHÂN BỔ MA TRẬN - BIT PLACEMENT]\n"
    log += "    - Đặt các Finder Pattern (Hình chữ L nét liền ở cạnh trái/dưới) và Clock Track (Răng cưa ở cạnh phải/trên).\n"
    log += "    - Áp dụng thuật toán điền zíc-zắc (Snake/Zigzag sweep) chạy nghiêng 45 độ để thả các khối 8-bit.\n"
    log += "  * [VẼ ĐỒ HOẠ]\n"
    log += "    - Vẽ các điểm (Modules) trên lưới vuông.\n"
    return log

def build_log(text: str, encoding_type: str, barcode_type: str = "", error_val: str = "") -> str:
    log = f"⚙️ Đang thực thi mã hoá: {encoding_type.upper()}\n"
    log += "="*40 + "\n"
    
    if encoding_type == "barcode":
        log += _log_barcode(text)
    elif encoding_type == "qrcode":
        log += _log_qrcode(text, error_val)
    elif encoding_type == "datamatrix":
        log += _log_datamatrix(text)
        
    log += "="*40 + "\n"
    log += "✅ Hoàn tất render ảnh.\n"
    return log
