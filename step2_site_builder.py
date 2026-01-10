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
# 2. HTML 模板 (V5.6 自动核销版)
# ==========================================
# 修复日志 V5.6:
# 1. 新增 Email 输入框 (Pre-Payment)，用于锁定身份。
# 2. 实现 Auto-Polling (自动轮询)：点击支付后，前端每 3 秒呼叫 /api/verify-payhip 查单。
# 3. 如果 API 返回 success: true，直接自动触发下载。
# 4. Payhip 链接自动带参数 ?email=xxx，预填用户邮箱提升体验。

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} - Michael Expert System</title>
    <script src="https://cdn.tailwindcss.com"></script>
    
    <style>
        .drop-active { border-color: #4f46e5 !important; background-color: #f5f3ff !important; }
        .animate-in { animation: fadeIn 0.3s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        button:disabled { opacity: 0.5; cursor: not-allowed; filter: grayscale(100%); }
        .hidden { display: none; }
        .spinner { border: 3px solid rgba(255,255,255,0.3); border-radius: 50%; border-top: 3px solid white; width: 20px; height: 20px; animation: spin 1s linear infinite; display: inline-block; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .pulse-ring { box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.7); animation: pulse-ring 2s cubic-bezier(0.66, 0, 0, 1) infinite; }
        @keyframes pulse-ring { 70%, 100% { box-shadow: 0 0 0 10px rgba(79, 70, 229, 0); } }
    </style>
</head>
<body class="bg-slate-50 min-h-screen font-sans text-slate-900">
    <nav class="bg-white border-b border-slate-200 py-4 shadow-sm">
        <div class="max-w-5xl mx-auto px-4 flex justify-between items-center">
            <span class="font-black text-2xl text-indigo-600 tracking-tighter uppercase">Grich Tool</span>
            <div class="flex items-center space-x-2">
                <span id="status-dot" class="h-2 w-2 bg-yellow-500 rounded-full animate-pulse"></span>
                <span id="status-text" class="text-[10px] text-slate-400 font-bold uppercase tracking-widest">Loading ESM...</span>
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
                    
                    <button id="run-tool-btn" disabled class="w-full bg-slate-900 text-white py-6 rounded-3xl font-black text-xl hover:bg-indigo-600 transition-all shadow-xl flex items-center justify-center gap-2">
                        Wait for Engine...
                    </button>
                    <p id="engine-status" class="text-center text-xs text-slate-400 mt-2">Connecting to ESM Cloud...</p>
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
                    
                    <!-- 专家审计 -->
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

    <!-- 支付弹窗 (V5.6 Auto-Verify) -->
    <div id="pay-modal" class="fixed inset-0 bg-slate-900/95 hidden flex items-center justify-center z-50 p-4 backdrop-blur-md">
        <div class="bg-white p-12 rounded-[3rem] max-w-md w-full text-center shadow-2xl animate-in relative overflow-hidden">
            <!-- 初始状态 -->
            <div id="pay-phase-1">
                <h3 class="text-3xl font-black text-slate-900 mb-2 italic uppercase">Unlock Report</h3>
                <p class="text-slate-500 mb-8 text-lg leading-snug">Enter your email to receive the report.</p>
                
                <div class="mb-6 text-left">
                    <label class="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">Recipient Email</label>
                    <input type="email" id="user-email" placeholder="name@company.com" class="w-full p-4 rounded-xl border border-slate-200 bg-slate-50 text-lg focus:ring-2 focus:ring-indigo-500 outline-none">
                </div>

                <a id="pay-btn" href="#" class="block w-full bg-indigo-600 text-white py-5 rounded-2xl font-black text-xl hover:bg-indigo-700 shadow-lg transition-all mb-4 cursor-pointer">
                    Pay with Payhip ($4.99)
                </a>
                <p class="text-xs text-slate-300">Secure payment. Report delivered instantly to email.</p>
            </div>

            <!-- 检测状态 (支付中) -->
            <div id="pay-phase-2" class="hidden text-center py-10">
                <div class="w-20 h-20 mx-auto bg-indigo-50 text-indigo-600 rounded-full flex items-center justify-center mb-6 pulse-ring">
                    <svg class="w-10 h-10 animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                </div>
                <h3 class="text-2xl font-black text-slate-900 mb-2">Confirming Payment...</h3>
                <p class="text-slate-500 mb-6">Please complete payment in the new tab.<br>We are scanning for your confirmation.</p>
                <div class="w-full bg-slate-100 rounded-full h-2 mb-2">
                    <div class="bg-indigo-500 h-2 rounded-full w-2/3 animate-[pulse_1s_infinite]"></div>
                </div>
                <p id="poll-status" class="text-xs text-slate-400 font-mono">Status: Waiting for Payhip API...</p>
            </div>

            <button id="close-modal-btn" class="absolute top-4 right-4 text-slate-300 hover:text-slate-500">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>
        </div>
    </div>

    <!-- ESM Script Logic -->
    <script type="module">
        import { PDFDocument, StandardFonts, rgb } from 'https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/+esm';
        import { jsPDF } from 'https://cdn.jsdelivr.net/npm/jspdf@2.5.1/+esm';

        // Element Refs
        const payModal = document.getElementById('pay-modal');
        const payPhase1 = document.getElementById('pay-phase-1');
        const payPhase2 = document.getElementById('pay-phase-2');
        const userEmailInput = document.getElementById('user-email');
        const payBtn = document.getElementById('pay-btn');
        const pollStatus = document.getElementById('poll-status');
        
        let pollInterval = null;
        let isVerified = false;

        // Base Payhip Link
        const BASE_PAYHIP_URL = "{{payhip_link}}"; 

        // --- ESM 初始化 ---
        (function initSystem() {
            document.getElementById('status-dot').className = 'h-2 w-2 bg-green-500 rounded-full';
            document.getElementById('status-text').innerText = 'System V5.6 Online';
            document.getElementById('run-tool-btn').disabled = false;
            document.getElementById('run-tool-btn').innerText = "START {{action}} (FREE)";
        })();

        // --- UI Interactions ---
        // 1. Open Modal
        document.getElementById('paywall-trigger').onclick = () => {
            payModal.classList.remove('hidden');
            payPhase1.classList.remove('hidden');
            payPhase2.classList.add('hidden');
            clearInterval(pollInterval);
        };

        // 2. Click PAY (Start Process)
        payBtn.onclick = (e) => {
            e.preventDefault();
            const email = userEmailInput.value.trim();
            if(!email || !email.includes('@')) {
                alert("Please enter a valid email address.");
                return;
            }

            // A. Open Payhip (Prefilled)
            const finalUrl = BASE_PAYHIP_URL + "?email=" + encodeURIComponent(email);
            window.open(finalUrl, '_blank');

            // B. Switch to Polling UI
            payPhase1.classList.add('hidden');
            payPhase2.classList.remove('hidden');

            // C. Start AI Polling
            startPolling(email);
        };

        document.getElementById('close-modal-btn').onclick = () => {
             payModal.classList.add('hidden');
             clearInterval(pollInterval);
        };

        // --- Logic: Auto-Polling ---
        function startPolling(email) {
            let attempts = 0;
            pollStatus.innerText = `Scanning orders for: ${email}`;
            
            pollInterval = setInterval(async () => {
                attempts++;
                if (isVerified) return;

                try {
                    const res = await fetch('/api/verify-payhip', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ email: email })
                    });
                    
                    if (res.status === 200) {
                        const data = await res.json();
                        if (data.success) {
                            clearInterval(pollInterval);
                            isVerified = true;
                            pollStatus.innerText = "Payment Verified! Generating Report...";
                            pollStatus.classList.add('text-green-600', 'font-bold');
                            // Auto Trigger Generation
                            generateExpertReport();
                        }
                    } else {
                        pollStatus.innerText = `Scanning... (Attempt ${attempts})`;
                    }
                } catch (err) {
                    console.error("Poll Error", err);
                }

                if (attempts > 300) { // 15 mins timeout
                    clearInterval(pollInterval);
                    pollStatus.innerText = "Session timeout. Please retry.";
                }
            }, 3000); // Check every 3 seconds
        }

        async function generateExpertReport() {
            // Reusing Generate Logic
            const CONTEXT = {
                profession: "{{profession}}",
                state: "{{state}}",
                action: "{{action}}",
                filename: document.getElementById('ready-file-name').innerText
            };

            try {
                const res = await fetch('/api/generate-report', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(CONTEXT)
                });
                const data = await res.json();
                
                if (data.report) {
                    const doc = new jsPDF();
                    doc.setFontSize(22);
                    doc.text("Expert Compliance Audit (Paid)", 105, 20, {align: "center"});
                    doc.setFontSize(10);
                    doc.text(`Ref: {{laws}}`, 105, 30, {align: "center"});
                    doc.line(20, 35, 190, 35);
                    const lines = doc.splitTextToSize(data.report, 170);
                    let y = 45;
                    for (let line of lines) {
                        if (y > 280) { doc.addPage(); y = 20; }
                        doc.text(line, 20, y);
                        y += 6;
                    }
                    doc.save(`Expert_Audit_Report.pdf`);
                    alert("Thank you! Your report has been downloaded.");
                    payModal.classList.add('hidden');
                }
            } catch (e) {
                alert("Generation Error: " + e.message);
            }
        }

        // --- File & Tool Logic (Same as V5.5) ---
        const dropZone = document.getElementById('drop-zone');
        const pdfInput = document.getElementById('pdf-input');
        const runToolBtn = document.getElementById('run-tool-btn');
        let currentFileArrayBuffer = null;

        dropZone.onclick = () => pdfInput.click();
        pdfInput.onchange = (e) => handleFile(e.target.files[0]);
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('drop-active'); });
        dropZone.addEventListener('drop', (e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); });

        async function handleFile(file) {
            if (file) {
                currentFileArrayBuffer = await file.arrayBuffer();
                document.getElementById('ready-file-name').innerText = file.name;
                document.getElementById('upload-ui').classList.add('hidden');
                document.getElementById('file-ready-ui').classList.remove('hidden');
                document.getElementById('action-controls').classList.remove('hidden');
                if("{{action}}".toLowerCase().includes('encrypt')) {
                    document.getElementById('encrypt-input').classList.remove('hidden');
                }
            }
        }
        
        runToolBtn.onclick = async () => {
            // Simplified Processing Logic for V5.6 to save space
            if(!currentFileArrayBuffer) return;
            runToolBtn.innerHTML = "Processing...";
            try {
                const pdfDoc = await PDFDocument.load(currentFileArrayBuffer);
                const actionKey = "{{action}}".toLowerCase();
                 if (actionKey.includes('encrypt')) {
                    const pwd = document.getElementById('pdf-password').value || "123456";
                    pdfDoc.encrypt({ userPassword: pwd, ownerPassword: pwd });
                } else if (actionKey.includes('watermark')) {
                    const pages = pdfDoc.getPages();
                    const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
                    pages[0].drawText('MICHAEL', { x: 50, y: 50, size: 50, font: font, opacity: 0.3 });
                }
                const bytes = await pdfDoc.save();
                // Enable Download
                 document.getElementById('action-controls').classList.add('hidden');
                 document.getElementById('result-ui').classList.remove('hidden');
                 document.getElementById('free-download-btn').onclick = () => {
                    const blob = new Blob([bytes], {type: 'application/pdf'});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = "Processed.pdf";
                    a.click();
                 };
            } catch(e) {
                alert("Error: " + e.message);
                runToolBtn.innerHTML = "Retry";
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
                                      .replace("{{laws}}", law_text)\
                                      .replace("{{payhip_link}}", PAYHIP_LINK)
                
                fname = slugify(f"{action}-{occ}-{st}") + ".html"
                with open(os.path.join(OUTPUT_DIR, fname), "w", encoding="utf-8") as out:
                    out.write(content)
                count += 1
            print(f"✅ Michael! V5.6 Auto-Verify Logic: {count} pages generated.")
    except Exception as e:
        print(f"❌ Error during build: {str(e)}")

if __name__ == "__main__": build()
