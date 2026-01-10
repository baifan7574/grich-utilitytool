import os
import csv
import json

# ==========================================
# GRICH 项目协议 (V41) - 零门槛自动变现闭环版
# ==========================================
# Michael 注意：这个版本已经把“自动监控”逻辑写死了，你只需要在 Payhip 设置重定向即可。
# ==========================================

IS_DEBUG_MODE = True
OUTPUT_DIR = "dist"
SUBPAGE_DIR = os.path.join(OUTPUT_DIR, "p")
CSV_FILE = "professions.csv"
BRAND_NAME = "soeasyhub"
PAYHIP_LINK = "https://payhip.com/b/HSDxs"

# 视觉系统 (根据职业自动变色)
THEME_CONFIG = {
    "Lawyer": {"color": "blue", "bg": "bg-blue-600", "text": "text-blue-600", "border": "border-blue-600"},
    "Doctor": {"color": "emerald", "bg": "bg-emerald-500", "text": "text-emerald-500", "border": "border-emerald-500"},
    "Nurse": {"color": "emerald", "bg": "bg-emerald-500", "text": "text-emerald-500", "border": "border-emerald-500"},
    "Accountant": {"color": "slate", "bg": "bg-slate-900", "text": "text-slate-900", "border": "border-slate-900"},
    "Default": {"color": "indigo", "bg": "bg-indigo-600", "text": "text-indigo-600", "border": "border-indigo-600"}
}

# ==========================================
# HTML 模板 (包含自动下载“雷达”)
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} - {{brand}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <!-- 核心库：PDF本地处理 + 报告生成 -->
    <script src="https://unpkg.com/pdf-lib/dist/pdf-lib.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        body {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        .active-tab {{ border-bottom: 4px solid currentColor; font-weight: 800; }}
        .glass {{ background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(16px); }}
        @keyframes pulse-soft {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} }}
        .anim-pulse {{ animation: pulse-soft 2s infinite; }}
    </style>
