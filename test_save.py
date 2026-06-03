import core.encode as encode
img = encode.generate_qrcode("hello", "M")
img.save("test_qr.png")

img2 = encode.generate_barcode("123456789012", "ean13")
try:
    img2.save("test_barcode.png")
except Exception as e:
    print("Barcode save error:", type(e), e)

img3 = encode.generate_datamatrix("hello")
try:
    img3.save("test_datamatrix.png")
except Exception as e:
    print("Datamatrix save error:", type(e), e)
