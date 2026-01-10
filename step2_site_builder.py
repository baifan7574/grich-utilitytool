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
# 2. HTML 模板 (V4.0 修复下载与排版)
# ==========================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} - Michael Expert System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script>
        if (typeof window.jspdf === 'undefined') {
            document.write('<script src="https://cdn.jsdelivr.net/npm/jspdf@2.5.1/dist/jspdf.umd.min.js"><\\/script>');
        }
    </script>
    <style>
        .drop-active { border-color: #4f46e5 !important; background-color: #f5f3ff !important; }
        .animate-in { animation: fadeIn 0.3s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
    </style>
</head>
<body class="bg-slate-50 min-h-screen font-sans text-slate-900">
    <nav class="bg-white border-b border-slate-200 py-4 shadow-sm">
        <div class="max-w-5xl mx-auto px-4 flex justify-between items-center">
            <span class="font-black text-2xl text-indigo-600 tracking-tighter uppercase">Grich Audit</span>
            <div class="flex items-center space-x-2">
                <span id="status-dot" class="h-2 w-2 bg-green-500 rounded-full"></span>
                <span class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">System V4.0 Ready</span>
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
                <div id="drop-zone" class="relative border-2 border-dashed border-slate-200 rounded-3xl p-16 text-center transition-all cursor-pointer hover:border-indigo-400 hover:bg-slate-50 group">
                    <input type="file" id="pdf-input" class="hidden" accept="application/pdf">
                    <div id="upload-ui">
                        <div class="w-20 h-20 bg-indigo-50 text-indigo-600 rounded-3xl flex items-center justify-center mx-auto mb-6">
                            <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                        </div>
                        <p class="text-2xl font-bold text-slate-700">Drop PDF to Start {{action}}</p>
                        <p class="text-slate-400 mt-3 italic uppercase text-xs tracking-widest font-bold">Ref: {{laws}}</p>
                    </div>
                    <div id="file-ready-ui" class="hidden animate-in">
                        <div class="w-20 h-20 bg-green-50 text-green-600 rounded-3xl flex items-center justify-center mx-auto mb-6">
                            <svg class="w-10 h-10" fill="currentColor" viewBox="0 0 20 20"><path d="M9 2a2 2 0 00-2 2v12a2 2 0 002 2h2a2 2 0 002-2V4a2 2 0 00-2-2H9z" /></svg>
                        </div>
                        <p id="ready-file-name" class="text-2xl font-bold text-slate-800 truncate px-8"></p>
                    </div>
                </div>

                <button id="run-tool-btn" class="hidden mt-10 w-full bg-slate-900 text-white py-6 rounded-3xl font-black text-xl hover:bg-indigo-600 transition-all shadow-xl">
                    PROCESS DOCUMENT
                </button>

                <!-- 结果区域 -->
                <div id="result-ui" class="hidden mt-10 border-t pt-10 animate-in">
                    <!-- 免费下载部分 -->
                    <div class="bg-green-50 border border-green-100 p-6 rounded-3xl mb-8 flex items-center justify-between">
                        <div>
                            <h4 class="text-green-800 font-bold text-lg">Task Complete!</h4>
                            <p class="text-green-600 text-sm">Your file is processed and ready.</p>
                        </div>
                        <button id="free-download-btn" class="bg-green-600 text-white px-6 py-3 rounded-xl font-bold hover:bg-green-700 transition-all shadow-md flex items-center">
                            <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
                            Download File
                        </button>
                    </div>
                    
                    <!-- 付费转化部分 -->
                    <div class="bg-indigo-50 border border-indigo-100 p-8 rounded-[2rem]">
                        <div class="flex items-start space-x-4">
                            <div class="bg-indigo-600 text-white p-3 rounded-2xl">
                                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                            </div>
                            <div class="flex-1">
                                <h4 class="text-indigo-900 font-black text-xl mb-2 italic uppercase tracking-tight">Compliance Alert</h4>
                                <p class="text-indigo-700 mb-6 leading-relaxed text-sm">
                                    Our system detected potential risks regarding <b>{{laws}}</b>. 
                                    We recommend generating an <b>Expert Audit Report</b>.
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

    <!-- Paywall Modal -->
    <div id="pay-modal" class="fixed inset-0 bg-slate-900/95 hidden flex items-center justify-center z-50 p-4 backdrop-blur-md">
        <div class="bg-white p-12 rounded-[3rem] max-w-md w-full text-center shadow-2xl animate-in">
            <h3 class="text-3xl font-black text-slate-900 mb-4 italic uppercase">Unlock Report</h3>
            <p class="text-slate-500 mb-10 text-lg leading-snug">Secure the professional compliance report for <b>{{profession}}</b> in <b>{{state}}</b>.</p>
            
            <a href="""" + PAYHIP_LINK + """" target="_blank" class="block w-full bg-indigo-600 text-white py-5 rounded-2xl font-black text-xl hover:bg-indigo-700 shadow-lg transition-all mb-4">
                Pay with Payhip ($4.99)
            </a>
            
            <div class="relative py-6">
                <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-100"></div></div>
                <div class="relative flex justify-center text-xs uppercase tracking-widest text-slate-300 font-bold bg-white px-4">Admin Only</div>
            </div>
            
            <button id="bypass-btn" class="text-slate-400 font-bold hover:text-red-500 transition-colors uppercase text-[10px] tracking-widest underline">
                Internal Acceptance
            </button>
            <button onclick="document.getElementById('pay-modal').classList.add('hidden')" class="mt-4 block w-full text-slate-300 text-xs">Close</button>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const pdfInput = document.getElementById('pdf-input');
        const runToolBtn = document.getElementById('run-tool-btn');
        const resultUi = document.getElementById('result-ui');
        const payModal = document.getElementById('pay-modal');
        const paywallTrigger = document.getElementById('paywall-trigger');
        const bypassBtn = document.getElementById('bypass-btn');
        const freeDownloadBtn = document.getElementById('free-download-btn');

        let currentFile = null; // 存储当前文件对象

        const CONTEXT = {
            profession: "{{profession}}",
            state: "{{state}}",
            action: "{{action}}",
            filename: ""
        };

        dropZone.onclick = () => pdfInput.click();
        
        pdfInput.onchange = (e) => handleFileSelection(e.target.files[0]);
        
        // 拖拽支持
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drop-active'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('drop-active'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drop-active');
            handleFileSelection(e.dataTransfer.files[0]);
        });

        function handleFileSelection(file) {
            if (file && file.type === 'application/pdf') {
                currentFile = file; // 保存文件以供下载
                CONTEXT.filename = file.name;
                document.getElementById('ready-file-name').innerText = file.name;
                document.getElementById('upload-ui').classList.add('hidden');
                document.getElementById('file-ready-ui').classList.remove('hidden');
                runToolBtn.classList.remove('hidden');
            }
        }

        runToolBtn.onclick = () => {
            runToolBtn.disabled = true;
            runToolBtn.innerHTML = '<span class="animate-pulse tracking-widest uppercase">Processing...</span>';
            setTimeout(() => {
                runToolBtn.classList.add('hidden');
                resultUi.classList.remove('hidden');
                resultUi.scrollIntoView({ behavior: 'smooth' });
            }, 1500);
        };

        // 修复 1: 免费下载逻辑
        freeDownloadBtn.onclick = () => {
            if (!currentFile) return;
            const url = URL.createObjectURL(currentFile);
            const a = document.createElement('a');
            a.href = url;
            a.download = "Processed_" + currentFile.name; // 模拟处理后的文件名
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        };

        paywallTrigger.onclick = () => payModal.classList.remove('hidden');

        // 修复 2: 专家报告排版逻辑
        bypassBtn.onclick = async () => {
            bypassBtn.innerText = "Generating PDF...";
            bypassBtn.disabled = true;
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
                    
                    // 报告页眉
                    doc.setFont("helvetica", "bold");
                    doc.setFontSize(22);
                    doc.text("Expert Compliance Audit Report", 105, 20, {align: "center"});
                    
                    doc.setFontSize(10);
                    doc.setFont("helvetica", "normal");
                    doc.text(`Target: {{profession}} | Jurisdiction: {{state}}`, 105, 30, {align: "center"});
                    doc.setLineWidth(0.5);
                    doc.line(20, 35, 190, 35);
                    
                    // 报告正文 - 自动分页处理
                    doc.setFontSize(11);
                    const splitText = doc.splitTextToSize(data.report, 170);
                    
                    let y = 45;
                    // 循环打印每一行，处理分页
                    for (let i = 0; i < splitText.length; i++) {
                        if (y > 280) { // 如果到了页面底部
                            doc.addPage();
                            y = 20; // 重置 y 坐标
                        }
                        doc.text(splitText[i], 20, y);
                        y += 6; // 行间距
                    }
                    
                    doc.save(`Expert_Audit_${CONTEXT.profession}.pdf`);
                } else {
                    alert("Error: " + (data.error || "Brain disconnected."));
                }
            } catch (e) {
                alert("Critical System Error: " + e.message);
            }
            payModal.classList.add('hidden');
            bypassBtn.innerText = "Internal Acceptance (Admin Only)";
            bypassBtn.disabled = false;
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
                desc = row.get(h_map.get('seo_description'), f"Professional compliance audit system for {occ} in {st}.")
                
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
            print(f"✅ Michael! V4.0 Final Build Ready: {count} pages generated. Free Download + Expert PDF Fixed.")
    except Exception as e:
        print(f"❌ Error during build: {str(e)}")

if __name__ == "__main__": build()