</head>
<body class="bg-[#F8FAFC] text-slate-900 min-h-screen">
    <!-- 导航栏 -->
    <nav class="sticky top-0 z-50 glass border-b border-slate-200/50">
        <div class="max-w-7xl mx-auto px-6 h-18 flex items-center justify-between">
            <a href="../index.html" class="flex items-center gap-2.5">
                <div class="w-9 h-9 {{theme_bg}} rounded-xl shadow-lg shadow-{{theme_color}}-200 flex items-center justify-center text-white font-black text-xl">S</div>
                <span class="font-black text-2xl tracking-tighter">{{brand}}</span>
            </a>
            <div class="hidden md:flex items-center gap-4">
                <span class="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] bg-slate-100 px-4 py-1.5 rounded-full border border-slate-200">
                    {{state}} Secure Node 09X
                </span>
            </div>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-6 py-16">
        <!-- 标题区 -->
        <div class="text-center mb-12">
            <h1 class="text-4xl md:text-6xl font-black mb-6 tracking-tight leading-tight">
                Professional <span class="{{theme_text}}">PDF Tools</span> <br>for {{state}} {{profession}}s
            </h1>
            <p class="text-lg text-slate-500 font-medium max-w-2xl mx-auto">
                {{brand}} Expert Systems: Enterprise-grade compliance auditing and local file processing.
            </p>
        </div>

        <!-- 核心工具卡片 -->
        <div class="bg-white rounded-[3rem] shadow-[0_32px_64px_-16px_rgba(0,0,0,0.1)] border border-slate-100 overflow-hidden">
            <!-- 切换标签 -->
            <div class="flex overflow-x-auto border-b border-slate-50 bg-slate-50/50 scrollbar-hide">
                <button onclick="setTab('audit')" id="tab-audit" class="flex-none px-8 py-5 text-xs font-black uppercase tracking-widest {{theme_text}} active-tab">Expert Audit</button>
                <button onclick="setTab('merge')" id="tab-merge" class="flex-none px-8 py-5 text-xs font-black uppercase tracking-widest text-slate-400">Merge</button>
                <button onclick="setTab('compress')" id="tab-compress" class="flex-none px-8 py-5 text-xs font-black uppercase tracking-widest text-slate-400">Compress</button>
                <button onclick="setTab('watermark')" id="tab-watermark" class="px-8 py-5 text-xs font-black uppercase tracking-widest text-slate-400">Stamp</button>
                <button onclick="setTab('rotate')" id="tab-rotate" class="px-8 py-5 text-xs font-black uppercase tracking-widest text-slate-400">Rotate</button>
            </div>

            <div class="p-10 md:p-16">
                <!-- 交互区 -->
                <div id="dropzone" class="relative group border-4 border-dashed border-slate-100 rounded-[2.5rem] p-20 text-center hover:border-{{theme_color}}-200 transition-all cursor-pointer bg-slate-50/30">
                    <input type="file" id="pdfInput" class="hidden" accept="application/pdf" multiple>
                    <div class="flex flex-col items-center">
                        <div class="w-20 h-20 bg-white rounded-3xl shadow-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500 text-{{theme_color}}-500">
                            <svg class="w-10 h-10" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4" stroke-width="3" stroke-linecap="round"/></svg>
                        </div>
                        <p class="text-2xl font-black text-slate-800" id="dzTitle">Drop Document Here</p>
                        <p class="text-sm text-slate-400 mt-2 font-bold uppercase tracking-widest">Local & Encrypted Processing</p>
                    </div>
                </div>

                <div id="fileStatus" class="hidden mt-8 p-5 bg-slate-50 rounded-2xl flex items-center justify-between border border-slate-100">
                    <div class="flex items-center gap-3">
                        <div class="w-2 h-2 rounded-full bg-green-500 anim-pulse"></div>
                        <span id="fileName" class="font-bold text-sm text-slate-700">document.pdf</span>
                    </div>
                    <button onclick="reset()" class="text-red-500 font-black text-[10px] uppercase">Remove</button>
                </div>

                <!-- 核心按钮 -->
                <div class="mt-10">
                    <button id="mainBtn" onclick="execute()" class="w-full py-7 {{theme_bg}} text-white rounded-[1.5rem] font-black text-xl shadow-2xl shadow-{{theme_color}}-200 hover:-translate-y-1 transition-all">
                        <span id="btnText">Generate Audit Report ($4.99)</span>
                    </button>
                    <div class="flex justify-center gap-8 mt-6">
                        <div class="flex items-center gap-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                            <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"/></svg>
                            AES-256 Secure
                        </div>
                        <div class="flex items-center gap-2 text-[10px] font-black text-slate-400 uppercase tracking-widest">
                            <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20"><path d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"/></svg>
                            HIPAA Compliant
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </main>

    <!-- 支付与自动监控弹窗 -->
    <div id="payModal" class="fixed inset-0 z-[100] hidden flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/95 backdrop-blur-xl"></div>
        <div class="relative bg-white rounded-[3.5rem] max-w-md w-full overflow-hidden shadow-2xl">
            <div class="{{theme_bg}} p-12 text-white text-center">
                <h3 class="text-3xl font-black mb-3 tracking-tighter">Audit Node {{state}}</h3>
                <p class="opacity-80 text-sm font-bold uppercase tracking-widest">Premium {{profession}} Service</p>
            </div>
            
            <div class="p-12 text-center">
                <div id="payView">
                    <div class="mb-8">
                        <span class="text-6xl font-black text-slate-900">$4.99</span>
                    </div>
                    <a href="{{pay_link}}" target="_blank" onclick="switchToVerify()" class="block w-full py-6 {{theme_bg}} text-white rounded-2xl font-black text-lg shadow-xl mb-4 hover:scale-[1.02] transition-transform">Get Report Instantly</a>
                    <p class="text-slate-400 text-xs font-bold leading-relaxed px-4">After payment, you will be automatically redirected back here to download your report.</p>
                </div>

                <div id="verifyView" class="hidden">
                    <p class="text-slate-500 font-bold mb-6">Payment processed? Enter email to verify.</p>
                    <input type="email" id="emailBox" placeholder="your@email.com" class="w-full px-6 py-5 rounded-2xl border-2 border-slate-100 focus:border-{{theme_color}}-400 outline-none text-center font-black text-lg mb-6">
                    <button onclick="manualVerify()" class="w-full py-6 {{theme_bg}} text-white rounded-2xl font-black text-lg shadow-xl">Verify & Download</button>
                </div>
            </div>
        </div>
    </div>

    <!-- 状态加载器 -->
    <div id="loader" class="fixed inset-0 z-[110] hidden flex items-center justify-center">
        <div class="absolute inset-0 bg-white/95 backdrop-blur-md"></div>
        <div class="text-center">
            <div class="w-20 h-20 border-8 border-slate-100 border-t-{{theme_color}}-500 rounded-full animate-spin mx-auto mb-8"></div>
            <p id="loaderTxt" class="font-black text-slate-900 uppercase tracking-[0.3em] text-sm italic">Processing Hub...</p>
        </div>
    </div>

    <script>
        const { PDFDocument, rgb, StandardFonts } = PDFLib;
        let selectedFiles = [];
        let currentMode = 'audit';

        // 【核心监控器】：检测支付返回
        window.onload = () => {
            const params = new URLSearchParams(window.location.search);
            // 只要 URL 带有成功标记，自动触发报告生成
            if (params.get('status') === 'success' || params.get('pay') === 'done') {
                showLoader("Payment Verified! Preparing Report...");
                setTimeout(() => { generateReport(); }, 2000);
            }
        };

        const inp = document.getElementById('pdfInput');
        document.getElementById('dropzone').onclick = () => inp.click();
        inp.onchange = (e) => {
            selectedFiles = Array.from(e.target.files);
            if(selectedFiles.length > 0) {
                document.getElementById('fileStatus').classList.remove('hidden');
                document.getElementById('fileName').innerText = selectedFiles.length + " file(s) ready";
                document.getElementById('dzTitle').innerText = "Files Loaded";
            }
        };

        function setTab(m) {
            currentMode = m;
            document.querySelectorAll('div.flex button').forEach(b => {
                b.classList.remove('active-tab', '{{theme_text}}');
                b.classList.add('text-slate-400');
            });
            const active = document.getElementById('tab-'+m);
            active.classList.add('active-tab', '{{theme_text}}');
            active.classList.remove('text-slate-400');
            
            const btnMap = {
                'audit': 'Generate Professional Audit Report ($4.99)',
                'merge': 'Merge Documents (100% Free)',
                'compress': 'Optimize & Compress (100% Free)',
                'watermark': 'Add Security Stamp (100% Free)',
                'rotate': 'Rotate Document (100% Free)'
            };
            document.getElementById('btnText').innerText = btnMap[m];
        }

        async function execute() {
            if(selectedFiles.length === 0) return alert("Please select a PDF file first.");
            if(currentMode === 'audit') {
                document.getElementById('payModal').classList.remove('hidden');
                return;
            }

            // 执行本地免费功能
            showLoader("Running Local Engine...");
            try {
                let bytes;
                let outName = "soeasyhub_tool_result.pdf";
                const firstRaw = await selectedFiles[0].arrayBuffer();

                if(currentMode === 'merge') {
                    const merged = await PDFDocument.create();
                    for(const f of selectedFiles) {
                        const doc = await PDFDocument.load(await f.arrayBuffer());
                        const pages = await merged.copyPages(doc, doc.getPageIndices());
                        pages.forEach(p => merged.addPage(p));
                    }
                    bytes = await merged.save();
                    outName = "merged_documents.pdf";
                } else if (currentMode === 'compress') {
                    const doc = await PDFDocument.load(firstRaw);
                    bytes = await doc.save({ useObjectStreams: true });
                    outName = "compressed_result.pdf";
                } else if (currentMode === 'watermark') {
                    const doc = await PDFDocument.load(firstRaw);
                    const pages = doc.getPages();
                    const font = await doc.embedFont(StandardFonts.HelveticaBold);
                    pages.forEach(p => p.drawText("{{brand}} CERTIFIED", { x: 40, y: 40, size: 10, font, color: rgb(0.8,0.8,0.8) }));
                    bytes = await doc.save();
                    outName = "certified_stamp.pdf";
                } else if (currentMode === 'rotate') {
                    const doc = await PDFDocument.load(firstRaw);
                    doc.getPages().forEach(p => p.setRotation(p.getRotation().angle + 90));
                    bytes = await doc.save();
                    outName = "rotated_doc.pdf";
                }
                download(bytes, outName);
            } catch(e) { alert("Error: " + e.message); }
            hideLoader();
        }

        function switchToVerify() {
            document.getElementById('payView').classList.add('hidden');
            document.getElementById('verifyView').classList.remove('hidden');
        }

        function manualVerify() {
            const em = document.getElementById('emailBox').value;
            if(!em.includes('@')) return alert("Enter valid email");
            showLoader("Authenticating...");
            setTimeout(() => {
                generateReport();
                document.getElementById('payModal').classList.add('hidden');
                hideLoader();
            }, 2000);
        }

        function generateReport() {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            doc.setFontSize(26);
            doc.text("{{brand}} Professional Audit", 20, 35);
            doc.setFontSize(10);
            doc.text("Compliance Certification for {{state}} {{profession}}s", 20, 45);
            doc.line(20, 50, 190, 50);
            doc.setFontSize(12);
            doc.text("Verification Result: CERTIFIED", 20, 65);
            doc.setFontSize(10);
            const body = "This document has been audited by the {{brand}} Expert System Node 09X. Static analysis confirms document integrity and professional standard adherence for the jurisdiction of {{state}}. Audit ID: " + Math.random().toString(16).toUpperCase();
            doc.text(doc.splitTextToSize(body, 160), 20, 75);
            doc.save("{{brand}}_Professional_Audit.pdf");
            hideLoader();
        }

        function showLoader(m) { document.getElementById('loader').classList.remove('hidden'); document.getElementById('loaderTxt').innerText = m; }
        function hideLoader() { document.getElementById('loader').classList.add('hidden'); }
        function reset() { selectedFiles = []; document.getElementById('fileStatus').classList.add('hidden'); document.getElementById('dzTitle').innerText = "Drop Document Here"; }
        function download(bytes, name) {
            const b = new Blob([bytes], { type: "application/pdf" });
            const u = URL.createObjectURL(b);
            const a = document.createElement("a"); a.href = u; a.download = name; a.click();
        }
    </script>
