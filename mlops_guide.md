# Hướng Dẫn Toàn Diện Về MLOps (Machine Learning Operations)

MLOps (Machine Learning Operations) là một tập hợp các phương pháp và nguyên tắc thực hành kết hợp Học máy (Machine Learning), Kỹ thuật dữ liệu (Data Engineering) và DevOps nhằm triển khai và duy trì các hệ thống ML trong môi trường sản xuất một cách đáng tin cậy và hiệu quả.

Dưới đây là danh sách chi tiết những thứ cần thiết để xây dựng một hệ thống MLOps hoàn chỉnh.

---

## 1. Vòng Đời Cốt Lõi Của MLOps (MLOps Lifecycle)

Một hệ thống MLOps trưởng thành cần tự động hoá và giám sát được 4 giai đoạn chính sau:

### A. Data Engineering (Xử lý dữ liệu)
- **Data Ingestion:** Thu thập dữ liệu từ các nguồn (Database, API, Kafka...).
- **Data Validation & Preprocessing:** Làm sạch, xác thực định dạng dữ liệu, xử lý nhiễu.
- **Feature Store:** Lưu trữ các đặc trưng (features) đã được tính toán để dùng chung giữa các model nhằm tránh tính toán lại.

### B. ML Model Engineering (Phát triển mô hình)
- **Model Training:** Huấn luyện mô hình (bao gồm cả phân bổ tài nguyên GPU/CPU).
- **Hyperparameter Tuning:** Tự động hoá quá trình dò tìm siêu tham số.
- **Model Registry (Quản lý phiên bản):** Lưu trữ mã nguồn (code), tham số (hyperparameters), kiến trúc và trọng số (weights) của từng lần huấn luyện.

### C. Deployment & Serving (Triển khai)
- **Containerization:** Đóng gói mô hình thành các Docker Container.
- **Serving:** Đưa mô hình lên môi trường Production (Real-time API bằng FastAPI/Flask, hoặc Batch Inference).
- **CI/CD Pipelines:** Tự động kiểm thử mã nguồn và deploy mô hình mới khi vượt qua các ngưỡng chất lượng (Quality thresholds).

### D. Monitoring & Maintenance (Giám sát)
- **Data Drift Monitoring:** Giám sát xem phân phối dữ liệu đầu vào có bị thay đổi so với lúc training không.
- **Model Drift (Concept Drift):** Giám sát xem mô hình có bị suy giảm độ chính xác theo thời gian không.
- **Alerting:** Gửi cảnh báo (Slack/Email) và kích hoạt tự động Retraining (Huấn luyện lại) khi mô hình xuống cấp.

---

## 2. Đặc thù: Data Ingestion Từ Máy Móc Xưởng Sản Xuất (IIoT)

Thu thập dữ liệu từ máy móc công nghiệp (Industrial IoT) phức tạp hơn rất nhiều so với Web/App thông thường. Bạn sẽ phải đối mặt với các máy móc cũ (Legacy machines), giao thức độc quyền, môi trường mạng cô lập và dữ liệu thời gian thực (Real-time) cực lớn.

Dưới đây là kiến trúc chuẩn để **Ingest dữ liệu từ xưởng (Shop Floor) lên hệ thống ML (Top Floor)**:

### 2.1. Cấp độ Máy móc & Cảm biến (Edge Layer)
- **Cảm biến (Sensors):** Gắn thêm cảm biến (Nhiệt độ, Độ rung, Camera quang học) nếu máy cũ không tự xuất được dữ liệu.
- **PLC/CNC:** Các bộ điều khiển máy (Siemens, Mitsubishi, Fanuc...).
- **Giao thức Công nghiệp:** Máy móc không nói chung một ngôn ngữ. Chúng sử dụng `Modbus TCP/RTU`, `OPC UA`, `PROFINET`, `MQTT`, `MTConnect`.

### 2.2. Lớp Cổng kết nối (Edge Gateway Layer)
- **Edge Devices (Industrial PC / Raspberry Pi / HMI):** Máy tính công nghiệp đặt cạnh dây chuyền.
- **Phần mềm Gateway (Kepware / Ignition / Node-RED):** Phần mềm cài trên Edge Device để làm nhiệm vụ "Phiên dịch". Nó thu thập dữ liệu từ hàng chục giao thức PLC khác nhau (Modbus, OPC UA) và **chuẩn hoá** chúng thành một format duy nhất (thường là JSON).
- **Lọc & Nén tại nguồn (Edge Computing):** Không nên gửi toàn bộ dữ liệu thô (ví dụ: gửi liên tục 1000 mẫu độ rung/giây) lên server. Gateway sẽ tính toán sơ bộ (Trung bình, Max, Min) hoặc chỉ gửi khi có sự kiện bất thường để tiết kiệm băng thông.

### 2.3. Lớp Truyền tải Thời gian thực (Message Broker Layer)
- **MQTT Broker (Eclipse Mosquitto / EMQX):** Cực kỳ phổ biến trong nhà máy. Gateway sẽ `Publish` dữ liệu chuẩn hoá qua giao thức MQTT. MQTT rất nhẹ, hỗ trợ mạng chập chờn.
- **Apache Kafka / RabbitMQ:** Nếu nhà máy có hàng nghìn máy móc, dữ liệu đổ về khổng lồ, Kafka sẽ đứng sau MQTT để hứng (buffer) luồng dữ liệu stream này, đảm bảo không mất gói tin nào ngay cả khi Database bị sập.

