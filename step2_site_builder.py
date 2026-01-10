import csv
import os
import shutil
import re

# ==========================================
# 1. Michael 核心配置区
# ==========================================
INPUT_CSV = "niche_data.csv"
OUTPUT_DIR = "dist"
LIMIT_PAGES = 500

# Michael 真实支付链接
PAYHIP_LINK = "https://payhip.com/b/HSDxs"
BASE_URL = "https://grich-utilitytool.pages.dev"

# 行业法律映射表
LAW_DATABASE = {
    "lawyer": "ABA Model Rules of Professional Conduct 2024",
    "doctor": "HIPAA Privacy Rule (45 CFR Part 160)",
    "nurse": "Nursing Practice Act",
    "teacher": "FERPA Compliance",
    "accountant": "SOX Standards",
    "default": "Standard Compliance"
}

# ==========================================
# 2. HTML 模板 (V5.2 强力加载修复版)
# ==========================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} - Michael Expert System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- V5.2 核心修复：双重 CDN 冗余加载 PDF-Lib (解决免费功能报错) -->
    <script src="https://unpkg.com/pdf-lib@1.17.1/dist/pdf-lib.min.js" onerror="this.src='https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/dist/pdf-lib.min.js'"></script>
    
    <!-- jsPDF 依然保留双重备份 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js" onerror="this.src='https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js'"></script>

    <style>
        .drop-active { border-color: #4f46e5 !important; background-color: #f5f3ff !important; }
        .animate-in { animation: fadeIn 0.3s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        button:disabled { opacity: 0.5; cursor: not-allowed; filter: grayscale(100%); }
        .hidden { display: none; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen font-sans text-slate-900">
    <nav class="bg-white border-b border-slate-200 py-4 shadow-sm">
        <div class="max-w-5xl mx-auto px-4 flex justify-between items-center">
            <span class="font-black text-2xl text-indigo-600 tracking-tighter uppercase">Grich Tool</span>
            <div class="flex items-center space-x-2">
                <span id="status-dot" class="h-2 w-2 bg-yellow-500 rounded-full animate-pulse"></span>
                <span id="status-text" class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Loading Engine...</span>
            </div>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-4 py-16">
        <div class="text-center mb-16">
            <h1 class="text-5xl font-black text-slate-900 mb-6 tracking-tight leading-tight">{{h1}}</h1>
            <p class="text-xl text-slate-500 max-w-2xl mx-auto">{{description}}</p>
        </div>

        <div class="bg-white rounded-[2.5rem] shadow-2xl p-2 border border-slate-100">
            <div class="p-10">
                <!-- 拖拽区 -->
                <div id="drop-zone" class="relative border-2 border-dashed border-slate-200 rounded-3xl p-16 text-center transition-all cursor-pointer hover:border-indigo-400 hover:bg-slate-50 group">
                    <input type="file" id="pdf-input" class="hidden" accept="application/pdf">
                    
                    <div id="upload-ui">
                        <div class="w-20 h-20 bg-indigo-50 text-indigo-600 rounded-3xl flex items-center justify-center mx-auto mb-6">
                            <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                        </div>
                        <p class="text-2xl font-bold text-slate-700">Click to {{action}}</p>
                        <p class="text-slate-400 mt-3 italic uppercase text-xs tracking-widest font-bold">Free Tool for {{profession}}s</p>
                    </div>

                    <div id="file-ready-ui" class="hidden animate-in">
                        <div class="w-20 h-20 bg-green-50 text-green-600 rounded-3xl flex items-center justify-center mx-auto mb-6">
                            <svg class="w-10 h-10" fill="currentColor" viewBox="0 0 20 20"><path d="M9 2a2 2 0 00-2 2v12a2 2 0 002 2h2a2 2 0 002-2V4a2 2 0 00-2-2H9z" /></svg>
                        </div>
                        <p id="ready-file-name" class="text-2xl font-bold text-slate-800 truncate px-8"></p>
                    </div>
                </div>

                <!-- 动态功能区 -->
                <div id="action-controls" class="mt-8 hidden">
                    <div id="encrypt-input" class="hidden mb-4">
                        <input type="password" id="pdf-password" placeholder="Enter Password to Protect PDF" class="w-full p-4 border rounded-xl text-center bg-slate-50 focus:ring-2 focus:ring-indigo-500 outline-none">
                    </div>
                    
                    <button id="run-tool-btn" disabled class="w-full bg-slate-900 text-white py-6 rounded-3xl font-black text-xl hover:bg-indigo-600 transition-all shadow-xl">
                        Wait for Engine...
                    </button>
                </div>

                <!-- 结果区 -->
                <div id="result-ui" class="hidden mt-10 border-t pt-10 animate-in">
                    <!-- 免费下载 -->
                    <div class="bg-green-50 border border-green-100 p-6 rounded-3xl mb-8 flex items-center justify-between">
                        <div>
                            <h4 class="text-green-800 font-bold text-lg">Task Complete!</h4>
                            <p class="text-green-600 text-sm">Your file has been processed locally.</p>
                        </div>
                        <button id="free-download-btn" class="bg-green-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-green-700 transition-all shadow-md flex items-center">
                            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                            Download Free
                        </button>
                    </div>
                    
                    <!-- 专家审计转化 -->
                    <div class="bg-indigo-50 border border-indigo-100 p-8 rounded-[2rem]">
                        <div class="flex items-start space-x-4">
                            <div class="bg-indigo-600 text-white p-3 rounded-2xl">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                            </div>
                            <div class="flex-1">
                                <h4 class="text-indigo-900 font-black text-xl mb-2 italic uppercase tracking-tight">Compliance Alert</h4>
                                <p class="text-indigo-700 mb-6 leading-relaxed text-sm">
                                    System detected metadata risks. As a <b>{{profession}}</b>, verify compliance with <b>{{laws}}</b>.
                                </p>
                                <button id="paywall-trigger" class="w-full bg-indigo-600 text-white py-4 rounded-2xl font-black text-lg hover:bg-indigo-700 shadow-xl transition-all uppercase tracking-widest">
                                    Get Expert Audit Report ($4.99)
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- 支付弹窗 -->
    <div id="pay-modal" class="fixed inset-0 bg-slate-900/95 hidden flex items-center justify-center z-50 p-4 backdrop-blur-md">
        <div class="bg-white p-12 rounded-[3rem] max-w-md w-full text-center shadow-2xl animate-in">
            <h3 class="text-3xl font-black text-slate-900 mb-4 italic uppercase">Unlock Report</h3>
            <p class="text-slate-500 mb-10 text-lg leading-snug">Generate professional audit for <b>{{profession}}</b> regarding <b>{{laws}}</b>.</p>
            
            <a id="pay-link" href="""" + PAYHIP_LINK + """" target="_blank" class="block w-full bg-indigo-600 text-white py-5 rounded-2xl font-black text-xl hover:bg-indigo-700 shadow-lg transition-all mb-4 cursor-pointer">
                Pay with Payhip ($4.99)
            </a>
            
            <p class="text-xs text-slate-400 mt-2 mb-6">Secure payment via Payhip.</p>

            <div id="post-pay-actions" class="hidden border-t border-slate-100 pt-6">
                <p class="text-green-600 font-bold mb-3 text-sm">Payment Initiated?</p>
                <button id="generate-report-btn" class="w-full bg-slate-900 text-white py-3 rounded-xl font-bold hover:bg-slate-800 transition-all shadow-md">
                    I've Paid - Download Report
                </button>
            </div>
            
            <button onclick="document.getElementById('pay-modal').classList.add('hidden')" class="mt-4 block w-full text-slate-300 text-xs hover:text-slate-500">Close</button>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const pdfInput = document.getElementById('pdf-input');
        const actionControls = document.getElementById('action-controls');
        const runToolBtn = document.getElementById('run-tool-btn');
        const resultUi = document.getElementById('result-ui');
        const payModal = document.getElementById('pay-modal');
        const paywallTrigger = document.getElementById('paywall-trigger');
        const freeDownloadBtn = document.getElementById('free-download-btn');
        const encryptInput = document.getElementById('encrypt-input');
        const payLink = document.getElementById('pay-link');
        const postPayActions = document.getElementById('post-pay-actions');
        const generateReportBtn = document.getElementById('generate-report-btn');
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');

        let currentFileArrayBuffer = null;
        let processedPdfBytes = null;

        const CONTEXT = {
            profession: "{{profession}}",
            state: "{{state}}",
            action: "{{action}}",
            filename: ""
        };

        // --- 系统自检 (V5.2 Fix) ---
        function checkEngines() {
            if (typeof PDFLib !== 'undefined' && typeof window.jspdf !== 'undefined') {
                statusDot.className = 'h-2 w-2 bg-green-500 rounded-full';
                statusText.innerText = 'System V5.2 Online';
                if (!runToolBtn.classList.contains('processing')) {
                    runToolBtn.disabled = false;
                    runToolBtn.innerText = "START {{action}} (FREE)";
                }
                return true;
            } else {
                // 如果未加载，尝试动态重载或等待
                setTimeout(checkEngines, 500); 
                return false;
            }
        }
        window.onload = checkEngines;

        // --- 1. 文件处理 ---
        dropZone.onclick = () => pdfInput.click();
        pdfInput.onchange = (e) => handleFile(e.target.files[0]);
        
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drop-active'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drop-active'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drop-active');
            handleFile(e.dataTransfer.files[0]);
        });

        async function handleFile(file) {
            if (file && file.type === 'application/pdf') {
                currentFileArrayBuffer = await file.arrayBuffer();
                CONTEXT.filename = file.name;
                document.getElementById('ready-file-name').innerText = file.name;
                document.getElementById('upload-ui').classList.add('hidden');
                document.getElementById('file-ready-ui').classList.remove('hidden');
                actionControls.classList.remove('hidden');
                
                const actionLower = CONTEXT.action.toLowerCase();
                if (actionLower.includes('encrypt') || actionLower.includes('protect') || actionLower.includes('lock')) {
                    encryptInput.classList.remove('hidden');
                }
            }
        }

        // --- 2. 免费功能执行 (强力修复) ---
        runToolBtn.onclick = async () => {
            if (typeof PDFLib === 'undefined') {
                alert("Core Engine (PDFLib) failed to load from CDN. Please refresh the page.");
                return;
            }

            runToolBtn.disabled = true;
            runToolBtn.classList.add('processing');
            runToolBtn.innerHTML = '<span class="animate-pulse tracking-widest uppercase">Processing...</span>';
            
            try {
                const { PDFDocument, rgb } = PDFLib;
                const pdfDoc = await PDFDocument.load(currentFileArrayBuffer);
                const actionKey = CONTEXT.action.toLowerCase();

                // 路由 A: 加密
                if (actionKey.includes('encrypt') || actionKey.includes('protect') || actionKey.includes('lock')) {
                    const pwd = document.getElementById('pdf-password').value || "123456";
                    pdfDoc.encrypt({ userPassword: pwd, ownerPassword: pwd });
                }
                // 路由 B: 水印
                else if (actionKey.includes('watermark') || actionKey.includes('stamp')) {
                    const pages = pdfDoc.getPages();
                    const { width, height } = pages[0].getSize();
                    pages[0].drawText('MICHAEL SYSTEM STAMP', {
                        x: 50, y: height - 50, size: 20, color: rgb(0.8, 0.1, 0.1), opacity: 0.5
                    });
                }
                // 路由 C: 默认 (加个元数据)
                else {
                    pdfDoc.setTitle('Processed by Michael Tool');
                }

                processedPdfBytes = await pdfDoc.save();
                
                setTimeout(() => {
                    actionControls.classList.add('hidden');
                    resultUi.classList.remove('hidden');
                    resultUi.scrollIntoView({ behavior: 'smooth' });
                }, 1000);

            } catch (err) {
                alert("Processing Error: " + err.message);
                runToolBtn.disabled = false;
                runToolBtn.classList.remove('processing');
                runToolBtn.innerText = "RETRY";
            }
        };

        // --- 3. 免费下载 ---
        freeDownloadBtn.onclick = () => {
            if (!processedPdfBytes) return;
            const blob = new Blob([processedPdfBytes], { type: 'application/pdf' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `Processed_${CONTEXT.filename}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        };

        // --- 4. 专家报告逻辑 ---
        paywallTrigger.onclick = () => payModal.classList.remove('hidden');
        payLink.onclick = () => { setTimeout(() => postPayActions.classList.remove('hidden'), 2000); };

        generateReportBtn.onclick = async () => {
            generateReportBtn.innerText = "Connecting to Expert Brain...";
            generateReportBtn.disabled = true;
            try {
                const res = await fetch('/api/generate-report', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(CONTEXT)
                });
                const data = await res.json();
                if (data.report) {
                    const { jsPDF } = window.jspdf;
                    const doc = new jsPDF();
                    doc.setFontSize(22);
                    doc.text("Expert Compliance Audit", 105, 20, {align: "center"});
                    doc.setFontSize(10);
                    doc.text(`Ref: {{laws}}`, 105, 30, {align: "center"});
                    doc.line(20, 35, 190, 35);
                    doc.setFontSize(11);
                    const lines = doc.splitTextToSize(data.report, 170);
                    let y = 45;
                    for (let line of lines) {
                        if (y > 280) { doc.addPage(); y = 20; }
                        doc.text(line, 20, y);
                        y += 6;
                    }
                    doc.save(`Audit_Report.pdf`);
                    setTimeout(() => payModal.classList.add('hidden'), 1000);
                } else {
                    throw new Error(data.error || "Brain disconnected.");
                }
            } catch (e) { 
                alert("Error: " + e.message);
                generateReportBtn.disabled = false;
                generateReportBtn.innerText = "Retry Download";
            }
        };
    </script>
</body>
</html>
"""

def slugify(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def build():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    for f in os.listdir(OUTPUT_DIR):
        file_path = os.path.join(OUTPUT_DIR, f)
        if os.path.isfile(file_path): os.unlink(file_path)

    try:
        with open(INPUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            h_map = {k.lower().strip(): k for k in reader.fieldnames}
            count = 0
            for row in reader:
                if count >= LIMIT_PAGES: break
                
                action = row.get(h_map.get('action'), 'Audit')
                occ = row.get(h_map.get('occupation'), row.get(h_map.get('niche'), 'Expert'))
                st = row.get(h_map.get('state'), 'California')
                title = row.get(h_map.get('title'), f"{action} for {occ} in {st}")
                desc = row.get(h_map.get('seo_description'), f"Professional {action} tool for {occ}.")
                
                law_text = LAW_DATABASE.get(occ.lower(), LAW_DATABASE["default"])
                
                content = HTML_TEMPLATE.replace("{{h1}}", f"Professional {action} for {occ}s")\
                                      .replace("{{title}}", title)\
                                      .replace("{{description}}", desc)\
                                      .replace("{{profession}}", occ)\
                                      .replace("{{state}}", st)\
                                      .replace("{{action}}", action)\
                                      .replace("{{laws}}", law_text)
                
                fname = slugify(f"{action}-{occ}-{st}") + ".html"
                with open(os.path.join(OUTPUT_DIR, fname), "w", encoding="utf-8") as out:
                    out.write(content)
                count += 1
            print(f"✅ Michael! V5.2 Robust Build Ready: {count} pages generated. PDF Engines Secured.")
    except Exception as e:
        print(f"❌ Error during build: {str(e)}")

if __name__ == "__main__": build()