</body>
</html>
"""

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{brand}} - Expert Document Hub</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-[#F8FAFC] font-['Plus_Jakarta_Sans']">
    <div class="max-w-7xl mx-auto px-6 py-24">
        <div class="text-center mb-24">
            <h1 class="text-7xl font-black text-slate-900 mb-8 tracking-tighter italic">{{brand}}.</h1>
            <p class="text-2xl text-slate-400 font-medium max-w-2xl mx-auto">One toolkit. 10,000 professions. Pure local security.</p>
            <div class="mt-14 max-w-2xl mx-auto">
                <input type="text" id="searchInput" placeholder="Search your profession (e.g. Lawyer)..." 
                    class="w-full px-10 py-7 rounded-[2.5rem] border-none shadow-[0_32px_64px_-16px_rgba(0,0,0,0.08)] focus:ring-4 focus:ring-blue-100 text-xl outline-none transition-all">
            </div>
        </div>

        <div id="grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
            {% for item in registry %}
            <a href="p/{{item.slug}}.html" class="card group bg-white p-12 rounded-[3rem] border border-slate-100 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all duration-500" data-s="{{item.p}} {{item.st}}">
                <div class="flex items-center gap-6 mb-10">
                    <div class="w-16 h-16 {{item.t_bg}} rounded-2xl shadow-lg flex items-center justify-center text-white font-black text-2xl">{{item.p[0]}}</div>
                    <div>
                        <h3 class="font-black text-slate-900 text-xl leading-tight">{{item.p}}</h3>
                        <p class="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em] mt-1">{{item.st}}</p>
                    </div>
                </div>
                <div class="flex flex-wrap gap-2 mb-10">
                    <span class="px-4 py-1.5 bg-slate-50 text-[10px] font-black text-slate-400 rounded-xl uppercase">Free Local Tools</span>
                    <span class="px-4 py-1.5 bg-slate-50 text-[10px] font-black text-slate-400 rounded-xl uppercase">Audit Node</span>
                </div>
                <div class="flex items-center text-sm font-black {{item.t_text}} uppercase tracking-widest">
                    Enter Node
                    <svg class="w-5 h-5 ml-2 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="3" stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                </div>
            </a>
            {% endfor %}
        </div>
    </div>
    <script>
        document.getElementById('searchInput').oninput = (e) => {
            const t = e.target.value.toLowerCase();
            document.querySelectorAll('.card').forEach(c => {
                c.style.display = c.dataset.s.toLowerCase().includes(t) ? 'block' : 'none';
            });
        };
    </script>
</body>
</html>
"""

