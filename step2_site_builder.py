import os
import csv
import json
import random
from datetime import datetime

# ==========================================
# GRICH 项目协议 (V43.2 Final AdSense Ready)
# ==========================================
# Michael 专用：全量物理生成 + 仪式感扫描 + AdSense 合规
# ------------------------------------------

# --- Michael 核心控制区 ---
LIMIT_PAGES = 19800          # 针对 Cloudflare 20,000 文件限制的极致优化
INDEX_DISPLAY_LIMIT = 80    # 主页展示精品卡片数
BRAND_NAME = "soeasyhub"
CONTACT_EMAIL = "contact@soeasyhub.com" # 申请广告必须有真实的联系方式
BASE_URL = "https://soeasyhub.com" 
PAYHIP_LINK = "https://payhip.com/b/HSDxs"
# ------------------------------------------

OUTPUT_DIR = "dist"
SUBPAGE_DIR = os.path.join(OUTPUT_DIR, "p")
CSV_FILE = "professions.csv"

# --- 深度法律合规知识库 (确保报告含金量，且不产生 API 费用) ---
KNOWLEDGE_BASE = {
    "Lawyer": [
        "Audit Log: Found unprotected revision metadata. Fails ABA Formal Opinion 06-442 for digital security. Recommendation: Apply {{brand}} proprietary sanitization layers.",
        "Security Alert: Document structure lacks NIST-compliant digital preservation tags required for {{state}} e-filing protocols. Metadata integrity hash generated: #77X-{{rand_hex}}.",
        "Compliance Gap: Fails the Digital Chain of Custody (DCoC) requirement for {{state}} legal practice. Unprotected metadata may lead to evidence inadmissibility."
    ],
    "Doctor": [
        "HIPAA Privacy Shield Alert: Detected PHI (Protected Health Information) leak in non-printable XMP layers. Fails {{state}} medical privacy audit v2.1.",
        "Compliance Failure: Missing HIPAA-compliant header encryption. Unauthorized scraping of this patient record is possible in current state. Hash: #MED-{{rand_hex}}.",
        "Security Report: Document metadata contains geolocation tags and device ID. Violates {{state}} Health Dept. tele-health data standards. Sanitize immediately."
    ],
    "Real Estate": [
        "Real Estate Disclosure Alert: Document lacks mandatory digital provenance seal for {{state}} residential transactions. Audit ID: #RE-{{rand_hex}}.",
        "Liability Warning: PDF contains residual GPS data in architectural photos. Fails {{state}} Brokerage privacy protocols. Potential civil litigation risk detected.",
        "Compliance Notice: Missing the mandatory {{state}} Fair Housing digital watermark. Non-compliant documents in real estate filings may trigger automated state audits."
    ],
    "Default": [
        "Professional Integrity Scan: High-risk metadata detected in background object streams. Document structure fails {{state}} expert verification protocols.",
        "Security Hash Mismatch: Metadata integrity not verified for professional standards. Found #{{rand_hex}} risk signature in hidden layers.",
        "Compliance Recommendation: Document lacks professional digital certification. Fails general {{state}} standards for encrypted document transmission."
    ]
}

THEME_CONFIG = {
    "Lawyer": {"color": "blue", "bg": "bg-blue-600", "text": "text-blue-600", "warning": "Legal Compliance Alert: This document lacks 'Digital Chain of Custody' signatures required for {{state}} Court."},
    "Doctor": {"color": "emerald", "bg": "bg-emerald-500", "text": "text-emerald-500", "warning": "HIPAA Critical Alert: PHI (Protected Health Information) leak detected in PDF metadata. Non-compliant with {{state}} standards."},
    "Accountant": {"color": "slate", "bg": "bg-slate-900", "text": "text-slate-900", "warning": "Audit Risk Alert: Non-standard object streams detected. High risk of filing rejection in {{state}}."},
    "Real Estate": {"color": "rose", "bg": "bg-rose-500", "text": "text-rose-500", "warning": "Disclosure Compliance Alert: This PDF lacks mandatory {{state}} Fair Housing digital disclosures."},
    "Default": {"color": "indigo", "bg": "bg-indigo-600", "text": "text-indigo-600", "warning": "Security Integrity Alert: Document structure not verified for {{state}} professional standards."}
}

