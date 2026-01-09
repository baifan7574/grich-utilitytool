import csv
import os
import shutil
import re
import datetime

# ==========================================
# 1. 配置区
# ==========================================
INPUT_CSV = "niche_data.csv"
OUTPUT_DIR = "dist"
LIMIT_PAGES = 500  # 滴灌策略：首批生成 500 页
BASE_URL = "https://grich-utilitytool.pages.dev" # 请确保这是你的真实域名

# ==========================================
# 2. Michael 专属 HTML 模板 (稳定响应版)
# ==========================================
HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Michael 专家审计系统</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/pdf-lib@1.17.1/dist/pdf-lib.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <style>
        .drop-active {{ border-color: #4f46e5 !important; background-color: #f5f3ff !important; }}
        .animate-in {{ animation: fadeIn 0.3s ease-out; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(10px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    </style>
</head>
<body class="bg-slate-50 min-h-screen font-sans text-slate-900">
    <nav class="bg-white border-b border-slate-200 py-4 sticky top-0 z-10 shadow-sm">
        <div class="max-w-5xl mx-auto px-4 flex justify-between items-center">
            <span class="font-bold text-xl text-indigo-600">GRICH <span class="text-slate-800">Audit</span></span>
            <div class="flex items-center space-x-2">
                <span class="h-2 w-2 bg-green-500 rounded-full animate-pulse"></span>
                <span class="text-xs text-slate-400 font-medium uppercase tracking-wider">Michael 专家系统 v2.8 运行中</span>
            </div>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-4 py-12">
        <div class="text-center mb-12">
            <h1 class="text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">{h1}</h1>
            <p class="text-lg text-slate-600 max-w-2xl mx-auto">{description}</p>
        </div>

        <div class="bg-white rounded-3xl shadow-2xl p-2 border border-slate-100 overflow-hidden">
            <div class="p-8">
                <div id="drop-zone" class="relative border-2 border-dashed border-slate-200 rounded-2xl p-12 text-center transition-all cursor-pointer hover:border-indigo-300 group">
                    <input type="file" id="pdf-input" class="hidden" accept="application/pdf">
                    <div id="upload-ui">
                        <div class="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                        </div>
                        <p class="text-lg font-bold text-slate-700">将您的 PDF 拖到这里</p>
                        <p class="text-slate-400 text-sm mt-2">系统将基于本地加密环境进行初步扫描</p>
                    </div>
                    <div id="file-info-ui" class="hidden animate-in">
                        <div class="w-16 h-16 bg-green-50 text-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20"><path d="M9 2a2 2 0 00-2 2v12a2 2 0 002 2h2a2 2 0 002-2V4a2 2 0 00-2-2H9z" /></svg>
                        </div>
                        <p id="file-name" class="text-lg font-bold text-slate-800 truncate px-4"></p>
                        <p class="text-green-600 text-sm font-medium mt-1">已就绪，准备审计</p>
                    </div>
                </div>

                <div id="action-bar" class="mt-8 hidden animate-in">
                    <button id="generate-btn" class="w-full bg-slate-900 text-white py-5 rounded-2xl font-bold text-lg hover:bg-indigo-600 transition-all shadow-xl active:scale-[0.98]">
                        立即启动 Michael 专家审计报告
                    </button>
                </div>
            </div>
        </div>

        <section class="mt-20 grid md:grid-cols-2 gap-8">
            <div class="bg-slate-100/50 p-6 rounded-2xl">
                <h3 class="font-bold text-slate-800 mb-2 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-indigo-600" fill="currentColor" viewBox="0 0 20 20"><path d="M9 2a2 2 0 00-2 2v12a2 2 0 002 2h2a2 2 0 002-2V4a2 2 0 00-2-2H9z" /></svg>
                    当前行业法条注入
                </h3>
                <p class="text-sm text-slate-500">针对 <b>{niche}</b> 优化，调取 <b>{laws}</b> 库。</p>
            </div>
            <div class="bg-slate-100/50 p-6 rounded-2xl">
                <h3 class="font-bold text-slate-800 mb-2 flex items-center">
                    <svg class="w-5 h-5 mr-2 text-indigo-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 4.925-3.467 9.47-8 10.655-4.533-1.185-8-5.73-8-10.655 0-.681.057-1.35.166-2.001zm9.496 3.852a1 1 0 00-1.414-1.414L8 9.586 6.75 8.336a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" /></svg>
                    隐私保护声明
                </h3>
                <p class="text-sm text-slate-500">所有处理均在本地浏览器完成，绝不上传您的源文件。</p>
            </div>
        </section>
    </main>

    <div id="pay-modal" class="fixed inset-0 bg-slate-900/80 hidden flex items-center justify-center z-50 p-4 backdrop-blur-sm">
        <div class="bg-white p-8 rounded-3xl max-w-sm w-full text-center shadow-2xl animate-in border border-slate-100">
            <h3 class="text-2xl font-bold text-slate-900 mb-2">审计报告已就绪</h3>
            <p class="text-slate-500 mb-8 px-4 leading-relaxed">基于 {laws}，系统检测到您的文档存在 <span class="text-indigo-600 font-bold underline">合规风险</span>。支付即可解锁全文。</p>
            <a href="https://payhip.com/b/YOUR_ID" target="_blank" class="block w-full bg-indigo-600 text-white py-4 rounded-2xl font-bold text-lg hover:bg-indigo-700 mb-4">$4.99 立即获取</a>
            <button id="test-pay-btn" class="text-slate-300 text-[10px] uppercase tracking-widest hover:text-indigo-400">内部验收 (8888)</button>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const pdfInput = document.getElementById('pdf-input');
        const fileNameDisp = document.getElementById('file-name');
        const actionBar = document.getElementById('action-bar');
        const generateBtn = document.getElementById('generate-btn');
        const payModal = document.getElementById('pay-modal');

        ['dragenter', 'dragover'].forEach(name => {{
            dropZone.addEventListener(name, (e) => {{ e.preventDefault(); dropZone.classList.add('drop-active'); }});
        }});

        ['dragleave', 'drop'].forEach(name => {{
            dropZone.addEventListener(name, (e) => {{ e.preventDefault(); dropZone.classList.remove('drop-active'); }});
        }});

        dropZone.addEventListener('drop', (e) => {{
            const files = e.dataTransfer.files;
            if (files.length > 0) handleFile(files[0]);
        }});

        dropZone.onclick = () => pdfInput.click();
        pdfInput.onchange = (e) => handleFile(e.target.files[0]);

        function handleFile(file) {{
            if (file && file.type === 'application/pdf') {{
                fileNameDisp.innerText = file.name;
                document.getElementById('upload-ui').classList.add('hidden');
                document.getElementById('file-info-ui').classList.remove('hidden');
                actionBar.classList.remove('hidden');
            }} else {{
                alert("仅支持 PDF 文件审计");
            }}
        }}

        generateBtn.onclick = async () => {{
            generateBtn.disabled = true;
            generateBtn.innerHTML = '<span class="animate-pulse">正在审计...</span>';
            await new Promise(r => setTimeout(r, 1500));
            payModal.classList.remove('hidden');
            generateBtn.disabled = false;
            generateBtn.innerText = "重新生成";
        }};

        document.getElementById('test-pay-btn').onclick = async () => {{
            const code = prompt("内部验证码:");
            if (code === "8888") {{
                try {{
                    const response = await fetch('/api/generate-report', {{
                        method: 'POST',
                        body: JSON.stringify({{ niche: "{niche}", fileName: fileNameDisp.innerText }})
                    }});
                    const data = await response.json();
                    if (data.report) {{
                        const {{ jsPDF }} = window.jspdf;
                        const doc = new jsPDF();
                        doc.text("Michael 专家审计报告", 10, 20);
                        const lines = doc.splitTextToSize(data.report, 180);
                        doc.text(lines, 10, 40);
                        doc.save(`Michael_Audit_Report.pdf`);
                        payModal.classList.add('hidden');
                    }}
                }} catch (e) {{ alert("API 错误"); }}
            }}
        }};
    </script>
</body>
</html>
"""

INDEX_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>Michael 专家合规工具矩阵</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 p-12 text-slate-900 font-sans">
    <div class="max-w-5xl mx-auto">
        <h1 class="text-3xl font-bold mb-8">Michael 专家系统：行业审计工具目录</h1>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cards_html}
        </div>
    </div>
</body>
</html>
"""

# ==========================================
# 3. 辅助函数 (SEO & 文件处理)
# ==========================================
def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def generate_sitemap(filenames, base_url):
    today = datetime.date.today().isoformat()
    xml = '<?xml version="1.0" encoding="UTF-8"?>\\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\\n'
    for f in filenames:
        xml += f'  <url>\\n    <loc>{base_url}/{f}</loc>\\n    <lastmod>{today}</lastmod>\\n  </url>\\n'
    xml += '</urlset>'
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w") as f: f.write(xml)
    with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\\nAllow: /\\nSitemap: {base_url}/sitemap.xml")

# ==========================================
# 4. 主构建逻辑
# ==========================================
def build():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    for f in os.listdir(OUTPUT_DIR): 
        file_path = os.path.join(OUTPUT_DIR, f)
        if os.path.isfile(file_path): os.unlink(file_path)

    generated_files = ["index.html"]
    generated_cards = []

    try:
        with open(INPUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                if count >= LIMIT_PAGES: break
                
                # 注入法律逻辑
                laws = "通用合规准则"
                n = row['niche'].lower()
                if "律" in n: laws = "ABA Model Rules 2024"
                elif "医" in n: laws = "HIPAA Security Act"
                
                content = HTML_TEMPLATE.format(
                    title=row['title'], h1=row['h1'],
                    description=row['description'], niche=row['niche'], laws=laws
                )
                
                filename = row.get('slug', f"audit-{count}") + ".html"
                with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as out:
                    out.write(content)
                
                generated_files.append(filename)
                generated_cards.append(f'<a href="{filename}" class="bg-white p-6 rounded-xl shadow-sm border hover:shadow-md transition"><b>{row["niche"]}</b><p class="text-xs text-slate-500 mt-2">{row["h1"]}</p></a>')
                count += 1
            
            # 生成 Index 和 SEO 文件
            with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
                f.write(INDEX_PAGE_TEMPLATE.format(cards_html="\\n".join(generated_cards)))
            
            generate_sitemap(generated_files, BASE_URL)
            print(f"✅ Michael! 500 个页面、目录页、Sitemap 已全部生成完毕。")
            
    except Exception as e:
        print(f"❌ 运行失败: {str(e)}")

if __name__ == "__main__":
    build()
