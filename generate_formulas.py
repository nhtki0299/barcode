from PIL import Image, ImageDraw, ImageFont

BG_COLOR = "#2B2B2B"
TEXT_COLOR_MAIN = "#FFD54F" # Yellow for formulas
TEXT_COLOR_SUB = "#E0E0E0"  # White/gray for text

def get_font(size=24):
    try:
        # Try a few common Mac fonts that support unicode math
        return ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size)
    except:
        return ImageFont.load_default()

def draw_text_image(filename, lines, width, height):
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)
    font_main = get_font(22)
    font_sub = get_font(18)
    
    y = 15
    for text, is_main in lines:
        f = font_main if is_main else font_sub
        c = TEXT_COLOR_MAIN if is_main else TEXT_COLOR_SUB
        draw.text((20, y), text, fill=c, font=f)
        # Advance Y based on font size approx
        y += 35 if is_main else 25
        
    img.save(filename)

def generate_rs_formula():
    lines = [
        ("Đa thức sinh Reed-Solomon (Generator Polynomial):", False),
        ("g(x) = (x - α⁰)(x - α¹)(x - α²)...(x - αⁿ⁻ᵏ)", True),
        ("Trong đó:", False),
        ("- α (Alpha): Phần tử nguyên thuỷ của trường Galois.", False),
        ("- (n-k): Số lượng byte sửa lỗi (Error Correction Codewords).", False)
    ]
    draw_text_image("docs/images/rs_formula.png", lines, 550, 180)

def generate_gf_formula():
    lines = [
        ("Trường số học GF(2⁸) (Galois Field Modulo):", False),
        ("p(x) = x⁸ + x⁴ + x³ + x² + 1", True),
        ("Mọi phép toán cộng/nhân byte trong mã vạch đều", False),
        ("sử dụng trường GF(2⁸) thay cho số học thông thường.", False)
    ]
    draw_text_image("docs/images/gf_formula.png", lines, 500, 140)

def generate_penalty_formula():
    lines = [
        ("Công thức tính Điểm Phạt Masking (Penalty Score):", False),
        ("N₁ = (Số ô cùng màu liên tiếp - 5) + 3", True),
        ("N₂ = 3 × (Số khối vuông 2x2 cùng màu)", True),
        ("N₃ = 40 × (Số hoa văn giả Finder Pattern)", True),
        ("N₄ = 10 × (|Tỉ lệ Đen/Trắng - 50| / 5)", True),
        ("Penalty = N₁ + N₂ + N₃ + N₄ (Chọn Mask có Penalty nhỏ nhất!)", False)
    ]
    draw_text_image("docs/images/penalty_formula.png", lines, 600, 220)

if __name__ == "__main__":
    generate_rs_formula()
    generate_gf_formula()
    generate_penalty_formula()

def generate_ean13_formula():
    lines = [
        ("Công thức tính Ký tự kiểm tra (Checksum) EAN-13:", False),
        ("C = (10 - [(Σ Lẻ + 3 × Σ Chẵn) mod 10]) mod 10", True),
        ("Giải thích:", False),
        ("- Σ Lẻ: Tổng các chữ số ở vị trí lẻ (1, 3, 5...).", False),
        ("- Σ Chẵn: Tổng các chữ số ở vị trí chẵn (2, 4, 6...).", False)
    ]
    draw_text_image("docs/images/ean13_formula.png", lines, 550, 180)

def generate_datamatrix_gf_formula():
    lines = [
        ("Trường số học GF(2⁸) của DataMatrix ECC200:", False),
        ("p(x) = x⁸ + x⁵ + x³ + x² + 1", True),
        ("Lưu ý: Đa thức này KHÁC với QR Code (dùng x⁴ thay vì x⁵).", False),
        ("Điều này khiến thuật toán Reed-Solomon của DataMatrix", False),
        ("phải được tính toán hoàn toàn riêng biệt so với QR Code.", False)
    ]
    draw_text_image("docs/images/datamatrix_gf_formula.png", lines, 580, 180)

if __name__ == "__main__":
    generate_rs_formula()
    generate_gf_formula()
    generate_penalty_formula()
    generate_ean13_formula()
    generate_datamatrix_gf_formula()