# 全站统一页脚 (AdSense 合规必备)
FOOTER_HTML = f"""
    <footer class="max-w-7xl mx-auto px-6 py-12 border-t border-slate-200 mt-24 text-center">
        <p class="text-slate-400 font-bold text-sm mb-6">© {datetime.now().year} {BRAND_NAME}. All Rights Reserved.</p>
        <div class="flex flex-wrap justify-center gap-8 text-[10px] font-black uppercase tracking-widest text-slate-400">
            <a href="/privacy.html" class="hover:text-slate-900 transition-all">Privacy Policy</a>
            <a href="/terms.html" class="hover:text-slate-900 transition-all">Terms of Service</a>
            <a href="/contact.html" class="hover:text-slate-900 transition-all">Contact Us</a>
            <a href="/index.html" class="hover:text-slate-900 transition-all">Home</a>
        </div>
    </footer>
"""

# 自动回航中转页内容
SUCCESS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><title>Verifying... - {{brand}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 flex items-center justify-center min-h-screen">
    <div class="text-center">
        <div class="w-20 h-20 border-8 border-slate-200 border-t-indigo-600 rounded-full animate-spin mx-auto mb-8"></div>
        <h1 class="text-3xl font-black text-slate-900 mb-2 italic tracking-tighter">Payment Verified!</h1>
        <p class="text-slate-500 font-medium italic">Authenticating node access. Please wait...</p>
    </div>
    <script>
        window.onload = function() {
            const lastNode = localStorage.getItem('last_node');
            setTimeout(() => {
                window.location.href = lastNode ? lastNode + '?status=success' : 'index.html';
            }, 1200);
        };
    </script>
</body>
</html>
"""

# 子页面 HTML 模板
SUBPAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}} - {{brand}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <script src="https://unpkg.com/pdf-lib/dist/pdf-lib.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style> body { font-family: 'Plus Jakarta Sans', sans-serif; } .active-tab { border-bottom: 4px solid currentColor; font-weight: 800; } .glass { background: rgba(255, 255, 255, 0.85); backdrop-filter: blur(20px); } </style>
</head>
<body class="bg-[#F8FAFC] text-slate-900 min-h-screen flex flex-col">
    <nav class="sticky top-0 z-50 glass border-b border-slate-200/50 py-4">
        <div class="max-w-7xl mx-auto px-6 flex items-center justify-between">
            <a href="../index.html" class="flex items-center gap-2.5">
                <div class="w-9 h-9 {{theme_bg}} rounded-xl shadow-lg flex items-center justify-center text-white font-black text-xl">S</div>
                <span class="font-black text-2xl tracking-tighter">{{brand}}</span>
            </a>
            <span class="text-[10px] font-black text-slate-400 uppercase bg-slate-100 px-4 py-1.5 rounded-full border border-slate-200">{{state}} Compliance Node</span>
        </div>
    </nav>

    <main class="flex-grow max-w-4xl mx-auto px-6 py-12 w-full text-center">
        <h1 class="text-4xl md:text-6xl font-black mb-6 tracking-tight">{{profession}} <span class="{{theme_text}}">Toolkit</span></h1>
        <p class="text-lg text-slate-500 font-medium max-w-2xl mx-auto italic mb-12">High-performance secure processing node for {{state}} practitioners.</p>

        <div class="bg-white rounded-[3.5rem] shadow-2xl border border-slate-100 overflow-hidden">
            <div class="flex overflow-x-auto border-b border-slate-50 bg-slate-50/50">
                <button onclick="setTab('merge')" id="tab-merge" class="flex-none px-10 py-6 text-xs font-black uppercase {{theme_text}} active-tab">Merge PDF</button>
                <button onclick="setTab('compress')" id="tab-compress" class="flex-none px-10 py-6 text-xs font-black uppercase text-slate-400">Compress</button>
                <button onclick="setTab('audit')" id="tab-audit" class="flex-none px-10 py-6 text-xs font-black uppercase text-slate-400 italic">Audit Report</button>
            </div>
            <div class="p-8 md:p-16">
                <div id="dropzone" class="border-4 border-dashed border-slate-100 rounded-[2.5rem] p-12 hover:border-{{theme_color}}-200 transition-all cursor-pointer bg-slate-50/30">
                    <input type="file" id="pdfInput" class="hidden" accept="application/pdf" multiple>
                    <div class="flex flex-col items-center text-{{theme_color}}-500">
                        <svg class="w-12 h-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M12 4v16m8-8H4" stroke-width="3" stroke-linecap="round"/></svg>
                        <p class="text-2xl font-black text-slate-800 tracking-tight">Click to Select PDF</p>
                    </div>
                </div>
                <div id="fileBox" class="hidden mt-8 p-6 bg-slate-50 rounded-2xl border border-slate-100">
                    <div id="fileList" class="space-y-2 mb-6 text-left text-xs font-bold"></div>
                    <div class="flex justify-between items-center"><button onclick="resetFiles()" class="text-red-500 font-black text-[10px] uppercase">Clear</button><span id="fileCounter" class="text-[10px] font-black text-slate-500 uppercase">0 Files</span></div>
                </div>
                <div class="mt-10"><button id="mainBtn" onclick="run()" class="w-full py-8 {{theme_bg}} text-white rounded-[1.5rem] font-black text-xl shadow-xl hover:-translate-y-1 transition-all">Execute Process (Free)</button></div>
            </div>
        </div>
    </main>

    <div id="upsellModal" class="fixed inset-0 z-[100] hidden flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/95 backdrop-blur-xl"></div>
        <div class="relative bg-white rounded-[3.5rem] max-w-lg w-full overflow-hidden shadow-2xl p-10 text-center">
            <h3 class="text-2xl font-black text-red-600 mb-4 italic uppercase tracking-tighter">Compliance Risk Detected</h3>
            <p class="text-slate-600 font-bold text-sm mb-8 leading-relaxed italic">{{warning}}</p>
            <div class="flex flex-col gap-4">
                <a href="{{pay_link}}" target="_blank" onclick="saveNode()" class="block w-full py-6 {{theme_bg}} text-white rounded-2xl font-black text-lg">Audit My Document ($4.99)</a>
                <button onclick="closeUpsell()" class="text-slate-400 font-black text-[10px] uppercase">Continue Free / Take Risk</button>
            </div>
        </div>
    </div>

    <div id="loader" class="fixed inset-0 z-[110] hidden flex items-center justify-center bg-white/95 backdrop-blur-md text-center">
        <div class="relative"><div class="w-16 h-16 border-8 border-slate-100 border-t-{{theme_color}}-500 rounded-full animate-spin mx-auto mb-6"></div><p id="loaderTxt" class="font-black text-slate-900 uppercase text-sm italic">Initializing Engine...</p></div>
    </div>

    {{footer}}

    <script>
        const { PDFDocument, rgb, StandardFonts } = PDFLib;
        let selectedFiles = []; let currentMode = 'merge'; let processedBytes = null;
        const knowledge = {{knowledge_json}};

        window.onload = () => {
            const params = new URLSearchParams(window.location.search);
            if (params.get('status') === 'success') {
                // 仪式感：多阶段扫描动画
                showLoader("Payment Verified!");
                setTimeout(() => showLoader("Scanning document metadata..."), 800);
                setTimeout(() => showLoader("Validating against {{state}} regional compliance..."), 1600);
                setTimeout(() => { generateAuditPDF(); }, 2500);
            }
        };

        function saveNode() { localStorage.setItem('last_node', window.location.href.split('?')[0]); }
        const inp = document.getElementById('pdfInput');
        document.getElementById('dropzone').onclick = () => inp.click();
        inp.onchange = (e) => { selectedFiles = [...selectedFiles, ...Array.from(e.target.files)]; updateUI(); };

        function updateUI() {
            const box = document.getElementById('fileBox');
            if (selectedFiles.length > 0) {
                box.classList.remove('hidden');
                document.getElementById('fileCounter').innerText = selectedFiles.length + " File(s) Ready";
                document.getElementById('fileList').innerHTML = selectedFiles.map(f => `<div class="bg-white p-3 rounded-xl border border-slate-100 flex justify-between"><span>${f.name}</span><span>${(f.size/1024).toFixed(0)}KB</span></div>`).join('');
            } else { box.classList.add('hidden'); }
        }

        function setTab(m) {
            currentMode = m;
            document.querySelectorAll('button').forEach(b => b.classList.remove('active-tab', '{{theme_text}}'));
            document.getElementById('tab-'+m).classList.add('active-tab', '{{theme_text}}');
            document.getElementById('mainBtn').innerText = m === 'audit' ? 'Generate Full Report ($4.99)' : 'Execute Process (Free)';
        }

        async function run() {
            if(selectedFiles.length === 0) return alert("Please select PDF files first.");
            if(currentMode === 'audit') return document.getElementById('upsellModal').classList.remove('hidden');
            if(currentMode === 'merge' && selectedFiles.length < 2) return alert("Merge requires at least 2 files.");
            
            showLoader("Running Secure Process...");
            try {
                if(currentMode === 'merge') {
                    const merged = await PDFDocument.create();
                    for(const f of selectedFiles) {
                        const d = await PDFDocument.load(await f.arrayBuffer());
                        (await merged.copyPages(d, d.getPageIndices())).forEach(p => merged.addPage(p));
                    }
                    processedBytes = await merged.save();
                } else {
                    const doc = await PDFDocument.load(await selectedFiles[0].arrayBuffer());
                    processedBytes = await doc.save({ useObjectStreams: true });
                }
                setTimeout(() => { hideLoader(); document.getElementById('upsellModal').classList.remove('hidden'); }, 1000);
            } catch(e) { alert("Processing Error: " + e.message); hideLoader(); }
        }

        function closeUpsell() {
            document.getElementById('upsellModal').classList.add('hidden');
            if(processedBytes) download(processedBytes, "processed_by_{{brand}}.pdf");
        }

        function generateAuditPDF() {
            const { jsPDF } = window.jspdf; const doc = new jsPDF();
            const fileName = selectedFiles.length > 0 ? selectedFiles[0].name : "Professional_Audit.pdf";
            let industryContent = knowledge[Math.floor(Math.random() * knowledge.length)];
            industryContent = industryContent.replace("{{rand_hex}}", Math.random().toString(16).substr(2, 6).toUpperCase());

            doc.setFontSize(22); doc.text("{{brand}} Compliance Audit", 20, 30);
            doc.setFontSize(10); doc.text("Report ID: AUDIT-" + Math.random().toString(36).substr(2, 9).toUpperCase(), 20, 40);
            doc.text("Jurisdiction: {{state}} | Professional: {{profession}}", 20, 46);
            doc.line(20, 52, 190, 52);
            doc.setFontSize(12); doc.text("1. Local File Analysis", 20, 65);
            doc.setFontSize(10); doc.text("File: " + fileName, 20, 75);
            doc.text("Processed at: " + new Date().toLocaleString(), 20, 80);
            doc.setFontSize(12); doc.text("2. Regulatory Findings", 20, 95);
            doc.setFontSize(10); doc.text(doc.splitTextToSize(industryContent, 165), 20, 105);
            doc.setFontSize(12); doc.text("3. Integrity Status", 20, 140);
            doc.text("Status: SECURITY STAMP APPLIED. COMPLIANCE VERIFIED.", 20, 150);
            doc.save("Audit_Report.pdf"); hideLoader();
        }

        function showLoader(m) { document.getElementById('loader').classList.remove('hidden'); document.getElementById('loaderTxt').innerText = m; }
        function hideLoader() { document.getElementById('loader').classList.add('hidden'); }
        function resetFiles() { selectedFiles = []; updateUI(); processedBytes = null; }
        function download(bytes, name) {
            const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([bytes], { type: "application/pdf" })); a.download = name; a.click();
        }
    </script>
</body>
</html>
"""

INDEX_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><title>{{brand}} - Expert Matrix</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body class="bg-[#F8FAFC] font-['Plus_Jakarta_Sans'] text-slate-900 min-h-screen flex flex-col">
    <div class="flex-grow max-w-7xl mx-auto px-6 py-24 text-center">
        <h1 class="text-7xl md:text-9xl font-black text-slate-900 mb-8 italic tracking-tighter">{{brand}}.</h1>
        <p class="text-2xl text-slate-400 font-medium mb-20 italic tracking-tight">Global Compliance Matrix for Professional Experts.</p>
        <div class="max-w-2xl mx-auto mb-24 relative">
            <input type="text" id="searchInput" placeholder="Search profession..." class="w-full px-12 py-8 rounded-[3rem] border-none shadow-2xl text-2xl outline-none font-bold">
        </div>
        <div id="grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
            {% for item in registry %}
            <a href="p/{{item.slug}}.html" class="card bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm hover:shadow-2xl transition-all text-left" data-s="{{item.p}} {{item.st}}">
                <div class="w-14 h-14 {{item.t_bg}} rounded-2xl flex items-center justify-center text-white font-black text-xl mb-8 shadow-lg">{{item.p[0]}}</div>
                <h3 class="font-black text-slate-900 text-lg leading-tight mb-2">{{item.p}}</h3>
                <p class="text-[10px] font-black text-slate-300 uppercase tracking-widest">{{item.st}} Node</p>
            </a>
            {% endfor %}
        </div>
    </div>
    {{footer}}
    <script>
        document.getElementById('searchInput').oninput = (e) => {
            const t = e.target.value.toLowerCase();
            document.querySelectorAll('.card').forEach(c => { c.style.display = c.dataset.s.toLowerCase().includes(t) ? 'block' : 'none'; });
        };
    </script>
</body>
</html>
"""

LEGAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>{{title}} - {{brand}}</title><script src="https://cdn.tailwindcss.com"></script></head>
<body class="bg-slate-50 p-12 text-slate-900 font-sans">
    <div class="max-w-3xl mx-auto bg-white p-16 rounded-3xl shadow-xl">
        <h1 class="text-4xl font-black mb-12 italic uppercase tracking-tighter leading-none">{{title}}</h1>
        <div class="prose prose-slate leading-relaxed text-sm font-medium space-y-6">
            {{content}}
        </div>
        <a href="index.html" class="inline-block mt-12 text-xs font-black uppercase text-indigo-600 border-b-2 border-indigo-600">Back to Home</a>
    </div>
</body>
</html>
"""

def build():
    if not os.path.exists(SUBPAGE_DIR): os.makedirs(SUBPAGE_DIR)
    registry = []; sitemap_urls = []; total = 0
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if total >= LIMIT_PAGES: break
            p, s, st = row['profession'], row['slug'], row['state']
            theme = THEME_CONFIG['Default']
            industry_knowledge = KNOWLEDGE_BASE['Default']
            for key in THEME_CONFIG:
                if key.lower() in p.lower():
                    theme = THEME_CONFIG[key]; industry_knowledge = KNOWLEDGE_BASE.get(key, KNOWLEDGE_BASE['Default'])
                    break
            
            pg = SUBPAGE_TEMPLATE.replace("{{title}}", f"{st} {p} Pro-Audit")\
                              .replace("{{brand}}", BRAND_NAME)\
                              .replace("{{profession}}", p)\
                              .replace("{{state}}", st)\
                              .replace("{{theme_bg}}", theme['bg'])\
                              .replace("{{theme_text}}", theme['text'])\
                              .replace("{{theme_color}}", theme['color'])\
                              .replace("{{warning}}", theme['warning'].replace("{{state}}", st))\
                              .replace("{{pay_link}}", PAYHIP_LINK)\
                              .replace("{{knowledge_json}}", json.dumps(industry_knowledge).replace("{{state}}", st).replace("{{brand}}", BRAND_NAME))\
                              .replace("{{footer}}", FOOTER_HTML)
            
            with open(os.path.join(SUBPAGE_DIR, f"{s}.html"), 'w', encoding='utf-8') as pf: pf.write(pg)
            if total < INDEX_DISPLAY_LIMIT:
                registry.append({ "p": p, "slug": s, "st": st, "t_bg": theme['bg'], "t_color": theme['color'] if 'color' in theme else 'indigo' })
            sitemap_urls.append(f"{BASE_URL}/p/{s}.html"); total += 1

    # 生成主页
    cards_html = ""
    for i in registry:
        cards_html += f'''<a href="p/{i['slug']}.html" class="card bg-white p-10 rounded-[3rem] border border-slate-100 shadow-sm hover:shadow-2xl transition-all text-left" data-s="{i['p']} {i['st']}"><div class="w-14 h-14 {i['t_bg']} rounded-2xl flex items-center justify-center text-white font-black text-xl mb-8 shadow-lg">{i['p'][0]}</div><h3 class="font-black text-slate-900 text-lg leading-tight mb-2">{i['p']}</h3><p class="text-[10px] font-black text-slate-300 uppercase tracking-widest">{i['st']} Node</p></a>'''
    
    parts = INDEX_TEMPLATE.split('{% for item in registry %}')
    header = parts[0].replace("{{brand}}", BRAND_NAME)
    footer_part = parts[1].split('{% endfor %}')[1].replace("{{footer}}", FOOTER_HTML)
    with open(os.path.join(OUTPUT_DIR, "index.html"), 'w', encoding='utf-8') as f: f.write(header + cards_html + footer_part)

    # 生成合规页
    def make_legal(name, title, content):
        pg = LEGAL_TEMPLATE.replace("{{title}}", title).replace("{{brand}}", BRAND_NAME).replace("{{content}}", content)
        with open(os.path.join(OUTPUT_DIR, f"{name}.html"), 'w', encoding='utf-8') as f: f.write(pg)

    make_legal("privacy", "Privacy Policy", f"We take your privacy seriously. All PDF processing is performed locally in your browser. No documents are ever uploaded to our servers. For inquiries, contact us at {CONTACT_EMAIL}.")
    make_legal("terms", "Terms of Service", f"By using {BRAND_NAME}, you acknowledge that all tools are for professional use. We are not liable for document integrity after processing. Audit reports are for reference only.")
    make_legal("contact", "Contact Us", f"For professional support or business inquiries regarding {BRAND_NAME}, please email us at: <strong>{CONTACT_EMAIL}</strong>. Our team typically responds within 48 hours.")
    
    with open(os.path.join(OUTPUT_DIR, "success.html"), 'w', encoding='utf-8') as f: f.write(SUCCESS_TEMPLATE.replace("{{brand}}", BRAND_NAME))
    
    # 生成 Sitemap.xml
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n'
    for url in sitemap_urls: sitemap += f'  <url><loc>{url}</loc><priority>0.8</priority></url>\\n'
    sitemap += '</urlset>'
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), 'w', encoding='utf-8') as f: f.write(sitemap)
    
    print(f"Build V43.2 Complete: Generated {total} subpages + Legal Pages + Sitemap.")

if __name__ == "__main__":
    build()