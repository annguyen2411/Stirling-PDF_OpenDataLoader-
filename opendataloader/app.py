import os
import sys
import time
import shutil
import tempfile
import threading
import subprocess
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="OpenDataLoader-PDF Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INPUT_WATCH_DIR = Path("/shared/input")
OUTPUT_WATCH_DIR = Path("/shared/output")

def process_single_pdf(file_path: Path, output_dir: Path):
    """Bóc tách 1 file PDF bằng OpenDataLoader-PDF CLI"""
    output_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "opendataloader-pdf",
        str(file_path),
        "-o", str(output_dir),
        "-f", "markdown,json"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"OpenDataLoader failed: {res.stderr}")

def watch_folder_worker():
    """Luồng chạy ngầm theo dõi thư mục mạng chia sẻ /shared/input"""
    INPUT_WATCH_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_WATCH_DIR.mkdir(parents=True, exist_ok=True)
    
    file_sizes = {}
    while True:
        try:
            for item in INPUT_WATCH_DIR.iterdir():
                if item.is_file() and item.suffix.lower() == ".pdf" and not item.name.startswith("."):
                    current_size = item.stat().st_size
                    prev_size, stable_count = file_sizes.get(item.name, (0, 0))
                    
                    if current_size == prev_size and current_size > 0:
                        stable_count += 1
                    else:
                        stable_count = 0
                    
                    file_sizes[item.name] = (current_size, stable_count)
                    
                    # Nếu file ổn định sau 2 chu kỳ (>= 4 giây ghi file xong)
                    if stable_count >= 2:
                        print(f"[WatchFolder] Bắt đầu bóc tách: {item.name}", flush=True)
                        try:
                            process_single_pdf(item, OUTPUT_WATCH_DIR)
                            item.unlink() # Xóa file gốc sau khi xử lý thành công
                            print(f"[WatchFolder] Hoàn tất: {item.name} -> {OUTPUT_WATCH_DIR}", flush=True)
                        except Exception as e:
                            print(f"[WatchFolder] Lỗi bóc tách {item.name}: {e}", flush=True)
                        file_sizes.pop(item.name, None)
        except Exception as err:
            print(f"[WatchFolder] Error loop: {err}", flush=True)
        time.sleep(3)

# Khởi chạy luồng theo dõi thư mục ngầm
threading.Thread(target=watch_folder_worker, daemon=True).start()

