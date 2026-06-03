# Advanced Barcode & Matrix Code Studio

Một ứng dụng Desktop mạnh mẽ được viết bằng Python (sử dụng thư viện giao diện hiện đại `CustomTkinter`). Ứng dụng này không chỉ đóng vai trò là một phần mềm tạo (Encode) và giải mã (Decode) các loại mã 1D/2D thông thường, mà còn là một **Công cụ học tập & minh hoạ thuật toán** chuyên sâu, cho phép người dùng nhìn thấy từng bước biến đổi dữ liệu đằng sau hậu trường.

## 🌟 Các tính năng nổi bật

### 1. Hệ thống Mã Hoá (Encode) Siêu Chi Tiết
Hỗ trợ sinh mã động với các chuẩn phổ biến:
- **Barcode 1D:** Code 128, Code 39, EAN-13.
- **QR Code:** Cho phép tuỳ chỉnh linh hoạt 4 mức độ sửa lỗi (Error Correction: L - 7%, M - 15%, Q - 25%, H - 30%).
- **DataMatrix (ECC 200):** Tự động chọn ma trận vuông tối ưu.

**Minh bạch Thuật toán:**
Bảng *Transformation Log* sẽ hiển thị thời gian thực tất cả các bước tính toán: 
- Quá trình quy đổi ký tự sang ASCII.
- Trích xuất luồng nhị phân (Binary Stream).
- Thêm bytes đệm (Padding) và khởi tạo giá trị nội suy sửa lỗi Reed-Solomon Check Bytes.
- Cách thuật toán sắp xếp bit trên không gian lưới.

### 2. Khám phá Lưới Tương tác (DataMatrix Explorer)
Đây là tính năng độc quyền của phần mềm giúp bạn thấu hiểu thuật toán *Diagonal Fill* (điền chéo) của DataMatrix:
- Bằng cách can thiệp sâu vào engine lõi (sử dụng *Monkey Patching*), hệ thống theo dõi tọa độ rơi của từng điểm ảnh (module).
- Mở ra một màn hình lưới Tương tác: Bấm vào một điểm đen/trắng bất kỳ, phần mềm sẽ **highlight khối 8-bit (Codeword)** thuộc về điểm đó bằng màu Xanh, làm nổi bật Điểm Neo (Anchor Bit 0) bằng màu Đỏ, và dịch ngược 8 bit đó ra giá trị Thập phân / Hex.

### 3. Hệ thống Giải Mã (Decode) Bậc Cao
Tích hợp cùng lúc 2 Engine giải mã mạnh nhất: `pyzbar` và `pylibdmtx`.
- **Đọc vạn vật:** Hỗ trợ tải mọi định dạng ảnh, tự động nhận diện và quét tất cả QR, Barcode, DataMatrix có trong hình.
- **Vẽ Bounding Box:** Khoanh vùng chính xác toạ độ của mã trên ảnh Preview (Đường viền xanh lá cho Polygon, Xanh dương cho Rect).
- **Phân tích lý thuyết thị giác máy tính:** Bảng Log Giải mã không chỉ hiện kết quả, mà còn mô tả lại các pha xử lý ảnh kỹ thuật số (Binarization, Edge Detection, Perspective Transform) và trích xuất trực tiếp **chuỗi Raw Bytes** (các khối 8-bit) đọc được từ bức ảnh.
- **Trích xuất ngược:** Khi quét ra DataMatrix, người dùng có thể bấm nút Trích xuất ngược để đưa kết quả vào DataMatrix Explorer và phân tích 8-bit trên lưới chuẩn.

---

## 🛠 Yêu cầu Hệ thống & Cài đặt

Dự án được xây dựng trên **Python 3.x**.

### 1. Cài đặt thư viện Python
Chạy lệnh sau tại thư mục gốc của dự án:
```bash
pip install -r requirements.txt
```
*(Bao gồm: `customtkinter`, `pillow`, `python-barcode`, `qrcode`, `pystrich`, `pyzbar`, `pylibdmtx`, `setuptools`)*

