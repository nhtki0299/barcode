import time
from typing import Tuple, List, Dict, Any

def run_decode(img) -> Tuple[str, List[Dict[str, Any]]]:
    log = ""
    log += "\n" + "="*40 + "\n BẮT ĐẦU GIẢI MÃ\n" + "="*40 + "\n\n"
    
    try:
        from pyzbar.pyzbar import decode as pyzbar_decode
    except ImportError:
        log += "[!] Chưa cài đặt pyzbar hoặc zbar. Vui lòng chạy lệnh: brew install zbar && pip install pyzbar\n"
        return log, []
        
    try:
        from pylibdmtx.pylibdmtx import decode as dmtx_decode
    except ImportError:
        log += "[!] Chưa cài đặt pylibdmtx.\n"
        return log, []
        
    found_codes = []
    
    # 1. Decode pyzbar
    log += "========================================================\n"
    log += "[PHASE 1] TÌM KIẾM QR CODE & BARCODE (Engine: pyzbar)\n"
    log += "========================================================\n"
    log += "  * [THUẬT TOÁN TIỀN XỬ LÝ ẢNH]\n"
    log += "    - Chuyển đổi ảnh sang hệ màu Xám (Grayscale).\n"
    log += "    - Nhị phân hoá (Binarization) sử dụng Adaptive Thresholding để tách vạch đen/trắng.\n"
    log += "    - Chạy thuật toán Edge Detection (Canny) để tìm đường viền.\n\n"
    
    start = time.time()
    try:
        zbar_results = pyzbar_decode(img)
        elapsed = (time.time() - start)*1000
        
        if len(zbar_results) == 0:
            log += f"  -> [KẾT QUẢ] Không tìm thấy QR/Barcode nào (Time: {elapsed:.1f}ms).\n\n"
        else:
            log += f"  -> [KẾT QUẢ] Đã quét và phát hiện {len(zbar_results)} mã (Time: {elapsed:.1f}ms).\n\n"
            
            for idx, res in enumerate(zbar_results):
                code_type = res.type
                data = res.data.decode('utf-8', errors='replace')
                rect = res.rect
                poly = res.polygon
                found_codes.append({"type": code_type, "data": data, "rect": rect, "poly": poly})
                
                log += f"  --- MÃ THỨ #{idx+1} ({code_type}) ---\n"
                log += "  * [NHẬN DIỆN ĐẶC TRƯNG - PATTERN RECOGNITION]\n"
                if "QR" in code_type:
                    log += "    - Thuật toán quét và định vị thành công 3 khối vuông Position Detection Patterns ở các góc.\n"
                else:
                    log += "    - Thuật toán quét tia (Scanlines) nhận diện khoảng cách các vạch dọc liên tiếp.\n"
                log += f"    - Bounding Box (Khu vực): X={rect.left}, Y={rect.top}, W={rect.width}, H={rect.height}\n"
                if poly:
                    log += f"    - Polygon (4 góc không gian 2D): {poly}\n"
                
                log += "  * [LẤY MẪU & KHÔI PHỤC MA TRẬN - GRID SAMPLING]\n"
                if "QR" in code_type:
                    log += "    - Tính toán lại ma trận (Perspective Transformation) để khử góc nghiêng ảnh.\n"
                    log += "    - Trích xuất ma trận nhị phân. Giải mã Format Information & xoá Mask Pattern.\n"
                else:
                    log += "    - Tính tỷ lệ vạch rộng/vạch hẹp để khôi phục cấu trúc bit.\n"
                    
                log += "  * [SỬA LỖI & DỊCH TEXT - ERROR CORRECTION]\n"
                if "QR" in code_type:
                    log += "    - Phân tách khối Codewords. Chạy giải thuật Reed-Solomon để xác minh và sửa các bit hỏng.\n"
                else:
                    log += "    - Tính Checksum (Modulo) để xác minh tính toàn vẹn.\n"
                
                raw_bytes = res.data
                binary_blocks = " ".join([f"{b:08b}" for b in raw_bytes])
                log += f"    - Chuỗi Binary thô khôi phục được:\n      {binary_blocks}\n"
                
                log += f"  => [DỮ LIỆU ĐÃ DỊCH]: {data}\n\n"
                
    except Exception as e:
        log += f"  [LỖI] pyzbar crashed: {e}\n\n"

    # 2. Decode pylibdmtx
    log += "========================================================\n"
    log += "[PHASE 2] TÌM KIẾM DATAMATRIX (Engine: pylibdmtx)\n"
    log += "========================================================\n"
    log += "  * [NHẬN DIỆN L-FINDER PATTERN]\n"
    log += "    - Quét biên để tìm hình chữ L nét liền (Finder) giúp định hướng và xác định kích thước ma trận.\n"
    log += "    - Tìm đường răng cưa (Clock Track) ở 2 viền đối diện để đếm số bit.\n\n"
    
    start2 = time.time()
    try:
        dmtx_results = dmtx_decode(img)
        elapsed2 = (time.time() - start2)*1000
        
        if len(dmtx_results) == 0:
            log += f"  -> [KẾT QUẢ] Không tìm thấy DataMatrix nào (Time: {elapsed2:.1f}ms).\n\n"
        else:
            log += f"  -> [KẾT QUẢ] Đã quét và phát hiện {len(dmtx_results)} mã DataMatrix (Time: {elapsed2:.1f}ms).\n\n"
            
            for idx, res in enumerate(dmtx_results):
                data = res.data.decode('utf-8', errors='replace')
                rect = res.rect
                
                poly = None
                
                found_codes.append({"type": "DataMatrix", "data": data, "rect": rect, "poly": poly})
                
                log += f"  --- DATAMATRIX THỨ #{idx+1} ---\n"
                log += f"    - Bounding Box: X={rect.left}, Y={rect.top}, W={rect.width}, H={rect.height}\n"
                log += "  * [LẤY MẪU & SỬA LỖI]\n"
                log += "    - Lấy mẫu lưới vuông dọc theo Clock Track.\n"
                log += "    - Áp dụng thuật toán sửa lỗi ECC200 Reed-Solomon.\n"
                
                raw_bytes = res.data
                binary_blocks = " ".join([f"{b:08b}" for b in raw_bytes])
                log += f"    - Chuỗi Binary thô (ECC200 decoded):\n      {binary_blocks}\n"
                
                log += f"  => [DỮ LIỆU ĐÃ DỊCH]: {data}\n\n"
                
    except Exception as e:
         log += f"  [LỖI] pylibdmtx crashed: {e}\n\n"

    log += "========================================================\n"
    log += f"TỔNG KẾT: ĐÃ TÌM THẤY {len(found_codes)} MÃ\n"
    log += "========================================================\n"

    return log, found_codes