HTML_PAGE = """<!DOCTYPE html>
<html lang="vi">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>OpenDataLoader-PDF | Bóc Tách Bảng Biểu & Dữ Liệu AI</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📊</text></svg>">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --border: #334155;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #ef4444;
      --primary-hover: #dc2626;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --success: #10b981;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: var(--bg); color: var(--text); min-height: 100vh; display: flex; flex-direction: column; }
    
    /* Header */
    header {
      background: rgba(30, 41, 59, 0.8);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 1rem 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      position: sticky;
      top: 0;
      z-index: 100;
    }
    .brand { display: flex; align-items: center; gap: 0.75rem; text-decoration: none; color: inherit; }
    .brand-icon {
      background: linear-gradient(135deg, #ef4444, #b91c1c);
      width: 38px; height: 38px; border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 20px; box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
    }
    .brand-title { font-weight: 800; font-size: 1.25rem; letter-spacing: -0.02em; }
    .brand-badge {
      background: rgba(239, 68, 68, 0.15); color: #f87171;
      border: 1px solid rgba(239, 68, 68, 0.3);
      font-size: 0.7rem; font-weight: 700; padding: 2px 8px; border-radius: 999px;
      text-transform: uppercase;
    }
    .nav-btn {
      display: inline-flex; align-items: center; gap: 0.5rem;
      background: #334155; color: #f8fafc; text-decoration: none;
      padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.875rem;
      transition: all 0.2s;
    }
    .nav-btn:hover { background: #475569; transform: translateY(-1px); }

    /* Main Container */
    main { max-width: 1200px; width: 100%; margin: 2rem auto; padding: 0 1.5rem; flex: 1; display: flex; flex-direction: column; gap: 2rem; }
    
    .hero { text-align: center; max-width: 760px; margin: 0 auto; }
    .hero h1 { font-size: 2.2rem; font-weight: 800; margin-bottom: 0.75rem; background: linear-gradient(to right, #f8fafc, #94a3b8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .hero p { color: var(--text-muted); font-size: 1.05rem; line-height: 1.5; }

    /* Dropzone */
    .upload-card {
      background: var(--card-bg); border: 2px dashed var(--border); border-radius: 16px;
      padding: 3rem 2rem; text-align: center; cursor: pointer; transition: all 0.25s ease;
      position: relative;
    }
    .upload-card:hover, .upload-card.dragover { border-color: var(--accent); background: rgba(59, 130, 246, 0.05); }
    .upload-icon { font-size: 3rem; margin-bottom: 1rem; }
    .upload-title { font-size: 1.25rem; font-weight: 700; margin-bottom: 0.5rem; }
    .upload-hint { color: var(--text-muted); font-size: 0.875rem; }
    input[type="file"] { display: none; }

    /* Action bar */
    .controls {
      display: flex; justify-content: center; align-items: center; gap: 1rem; flex-wrap: wrap;
    }
    .btn {
      background: var(--primary); color: white; border: none; padding: 0.75rem 1.75rem;
      border-radius: 10px; font-size: 1rem; font-weight: 700; cursor: pointer;
      display: inline-flex; align-items: center; gap: 0.5rem; transition: all 0.2s;
      box-shadow: 0 4px 14px rgba(239, 68, 68, 0.3);
    }
    .btn:hover:not(:disabled) { background: var(--primary-hover); transform: translateY(-1px); }
    .btn:disabled { opacity: 0.6; cursor: not-allowed; }

    /* Results */
    .result-section {
      display: none; background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px;
      overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    .result-header {
      background: rgba(15, 23, 42, 0.6); border-bottom: 1px solid var(--border);
      padding: 0.75rem 1.5rem; display: flex; justify-content: space-between; align-items: center;
      flex-wrap: wrap; gap: 1rem;
    }
    .tabs { display: flex; gap: 0.5rem; }
    .tab-btn {
      background: transparent; border: 1px solid transparent; color: var(--text-muted);
      padding: 0.5rem 1rem; border-radius: 8px; font-weight: 600; font-size: 0.875rem;
      cursor: pointer; transition: all 0.2s;
    }
    .tab-btn.active { background: #334155; color: white; border-color: var(--border); }
    .actions { display: flex; gap: 0.5rem; }
    .btn-action {
      background: #334155; color: white; border: none; padding: 0.5rem 1rem;
      border-radius: 8px; font-weight: 600; font-size: 0.85rem; cursor: pointer;
      display: inline-flex; align-items: center; gap: 0.4rem; transition: all 0.2s;
    }
    .btn-action:hover { background: #475569; }

    .result-body { padding: 2rem; max-height: 700px; overflow-y: auto; }
    .tab-content { display: none; }
    .tab-content.active { display: block; }

    /* Rendered Markdown Styling */
    .markdown-body { color: #e2e8f0; line-height: 1.7; font-size: 1rem; }
    .markdown-body h1, .markdown-body h2, .markdown-body h3 { color: #f8fafc; margin: 1.5rem 0 0.75rem; }
    .markdown-body h1 { border-bottom: 1px solid var(--border); padding-bottom: 0.5rem; font-size: 1.75rem; }
    .markdown-body h2 { font-size: 1.4rem; }
    .markdown-body p { margin-bottom: 1rem; }
    .markdown-body table {
      width: 100%; border-collapse: collapse; margin: 1.5rem 0; font-size: 0.95rem;
      background: rgba(15, 23, 42, 0.4); border-radius: 8px; overflow: hidden;
    }
    .markdown-body th, .markdown-body td {
      border: 1px solid var(--border); padding: 0.75rem 1rem; text-align: left;
    }
    .markdown-body th { background: rgba(51, 65, 85, 0.8); font-weight: 700; color: #f8fafc; }
    .markdown-body tr:nth-child(even) { background: rgba(30, 41, 59, 0.5); }
    .markdown-body tr:hover { background: rgba(59, 130, 246, 0.1); }
    pre {
      background: #0f172a; padding: 1.25rem; border-radius: 10px; overflow-x: auto;
      border: 1px solid var(--border); font-family: monospace; font-size: 0.9rem; color: #a5f3fc;
      white-space: pre-wrap; word-break: break-word;
    }

    /* Toast */
    .toast {
      position: fixed; bottom: 2rem; right: 2rem; background: var(--success); color: white;
      padding: 0.75rem 1.5rem; border-radius: 8px; font-weight: 600; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      display: none; animation: fadeIn 0.3s ease; z-index: 1000;
    }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    /* Spinner */
    .spinner {
      border: 3px solid rgba(255,255,255,0.2); border-top: 3px solid white;
      border-radius: 50%; width: 18px; height: 18px; animation: spin 0.8s linear infinite; display: none;
    }
    @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  </style>
</head>
<body>

  <header>
    <a href="#" class="brand">
      <div class="brand-icon">⚡</div>
      <div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span class="brand-title">OpenDataLoader PDF</span>
          <span class="brand-badge">AI Structured Parser</span>
        </div>
        <small style="color: var(--text-muted); font-size: 0.75rem;">Bóc tách bảng biểu & dữ liệu chuẩn AI/RAG</small>
      </div>
    </a>
    <a id="back-to-stirling" href="#" class="nav-btn">
      ← Quay lại Stirling PDF
    </a>
  </header>

  <main>
    <div class="hero">
      <h1>Bóc Tách Dữ Liệu PDF Chuẩn Cấu Trúc AI</h1>
      <p>Bảo toàn 100% cấu trúc <b>Bảng biểu (Tables)</b>, phân cột đọc <b>XY-Cut++</b>, trích xuất sang <b>Markdown / JSON</b> sạch sẽ để dán thẳng vào ChatGPT, Claude hoặc cơ sở dữ liệu tri thức RAG nội bộ.</p>
    </div>

    <div class="upload-card" id="dropzone">
      <input type="file" id="file-input" accept="application/pdf">
      <div class="upload-icon">📄</div>
      <div class="upload-title" id="file-name-display">Kéo thả file PDF vào đây hoặc bấm để chọn</div>
      <div class="upload-hint">Hỗ trợ các báo cáo tài chính, hợp đồng, tài liệu nhiều cột và bảng biểu phức tạp</div>
    </div>

    <div class="controls">
      <button class="btn" id="convert-btn" disabled>
        <span class="spinner" id="loading-spinner"></span>
        <span id="btn-text">Bắt đầu Bóc Tách Dữ Liệu</span>
      </button>
    </div>

    <div class="result-section" id="result-container">
      <div class="result-header">
        <div class="tabs">
          <button class="tab-btn active" onclick="switchTab('rendered')">📑 Xem trước định dạng & Bảng biểu</button>
          <button class="tab-btn" onclick="switchTab('raw')">📝 Mã Markdown (.md)</button>
          <button class="tab-btn" onclick="switchTab('json')">📊 Cấu trúc JSON (.json)</button>
        </div>
        <div class="actions">
          <button class="btn-action" onclick="copyResult()">📋 Sao chép Markdown</button>
          <button class="btn-action" onclick="downloadMd()">📥 Tải .md</button>
          <button class="btn-action" onclick="downloadJson()">📥 Tải .json</button>
        </div>
      </div>
      <div class="result-body">
        <div id="tab-rendered" class="tab-content active markdown-body"></div>
        <div id="tab-raw" class="tab-content"><pre><code id="raw-markdown-code"></code></pre></div>
        <div id="tab-json" class="tab-content"><pre><code id="raw-json-code"></code></pre></div>
      </div>
    </div>
  </main>

  <div class="toast" id="toast">Đã sao chép vào bộ nhớ tạm!</div>

  <script>
    // Link quay lại Stirling PDF trên cùng máy chủ
    document.getElementById('back-to-stirling').href = window.location.protocol + '//' + window.location.hostname + ':9280';

    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const fileNameDisplay = document.getElementById('file-name-display');
    const convertBtn = document.getElementById('convert-btn');
    const btnText = document.getElementById('btn-text');
    const spinner = document.getElementById('loading-spinner');
    const resultContainer = document.getElementById('result-container');
    const toast = document.getElementById('toast');

    let currentFile = null;
    let extractedMarkdown = "";
    let extractedJson = "";
    let baseFileName = "document";

    dropzone.addEventListener('click', () => fileInput.click());
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.classList.remove('dragover');
      if (e.dataTransfer.files.length) handleFile(e.dataTransfer.files[0]);
    });
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) handleFile(fileInput.files[0]);
    });

    function handleFile(file) {
      if (!file.name.toLowerCase().endsWith('.pdf')) {
        alert('Vui lòng chọn tệp có định dạng .pdf!');
        return;
      }
      currentFile = file;
      baseFileName = file.name.replace(/\\.[^/.]+$/, "");
      fileNameDisplay.innerHTML = `<strong>Tệp đã chọn:</strong> ${file.name} (${(file.size / (1024*1024)).toFixed(2)} MB)`;
      convertBtn.disabled = false;
    }

    convertBtn.addEventListener('click', async () => {
      if (!currentFile) return;
      convertBtn.disabled = true;
      spinner.style.display = 'inline-block';
      btnText.innerText = 'Đang bóc tách bảng biểu & văn bản...';
      resultContainer.style.display = 'none';

      const formData = new FormData();
      formData.append('file', currentFile);

      try {
        const response = await fetch('/api/convert', { method: 'POST', body: formData });
        const data = await response.json();

        if (!response.ok || !data.success) {
          throw new Error(data.detail || 'Lỗi bóc tách tài liệu');
        }

        extractedMarkdown = data.markdown || "";
        extractedJson = JSON.stringify(data.json_data || {}, null, 2);

        document.getElementById('tab-rendered').innerHTML = marked.parse(extractedMarkdown);
        document.getElementById('raw-markdown-code').textContent = extractedMarkdown;
        document.getElementById('raw-json-code').textContent = extractedJson;

        resultContainer.style.display = 'block';
        resultContainer.scrollIntoView({ behavior: 'smooth' });
      } catch (err) {
        alert('Xử lý thất bại: ' + err.message);
      } finally {
        convertBtn.disabled = false;
        spinner.style.display = 'none';
        btnText.innerText = 'Bắt đầu Bóc Tách Dữ Liệu';
      }
    });

    function switchTab(tabName) {
      document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      if (tabName === 'rendered') {
        document.querySelectorAll('.tab-btn')[0].classList.add('active');
        document.getElementById('tab-rendered').classList.add('active');
      } else if (tabName === 'raw') {
        document.querySelectorAll('.tab-btn')[1].classList.add('active');
        document.getElementById('tab-raw').classList.add('active');
      } else {
        document.querySelectorAll('.tab-btn')[2].classList.add('active');
        document.getElementById('tab-json').classList.add('active');
      }
    }

    function showToast(msg) {
      toast.innerText = msg;
      toast.style.display = 'block';
      setTimeout(() => { toast.style.display = 'none'; }, 2000);
    }

    function copyResult() {
      navigator.clipboard.writeText(extractedMarkdown).then(() => {
        showToast('Đã sao chép Markdown vào bộ nhớ tạm!');
      });
    }

    function downloadMd() {
      const blob = new Blob([extractedMarkdown], { type: 'text/markdown;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${baseFileName}.md`;
      a.click();
    }

    function downloadJson() {
      const blob = new Blob([extractedJson], { type: 'application/json;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${baseFileName}.json`;
      a.click();
    }
  </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index_page():
    return HTML_PAGE

@app.post("/api/convert")
async def convert_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Chỉ hỗ trợ tệp định dạng .pdf")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        input_file = temp_path / file.filename
        output_dir = temp_path / "output"
        
        with open(input_file, "wb") as f:
            shutil.copyfileobj(file.file, f)
            
        try:
            process_single_pdf(input_file, output_dir)
            
            # Đọc kết quả markdown và json
            md_content = ""
            json_content = {}
            
            for out_file in output_dir.glob("*.md"):
                md_content = out_file.read_text(encoding="utf-8")
                break
                
            for out_file in output_dir.glob("*.json"):
                import json
                try:
                    json_content = json.loads(out_file.read_text(encoding="utf-8"))
                except Exception:
                    pass
                break
                
            return {
                "success": True,
                "filename": file.filename,
                "markdown": md_content,
                "json_data": json_content
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
