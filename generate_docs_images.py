from PIL import Image, ImageDraw, ImageFont

BG_COLOR = "#2B2B2B"
CELL_SIZE = 15

def draw_qr_anatomy():
    # 21x21 QR Code
    img = Image.new("RGB", (21*CELL_SIZE, 21*CELL_SIZE), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    def draw_finder(r, c):
        for i in range(7):
            for j in range(7):
                is_black = (i==0 or i==6 or j==0 or j==6) or (2<=i<=4 and 2<=j<=4)
                color = "#FF3D00" if is_black else "#FFFFFF"
                draw.rectangle([c*CELL_SIZE+j*CELL_SIZE, r*CELL_SIZE+i*CELL_SIZE, c*CELL_SIZE+(j+1)*CELL_SIZE-1, r*CELL_SIZE+(i+1)*CELL_SIZE-1], fill=color)

    # Finders
    draw_finder(0, 0)
    draw_finder(0, 14)
    draw_finder(14, 0)
    
    # Timing
    for i in range(8, 13):
        color = "#00B4D8" if i % 2 == 0 else "#FFFFFF"
        # H
        draw.rectangle([i*CELL_SIZE, 6*CELL_SIZE, (i+1)*CELL_SIZE-1, 7*CELL_SIZE-1], fill=color)
        # V
        draw.rectangle([6*CELL_SIZE, i*CELL_SIZE, 7*CELL_SIZE-1, (i+1)*CELL_SIZE-1], fill=color)
        
    img.save("docs/images/qr_anatomy.png")

def draw_qr_masks():
    W = 4 * 10 * CELL_SIZE
    H = 2 * 12 * CELL_SIZE
    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # 8 masks
    for m in range(8):
        c_base = (m % 4) * 10
        r_base = (m // 4) * 12
        
        # text
        # draw.text((c_base*CELL_SIZE, r_base*CELL_SIZE), f"Mask {m}", fill="#FFFFFF") # Skip text, just draw pattern
        
        r_base += 2
        for r in range(8):
            for c in range(8):
                if m == 0: bit = (r + c) % 2 == 0
                elif m == 1: bit = r % 2 == 0
                elif m == 2: bit = c % 3 == 0
                elif m == 3: bit = (r + c) % 3 == 0
                elif m == 4: bit = (r // 2 + c // 3) % 2 == 0
                elif m == 5: bit = ((r * c) % 2) + ((r * c) % 3) == 0
                elif m == 6: bit = (((r * c) % 2) + ((r * c) % 3)) % 2 == 0
                elif m == 7: bit = (((r + c) % 2) + ((r * c) % 3)) % 2 == 0
                
                color = "#4CAF50" if bit else "#FFFFFF"
                x = (c_base + c) * CELL_SIZE
                y = (r_base + r) * CELL_SIZE
                draw.rectangle([x, y, x+CELL_SIZE-2, y+CELL_SIZE-2], fill=color)
                
    img.save("docs/images/qr_masks.png")

def draw_datamatrix():
    # 14x14 datamatrix
    img = Image.new("RGB", (14*CELL_SIZE, 14*CELL_SIZE), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    for r in range(14):
        for c in range(14):
            is_black = False
            color = "#FFFFFF"
            
            # L-finder
            if c == 0 or r == 13:
                is_black = True
                color = "#FF3D00"
            # Clock track
            elif r == 0:
                is_black = (c % 2 == 0)
                color = "#00E676" if is_black else "#FFFFFF"
            elif c == 13:
                is_black = (r % 2 == 1) # bottom is 13, so 13 is black (L-finder), so 12 is white, 11 is black. So if r%2 != 13%2
                # Wait, at row 0 (top), right is white or black?
                # Actually, DataMatrix clock track alternates.
                is_black = (r % 2 == 1)
                color = "#00E676" if is_black else "#FFFFFF"
            else:
                # Random data
                is_black = ((r*7 + c*3) % 5 < 2)
                color = "#9E9E9E" if is_black else "#E0E0E0"
                
            draw.rectangle([c*CELL_SIZE, r*CELL_SIZE, (c+1)*CELL_SIZE-1, (r+1)*CELL_SIZE-1], fill=color)
            
    img.save("docs/images/datamatrix.png")

if __name__ == "__main__":
    draw_qr_anatomy()
    draw_qr_masks()
    draw_datamatrix()