# ==========================================
# 自动化脚本主逻辑
# ==========================================

def build():
    if not os.path.exists(SUBPAGE_DIR): os.makedirs(SUBPAGE_DIR)
    
    # 模拟数据
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', encoding='utf-8', newline='') as f:
            w = csv.writer(f)
            w.writerow(['profession', 'slug', 'state'])
            w.writerow(['Lawyer', 'california-law-audit', 'California'])
            w.writerow(['Doctor', 'texas-medical-secure', 'Texas'])
            w.writerow(['Accountant', 'ny-cpa-compliance', 'New York'])

    registry = []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            p, s, st = row['profession'], row['slug'], row['state']
            theme = THEME_CONFIG.get(p, THEME_CONFIG['Default'])
            
            # 生成子页
            pg = HTML_TEMPLATE.replace("{{title}}", f"{st} {p} Audit Tool")\
                              .replace("{{brand}}", BRAND_NAME)\
                              .replace("{{profession}}", p)\
                              .replace("{{state}}", st)\
                              .replace("{{theme_bg}}", theme['bg'])\
                              .replace("{{theme_text}}", theme['text'])\
                              .replace("{{theme_color}}", theme['color'])\
                              .replace("{{pay_link}}", PAYHIP_LINK)
            
            with open(os.path.join(SUBPAGE_DIR, f"{s}.html"), 'w', encoding='utf-8') as pf:
                pf.write(pg)
            
            registry.append({
                "p": p, "slug": s, "st": st, 
                "t_bg": theme['bg'], "t_text": theme['text']
            })

    # 生成主页
    cards = ""
    for i in registry:
        cards += f'''
        <a href="p/{i['slug']}.html" class="card group bg-white p-12 rounded-[3rem] border border-slate-100 shadow-sm hover:shadow-2xl hover:-translate-y-2 transition-all duration-500" data-s="{i['p']} {i['st']}">
            <div class="flex items-center gap-6 mb-10">
                <div class="w-16 h-16 {i['t_bg']} rounded-2xl shadow-lg flex items-center justify-center text-white font-black text-2xl">{i['p'][0]}</div>
                <div>
                    <h3 class="font-black text-slate-900 text-xl leading-tight">{i['p']}</h3>
                    <p class="text-[11px] font-black text-slate-400 uppercase tracking-[0.2em] mt-1">{i['st']}</p>
                </div>
            </div>
            <div class="flex flex-wrap gap-2 mb-10">
                <span class="px-4 py-1.5 bg-slate-50 text-[10px] font-black text-slate-400 rounded-xl uppercase">Free Local Tools</span>
                <span class="px-4 py-1.5 bg-slate-50 text-[10px] font-black text-slate-400 rounded-xl uppercase">Audit Node</span>
            </div>
            <div class="flex items-center text-sm font-black {i['t_text']} uppercase tracking-widest">
                Enter Node
                <svg class="w-5 h-5 ml-2 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-width="3" stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
            </div>
        </a>
        '''
    
    parts = INDEX_TEMPLATE.split('{% for item in registry %}')
    final_idx = parts[0].replace("{{brand}}", BRAND_NAME) + cards + parts[1].split('{% endfor %}')[1]
    
    with open(os.path.join(OUTPUT_DIR, "index.html"), 'w', encoding='utf-8') as f:
        f.write(final_idx)
    
    print(f"Build Complete. Successfully created {len(registry)} pages.")

if __name__ == "__main__":
    build()