### 2.4. Lớp Lưu trữ & Tiêu thụ (Data Lake / Data Warehouse Layer)
Kafka sẽ stream dữ liệu về 2 nhánh chính cho MLOps:
- **Hot Path (Xử lý ngay):** Dữ liệu chạy vào các công cụ stream processing (Apache Flink / Spark Streaming) để đưa qua **ML Model đang Serving** nhằm phát hiện lỗi tức thời (Ví dụ: Cảnh báo gãy mũi khoan ngay lập tức).
- **Cold Path (Lưu trữ để Training):** Dữ liệu được ghi vào các Time-Series Database (như `InfluxDB`, `TimescaleDB`) hoặc Data Lake (như Amazon S3, Hadoop) để Data Scientist lấy ra phân tích và train/retrain mô hình.

> **Ví dụ tóm tắt luồng dữ liệu:**
> Cảm biến nhiệt độ $\rightarrow$ PLC (Modbus) $\rightarrow$ Raspberry Pi (chạy Node-RED) $\rightarrow$ Chuyển thành JSON $\rightarrow$ Gửi qua MQTT/Kafka $\rightarrow$ InfluxDB (Lưu trữ) + FastAPI Model (Dự đoán mài mòn).

---

## 3. Các Công Cụ Tiêu Biểu Theo Từng Nhóm MLOps Stack

Để xây dựng các bước trên, bạn sẽ cần phối hợp nhiều công cụ khác nhau:

### 3.1. Quản lý Phiên Bản (Version Control)
- **Code:** Git (GitHub, GitLab, Bitbucket).
- **Data & Model Weights:** **DVC (Data Version Control)**. Giúp quản lý các file dữ liệu khổng lồ bằng Git-like syntax.

### 3.2. Theo dõi Huấn luyện & Đăng ký Mô hình (Experiment Tracking & Registry)
- **MLflow:** Nền tảng phổ biến nhất để tracking tham số, metrics và lưu trữ Model Registry.
- **Weights & Biases (W&B):** Công cụ SaaS tuyệt vời cho giao diện trực quan và quản lý hyperparameter.
- **Neptune.ai / Comet.ml:** Các giải pháp thay thế W&B.

### 3.3. Quản lý Luồng Công Việc (Orchestration & Pipelines)
- **Apache Airflow:** Điều phối các batch job và data pipeline phức tạp.
- **Kubeflow Pipelines:** Dành riêng cho hệ sinh thái Kubernetes, rất mạnh cho ML.
- **Prefect / Dagster:** Các lựa chọn điều phối Data/ML hiện đại, dễ code bằng Python hơn Airflow.

### 3.4. Lưu trữ Đặc trưng (Feature Store)
- **Feast:** Open-source Feature Store phổ biến nhất.
- **Hopsworks:** Nền tảng chuyên biệt hỗ trợ cả Data và ML.

### 3.5. Triển khai & Khai thác (Deployment / Serving)
- **BentoML:** Framework tuyệt vời để đóng gói và serving mô hình ML.
- **TensorFlow Serving / TorchServe / Triton Inference Server:** Tối ưu hóa serving cho các framework cụ thể.
- **FastAPI / Flask:** Tự viết REST API (phù hợp cho các dự án nhỏ/vừa).
- **Docker & Kubernetes:** Đóng gói và quản lý quy mô (Scaling) theo lượng request.

### 3.6. Giám sát (Monitoring)
- **Evidently AI / NannyML:** Chuyên dùng để giám sát Data Drift và Model Drift.
- **Prometheus & Grafana:** Giám sát tài nguyên phần cứng (CPU, GPU, RAM) và độ trễ (Latency).

---

## 4. Các Cấp Độ Trưởng Thành Của MLOps (Theo Google)

Bạn không cần áp dụng tất cả các công cụ trên ngay từ đầu. Hãy đi theo 3 cấp độ:

- **MLOps Level 0 (Manual):** Mọi thứ làm bằng tay trên Jupyter Notebook. Không có CI/CD. Đẩy mô hình lên Production thủ công. (Đa số các team mới bắt đầu ở đây).
- **MLOps Level 1 (ML Pipeline Automation):** Tự động hóa quá trình huấn luyện (Continuous Training - CT). Khi có dữ liệu mới, pipeline tự động chạy để train và ra mô hình mới.
- **MLOps Level 2 (CI/CD Pipeline Automation):** Hoàn toàn tự động. Cập nhật mã nguồn sẽ tự động kích hoạt CI/CD để build, test và deploy model lên môi trường thực tế một cách an toàn.

---

## 5. Các Vai Trò (Roles) Cần Có Trong Một Team MLOps
- **Data Engineer:** Xây dựng pipeline dữ liệu, Data Warehouse.
- **Data Scientist:** Phân tích dữ liệu, thiết kế thuật toán, thử nghiệm model.
- **ML Engineer:** Đưa model của Data Scientist từ môi trường lab ra Production, tối ưu hóa code và thiết lập hạ tầng serving.
- **DevOps/Platform Engineer:** Quản trị hạ tầng Cloud (AWS/GCP), Kubernetes, thiết lập CI/CD.

> **Tóm lại:** Để bắt đầu với MLOps, bạn nên học và sử dụng thành thạo combo cơ bản: **Git + DVC (Data versioning) + MLflow (Tracking) + Docker + FastAPI (Serving).**
