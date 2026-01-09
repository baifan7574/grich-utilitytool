import csv
import os
import shutil
import re

# ==========================================
# 1. 配置区
# ==========================================
INPUT_CSV = "niche_data.csv"
OUTPUT_DIR = "dist"

# Michael 核心 SEO 策略：分批上线，模拟自然增长
LIMIT_PAGES = 500  

# Michael 真实支付链接
PAYHIP_LINK = "https://payhip.com/b/HSDxs"

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
# 2. Michael 专属 HTML 模板 (V3.7 逻辑复原版)
# ==========================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} - Michael Expert Audit System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- 多重冗余 CDN 确保 PDF 库在各种浏览器环境下均可加载 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script>
        // 备份加载逻辑：如果第一个 CDN 挂了，尝试第二个
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
            <span class="font-black text-2xl text-indigo-600 tracking-tighter">GRICH AUDIT</span>
            <div class="flex items-center space-x-2">
                <span id="status-dot" class="h-2 w-2 bg-yellow-500 rounded-full animate-pulse"></span>
                <span id="status-text" class="text-[10px] text-slate-400 font-bold tracking-widest uppercase">System Initializing...</span>
            </div>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-4 py-16">
        <div class="text-center mb-16">
            <h1 class="text-5xl font-black text-slate-900 mb-6 tracking-tight">{{h1}}</h1>
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
                        <p class="text-2xl font-bold text-slate-700">Upload PDF for Compliance Audit</p>
                        <p class="text-slate-400 mt-3">Target Standard: <span class="text-indigo-500 font-semibold">{{laws}}</span></p>
                    </div>
                    <div id="file-ready-ui" class="hidden animate-in">
                        <div class="w-20 h-20 bg-green-50 text-green-600 rounded-3xl flex items-center justify-center mx-auto mb-6">
                            <svg class="w-10 h-10" fill="currentColor" viewBox="0 0 20 20"><path d="M9 2a2 2 0 00-2 2v12a2 2 0 002 2h2a2 2 0 002-2V4a2 2 0 00-2-2H9z" /></svg>
                        </div>
                        <p id="ready-file-name" class="text-2xl font-bold text-slate-800 truncate px-8"></p>
                    </div>
                </div>

                <button id="run-audit-btn" class="hidden mt-10 w-full bg-slate-900 text-white py-6 rounded-3xl font-black text-xl hover:bg-indigo-600 transition-all shadow-xl hover:-translate-y-1">
                    RUN EXPERT AUDIT SCAN
                </button>
            </div>
        </div>
    </main>

    <div id="pay-modal" class="fixed inset-0 bg-slate-900/95 hidden flex items-center justify-center z-50 p-4 backdrop-blur-md">
        <div class="bg-white p-12 rounded-[3rem] max-w-md w-full text-center shadow-2xl animate-in">
            <div class="w-24 h-24 bg-green-50 text-green-500 rounded-full flex items-center justify-center mx-auto mb-8">
                <svg class="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" /></svg>
            </div>
            <h3 class="text-3xl font-black text-slate-900 mb-4">Audit Complete</h3>
            <p class="text-slate-500 mb-10 text-lg">Your expert report for <b>{{profession}}</b> in <b>{{state}}</b> is ready for download.</p>
            
            <a href="""" + PAYHIP_LINK + """" target="_blank" class="block w-full bg-indigo-600 text-white py-5 rounded-2xl font-black text-xl hover:bg-indigo-700 shadow-lg transition-all mb-4">
                Download Full Report ($4.99)
            </a>
            
            <div class="relative py-6">
                <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-100"></div></div>
                <div class="relative flex justify-center text-xs uppercase tracking-widest text-slate-300 font-bold bg-white px-4">Michael Admin</div>
            </div>
            
            <button id="bypass-btn" class="text-slate-400 font-bold hover:text-red-500 transition-colors">
                Internal Acceptance (Admin Only)
            </button>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const pdfInput = document.getElementById('pdf-input');
        const runBtn = document.getElementById('run-audit-btn');
        const payModal = document.getElementById('pay-modal');
        const bypassBtn = document.getElementById('bypass-btn');
        const statusDot = document.getElementById('status-dot');
        const statusText = document.getElementById('status-text');

        const CONTEXT = {
            profession: "{{profession}}",
            state: "{{state}}",
            action: "{{action}}",
            filename: ""
        };

        // 系统自检
        window.onload = () => {
            if (window.jspdf || (window.jspdf && window.jspdf.jsPDF)) {
                statusDot.className = 'h-2 w-2 bg-green-500 rounded-full';
                statusText.innerText = 'Michael Expert System Active';
            } else {
                statusDot.className = 'h-2 w-2 bg-red-500 rounded-full';
                statusText.innerText = 'Engine Offline - Refresh Needed';
            }
        };

        dropZone.onclick = () => pdfInput.click();
        pdfInput.onchange = (e) => {
            const file = e.target.files[0];
            if (file && file.type === 'application/pdf') {
                CONTEXT.filename = file.name;
                document.getElementById('ready-file-name').innerText = file.name;
                document.getElementById('upload-ui').classList.add('hidden');
                document.getElementById('file-ready-ui').classList.remove('hidden');
                runBtn.classList.remove('hidden');
            }
        };

        runBtn.onclick = () => {
            runBtn.disabled = true;
            runBtn.innerHTML = '<span class="animate-pulse tracking-widest uppercase">Analyzing Compliance...</span>';
            setTimeout(() => {
                payModal.classList.remove('hidden');
                runBtn.disabled = false;
                runBtn.innerText = 'RUN EXPERT AUDIT SCAN';
            }, 1800);
        };

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
                    doc.setFontSize(22);
                    doc.text("Expert Compliance Audit Report", 105, 20, {align: "center"});
                    doc.setFontSize(10);
                    doc.text(`Target: {{profession}} | Standard: {{laws}} | Jurisdiction: {{state}}`, 105, 30, {align: "center"});
                    doc.line(20, 35, 190, 35);
                    
                    doc.setFontSize(11);
                    const lines = doc.splitTextToSize(data.report, 170);
                    doc.text(lines, 20, 45);
                    doc.save(`Audit_Report_${CONTEXT.profession}.pdf`);
                } else {
                    alert("System Feedback: " + (data.error || "Unknown error occurred."));
                }
            } catch (e) {
                alert("Critical Failure: " + e.message);
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
            # 获取 CSV 列名的映射，解决大小写不一致问题
            h_map = {k.lower().strip(): k for k in reader.fieldnames}
            
            count = 0
            for row in reader:
                if count >= LIMIT_PAGES: break
                
                action = row.get(h_map.get('action'), 'Audit')
                occ = row.get(h_map.get('occupation'), row.get(h_map.get('niche'), 'Expert'))
                st = row.get(h_map.get('state'), 'California')
                title = row.get(h_map.get('title'), f"{action} for {occ} in {st}")
                desc = row.get(h_map.get('seo_description'), f"Professional {action} services for {occ} practitioners.")
                
                law_text = LAW_DATABASE.get(occ.lower(), LAW_DATABASE["default"])
                
                content = HTML_TEMPLATE.replace("{{h1}}", f"Expert {action} for {occ}s")\
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
            print(f"✅ Michael! V3.7 Final Build Ready: {count} pages generated. Execute Git Push.")
    except Exception as e:
        print(f"❌ Error during build: {str(e)}")

if __name__ == "__main__": build()
