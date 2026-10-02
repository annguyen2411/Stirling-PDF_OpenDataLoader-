# Stirling-PDF & OpenDataLoader-PDF (All-in-One Office Suite)

Giải pháp tự lưu trữ (Self-hosted) toàn diện dành cho văn phòng và doanh nghiệp: Kết hợp giữa **Stirling-PDF** (xử lý mọi tác vụ PDF) và **OpenDataLoader-PDF** (bóc tách bảng biểu, dữ liệu có cấu trúc sang Markdown/JSON chuẩn AI & RAG).

---

## 🚀 Tính năng nổi bật

### 1. Stirling-PDF (Cổng `9280`)
- **Tối giản cho khối văn phòng**: Ghim sẵn 6 công cụ thiết yếu lên thanh ưu tiên (Gộp, Tách, Nén, Chuyển đổi Office/PDF, Ký số, OCR).
- **Giao diện Tiếng Việt 100%**: Mặc định ngôn ngữ tiếng Việt (`vi_VN`).
- **Hỗ trợ file lớn & dọn rác tự động**: Cho phép tải tệp lên tới 500 MB; tự động dọn rác và file tạm mỗi 15 phút.
- **OCR Tiếng Việt & Tiếng Anh**: Tích hợp sẵn `vie.traineddata` chất lượng cao.
- **Thư mục mạng tự động OCR (Watch Folder)**: Thả file scan vào `Scan-In`, nhận kết quả nhận diện văn bản tại `Scan-Out`.

### 2. OpenDataLoader-PDF (Cổng `9281`)
- **Bóc tách cấu trúc tài liệu AI**: Phân tích thứ tự đọc chuẩn `XY-Cut++`, bảo toàn 100% định dạng bảng biểu phức tạp.
- **Trực quan hóa tức thì (Visual Web UI)**:
  - Xem trước bảng biểu và nội dung đã render chuẩn Markdown.
  - Xem trực tiếp mã nguồn Markdown (`.md`) và cây cấu trúc JSON (`.json`).
  - 1 chạm sao chép nhanh vào clipboard để dán sang ChatGPT, Claude, DeepSeek hoặc nạp vào Knowledge Base RAG.
  - Tải file `.md` và `.json` về máy tính.
- **Tự động hóa qua thư mục chia sẻ LAN (Watch Folder)**: Thả file PDF vào `PDF-To-Markdown-In`, tự động trích xuất file `.md` và `.json` sang `PDF-To-Markdown-Out`.
- **Liên kết 2 chiều**: Chuyển đổi nhanh qua lại giữa Stirling-PDF và OpenDataLoader-PDF chỉ với 1 click.

---

## 🛠️ Hướng dẫn cài đặt & Khởi chạy

### Yêu cầu hệ thống
- Đã cài đặt [Docker](https://www.docker.com/) & Docker Compose.
- RAM khuyến nghị: Tối thiểu 4GB - 8GB.

### Khởi động hệ thống
1. Clone repository về máy:
   ```bash
   git clone https://github.com/annguyen2411/Stirling-PDF_OpenDataLoader-.git
   cd Stirling-PDF_OpenDataLoader-
   ```

2. Khởi chạy toàn bộ dịch vụ:
   ```bash
   docker compose up -d
   ```
   *(Hoặc trên Windows, bạn chỉ cần nháy đúp vào tệp `run.bat` và chọn số `1`)*.

---

## 🌐 Địa chỉ truy cập

| Dịch vụ | Máy chủ (Localhost) | Mạng LAN nội bộ | Internet (Cloudflare Tunnel) |
| :--- | :--- | :--- | :--- |
| **Stirling-PDF** | `http://localhost:9280` | `http://<IP_MAY_CHU>:9280` | `https://pdf.techhave.com` |
| **OpenDataLoader-PDF** | `http://localhost:9281` | `http://<IP_MAY_CHU>:9281` | `https://ai-pdf.techhave.com` |

---

## 🔒 Cấu hình truy cập Internet (Cloudflare Tunnel)

Hệ thống tích hợp sẵn dịch vụ `cloudflared` giúp xuất bản ứng dụng ra Internet an toàn mà không cần mở cổng modem:
1. Sao chép `.env.example` thành `.env`:
   ```bash
   cp .env.example .env
   ```
2. Điền mã token của Cloudflare Tunnel vào:
   ```env
   CLOUDFLARE_TUNNEL_TOKEN=eyJh...
   ```
3. Khởi động dịch vụ tunnel:
   ```bash
   docker compose up -d cloudflared
   ```


## 📁 Thư mục tự động hóa qua mạng LAN

Chạy tệp `chia-se-thu-muc.bat` với quyền **Run as Administrator** để chia sẻ các thư mục sau qua mạng nội bộ cho nhân viên:

1. **Nhận diện chữ (OCR tự động)**:
   - Thả file: `\\<IP_MAY_CHU>\Scan-In`
   - Nhận file: `\\<IP_MAY_CHU>\Scan-Out`

2. **Bóc tách bảng biểu & Markdown AI**:
   - Thả file: `\\<IP_MAY_CHU>\PDF-To-Markdown-In`
   - Nhận file: `\\<IP_MAY_CHU>\PDF-To-Markdown-Out`

---

## ⚙️ Cấu trúc thư mục

```text
├── data/
│   ├── customFiles/       # Giao diện tùy biến, logo và liên kết
│   ├── extraConfigs/      # Cấu hình hệ thống Stirling-PDF (settings.yml)
│   ├── logs/              # Nhật ký hoạt động
│   └── trainingData/      # Bộ dữ liệu OCR Tesseract (vie.traineddata)
├── opendataloader/
│   ├── Dockerfile         # Dockerfile cho OpenDataLoader Service (Python 3.11 + Java 21)
│   └── app.py             # FastAPI Server, Visual Web UI & Watchfolder Worker
├── pipeline/
│   ├── Scan-In/           # Thư mục nạp OCR tự động
│   ├── Scan-Out/          # Thư mục kết quả OCR
│   ├── PDF-To-Markdown-In/# Thư mục nạp trích xuất AI
│   └── PDF-To-Markdown-Out# Thư mục kết quả Markdown & JSON
├── chia-se-thu-muc.bat    # Script chia sẻ thư mục mạng LAN (Windows)
├── run.bat                # Trình quản lý khởi động / cập nhật dịch vụ
└── docker-compose.yml     # Khởi chạy toàn bộ hệ thống
```