### 2. Cài đặt Thư viện lõi C (Rất quan trọng)
Vì phần mềm sử dụng thuật toán Computer Vision để xử lý ảnh, bạn cần cài đặt các thư viện hệ thống cho OS tương ứng.

**Đối với macOS:**
```bash
brew install zbar libdmtx
```
*(Nếu bạn dùng máy Mac chip Apple Silicon M1/M2/M3, do Python mặc định tìm thư viện ở `/usr/local/lib`, bạn cần tạo đường dẫn tắt (Symlink) để kết nối thư viện Homebrew với hệ thống bằng lệnh sau):*
```bash
mkdir -p ~/lib
ln -sf /opt/homebrew/lib/libzbar.dylib ~/lib/libzbar.dylib
ln -sf /opt/homebrew/lib/libdmtx.dylib ~/lib/libdmtx.dylib
```

**Đối với Ubuntu / Debian:**
```bash
sudo apt-get install libzbar0 libdmtx0b
```

**Đối với Windows:**
Thông thường `pyzbar` và `pylibdmtx` đã kèm sẵn các file `.dll` cần thiết bên trong gói cài đặt pip, nên bạn không cần cài thêm.

---

## 🚀 Hướng dẫn sử dụng

Chạy phần mềm bằng lệnh:
```bash
python3 app.py
```

### Chế độ Mã Hoá (Encode Tab)
1. Gõ đoạn văn bản / dữ liệu cần mã hoá vào ô Input.
2. Chọn loại định dạng (Barcode, DataMatrix, QR Code) ở thanh radio.
3. Nếu chọn QR hoặc Barcode, một menu cài đặt phụ sẽ hiện ra để bạn chọn chuẩn loại/mức độ sửa lỗi.
4. Bấm **GENERATE CODE** để phần mềm tính toán.
5. Quan sát quá trình biến đổi tại bảng Log bên trái, và hình ảnh kết quả ở bên phải. (Sử dụng các nút Save để lưu hình/log).
6. Nếu chọn DataMatrix, bấm nút **Mở Lưới DataMatrix Tương tác** để trải nghiệm dò bit 8-bit trực quan.

### Chế độ Giải Mã (Decode Tab)
1. Chuyển sang Tab "Giải Mã".
2. Bấm **Tải Ảnh Cần Dịch** và chọn file hình ảnh mã vạch trong máy của bạn.
3. Bấm **GIẢI MÃ TỰ ĐỘNG**.
4. Chờ phần mềm chạy Engine phân tích. Kết quả toạ độ, phân tích bit và văn bản giải mã sẽ hiện ở khung Log. Hình ảnh cũng sẽ được vẽ viền bao quanh các mã quét được.
5. Nếu mã quét được là DataMatrix, nút **Trích xuất lưới 8-bit** sẽ phát sáng để bạn có thể mở Explorer nghiên cứu khối mã.

### Chế độ Xử Lý Ảnh (Process Tab)
1. Chuyển sang Tab "Xử Lý Ảnh".
2. Tải ảnh lên và tinh chỉnh các thông số: độ sáng, độ tương phản, làm mờ/làm nét, nhị phân hoá (Thresholding) hoặc hình thái học.
3. Bấm **CHUYỂN SANG GIẢI MÃ** để đưa ảnh đã xử lý sang bộ giải mã để tăng khả năng đọc mã mờ/hỏng.

### Chế độ Tài Liệu (Docs Tab)
1. Chuyển sang Tab "Tài Liệu".
2. Đọc các tài liệu kỹ thuật về cấu trúc, Mask Pattern, và cơ chế của các loại mã vạch (Barcode 1D, QR, DataMatrix).

---

## 📁 Cấu trúc thư mục

- `app.py`: Tệp thực thi chính, chứa toàn bộ logic xử lý giao diện UI và tích hợp các module thuật toán.
- `plan.md`: Tài liệu đặc tả kỹ thuật, phân tích chi tiết quy trình hoạt động nội bộ và kiến trúc dự án.
- `requirements.txt`: Danh sách các package Python cần thiết.
- `README.md`: Tài liệu hướng dẫn sử dụng này.
