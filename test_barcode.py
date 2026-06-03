import core.encode as encode
print("Generating barcode...")
img = encode.generate_barcode("123456789012", "ean13")
print("Saving barcode...")
img.save("out_barcode.png")
print("Barcode saved.")

print("Generating QR...")
img2 = encode.generate_qrcode("hello", "M")
print("Saving QR...")
img2.save("out_qrcode.png")
print("QR saved.")
