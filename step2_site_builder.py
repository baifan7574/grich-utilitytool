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
LIMIT_PAGES = 500  # 滴灌策略
BASE_URL = "https://grich-utilitytool.pages.dev" 

# ==========================================
# 2. Michael 专属 HTML 模板 (V2.8 调试增强版)
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
                <span class="text-xs text-slate-400 font-medium tracking-wider uppercase">Michael 调试模式 v2.8</span>
            </div>
        </div>
    </nav>

    <main class="max-w-4xl mx-auto px-4 py-12">
        <div class="text-center mb-12">
            <h1 class="text-4xl font-extrabold text-slate-900 mb-4 tracking-tight">{h1}</h1>
            <p class="text-lg text-slate-600 max-w-2xl mx-auto">{description}</p>
        </div>

        <div class="bg-white rounded-3xl shadow-2xl p-2 border border-slate-100">
            <div class="p-8">
                <!-- 拖拽区 -->
                <div id="drop-zone" class="relative border-2 border-dashed border-slate-200 rounded-2xl p-12 text-center transition-all cursor-pointer hover:border-indigo-300 group">
                    <input type="file" id="pdf-input" class="hidden" accept="application/pdf">
                    <div id="upload-ui">
                        <div class="w-16 h-16 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" /></svg>
                        </div>
                        <p class="text-lg font-bold text-slate-700">拖入 PDF 开始专家审计</p>
                    </div>
                    <!-- 文件就绪 UI -->
                    <div id="file-info-ui" class="hidden animate-in">
                        <div class="w-16 h-16 bg-green-50 text-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
                            <svg class="w-8 h-8" fill="currentColor" viewBox="0 0 20 20"><path d="M9 2a2 2 0 00-2 2v12a2 2 0 002 2h2a2 2 0 002-2V4a2 2 0 00-2-2H9z" /></svg>
                        </div>
                        <p id="file-name" class="text-lg font-bold text-slate-800 truncate px-4"></p>
                    </div>
                </div>

                <div id="action-bar" class="mt-8 hidden animate-in">
                    <button id="generate-btn" class="w-full bg-slate-900 text-white py-5 rounded-2xl font-bold text-lg hover:bg-indigo-600 transition-all shadow-xl">
                        立即生成合规报告
                    </button>
                </div>
            </div>
        </div>
    </main>

    <!-- 支付与验收弹窗 -->
    <div id="pay-modal" class="fixed inset-0 bg-slate-900/80 hidden flex items-center justify-center z-50 p-4 backdrop-blur-sm">
        <div class="bg-white p-8 rounded-3xl max-w-sm w-full text-center shadow-2xl animate-in">
            <div class="mb-6">
                <h3 class="text-2xl font-bold text-slate-900">审计已就绪</h3>
                <p class="text-slate-500 mt-2">行业背景：{niche} ({state})</p>
            </div>
            
            <!-- 真实支付（目前跳过） -->
            <button onclick="alert('生产环境请点击下方模拟支付')" class="block w-full bg-slate-100 text-slate-400 py-4 rounded-2xl font-bold mb-4 cursor-not-allowed">
                正式购买报告 ($4.99)
            </button>
            
            <!-- 模拟支付按钮 - Michael 验收专用 -->
            <button id="test-pay-btn" class="block w-full bg-indigo-600 text-white py-4 rounded-2xl font-bold text-lg hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all">
                Michael 内部验收：模拟支付并出图
            </button>
            
            <button onclick="document.getElementById('pay-modal').classList.add('hidden')" class="mt-6 text-slate-400 text-sm hover:underline">取消</button>
        </div>
    </div>

    <script>
        const dropZone = document.getElementById('drop-zone');
        const pdfInput = document.getElementById('pdf-input');
        const fileNameDisp = document.getElementById('file-name');
        const actionBar = document.getElementById('action-bar');
        const generateBtn = document.getElementById('generate-btn');
        const payModal = document.getElementById('pay-modal');
        const testPayBtn = document.getElementById('test-pay-btn');

        // 变量映射 - 对应 Worker 的 API 参数
        const CONTEXT = {{
            profession: "{niche}",
            state: "{state}",
            action: "{action}",
            filename: ""
        }};

        // 1. 拖拽逻辑
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
                CONTEXT.filename = file.name;
                document.getElementById('upload-ui').classList.add('hidden');
                document.getElementById('file-info-ui').classList.remove('hidden');
                actionBar.classList.remove('hidden');
            }} else {{
                alert("请上传 PDF 文件。");
            }}
        }}

        // 2. 唤起弹窗
        generateBtn.onclick = () => {{
            payModal.classList.remove('hidden');
        }};

        // 3. 模拟支付并生成报告 (核心逻辑修复)
        testPayBtn.onclick = async () => {{
            testPayBtn.disabled = true;
            testPayBtn.innerHTML = '<span class="animate-pulse">正在调用 DeepSeek 生成报告...</span>';
            
            try {{
                // 发送给 Worker 的参数必须包含职业和州，否则报告内容会错
                const response = await fetch('/api/generate-report', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(CONTEXT)
                }});
                
                if (!response.ok) throw new Error("API 响应失败，状态码: " + response.status);

                const data = await response.json();
                if (data.report) {{
                    const {{ jsPDF }} = window.jspdf;
                    const doc = new jsPDF();
                    
                    // 报告页眉
                    doc.setFontSize(22);
                    doc.text("Michael 专家审计报告", 105, 20, {{ align: "center" }});
                    doc.setFontSize(10);
                    doc.text("行业：" + CONTEXT.profession + " | 州：" + CONTEXT.state, 105, 30, {{ align: "center" }});
                    doc.line(20, 35, 190, 35);
                    
                    // 报告正文 (自动换行处理)
                    doc.setFontSize(11);
                    const lines = doc.splitTextToSize(data.report, 170);
                    doc.text(lines, 20, 45);
                    
                    doc.save(`Michael_Report_${{Date.now()}}.pdf`);
                    payModal.classList.add('hidden');
                }} else {{
                    alert("API 返回了空内容，请检查 Cloudflare Worker 的 Prompt 设置。");
                }}
            } catch (e) {{ 
                alert("生成失败！原因：" + e.message + "\\n请检查 API Key 是否配置或 Worker 是否已发布。"); 
            }} finally {{
                testPayBtn.disabled = false;
                testPayBtn.innerText = "Michael 内部验收：模拟支付并出图";
            }}
        }};
    </script>
</body>
</html>
"""

# ==========================================
# 3. 构建主函数
# ==========================================
def build():
    if not os.path.exists(OUTPUT_DIR): os.makedirs(OUTPUT_DIR)
    
    generated_files = []
    try:
        with open(INPUT_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                if count >= LIMIT_PAGES: break
                
                # 法条注入逻辑
                laws = "通用商事合规准则"
                n = row['niche'].lower()
                if any(x in n for x in ["律", "法", "law"]): laws = "ABA Model Rules 2024"
                elif any(x in n for x in ["医", "药", "health"]): laws = "HIPAA Privacy Rule"
                
                content = HTML_TEMPLATE.format(
                    title=row['title'], h1=row['h1'],
                    description=row['description'], niche=row['niche'], 
                    state=row['state'], action=row['action'], laws=laws
                )
                
                filename = row.get('slug', f"audit-{count}") + ".html"
                with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as out:
                    out.write(content)
                count += 1
            print(f"✅ Michael! 已生成 {count} 个调试页面。请去网站点击【模拟支付】验收报告内容！")
    except Exception as e:
        print(f"❌ 构建中断: {str(e)}")

if __name__ == "__main__":
    build()
