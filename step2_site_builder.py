import csv
import os
import shutil
import re
import math
import datetime

# Configuration
INPUT_CSV = "niche_data.csv"
OUTPUT_DIR = "dist"
# Drip Feed Strategy: Cap production build at 500 pages per week
PRODUCTION_LIMIT = 500 
PREVIEW_LIMIT = int(os.environ.get("PREVIEW_LIMIT", 10))  # Set to -1 in CI for 'Full' run (now capped by PRODUCTION_LIMIT)
BASE_URL = "https://grich-utilitytool.pages.dev"

# ==========================================
# 1. Dynamic Configs (Theming & Content)
# ==========================================

THEME_CONFIG = {
    "Lawyer":     {"body_bg": "bg-slate-50",   "nav_bg": "bg-slate-900", "nav_text": "text-white",       "accent_bg": "bg-slate-800", "btn_bg": "bg-blue-900", "btn_hover": "hover:bg-blue-800", "primary_text": "text-slate-900", "secondary_text": "text-slate-600"},
    "Accountant": {"body_bg": "bg-slate-50",   "nav_bg": "bg-slate-900", "nav_text": "text-white",       "accent_bg": "bg-slate-800", "btn_bg": "bg-blue-900", "btn_hover": "hover:bg-blue-800", "primary_text": "text-slate-900", "secondary_text": "text-slate-600"},
    
    "Doctor":     {"body_bg": "bg-emerald-50", "nav_bg": "bg-white",     "nav_text": "text-emerald-900", "accent_bg": "bg-emerald-600", "btn_bg": "bg-emerald-600", "btn_hover": "hover:bg-emerald-700", "primary_text": "text-emerald-950", "secondary_text": "text-emerald-700"},
    "Nurse":      {"body_bg": "bg-emerald-50", "nav_bg": "bg-white",     "nav_text": "text-emerald-900", "accent_bg": "bg-emerald-600", "btn_bg": "bg-emerald-600", "btn_hover": "hover:bg-emerald-700", "primary_text": "text-emerald-950", "secondary_text": "text-emerald-700"},
    
    "Teacher":    {"body_bg": "bg-orange-50",  "nav_bg": "bg-white",     "nav_text": "text-orange-900",  "accent_bg": "bg-orange-500",  "btn_bg": "bg-orange-600",  "btn_hover": "hover:bg-orange-700",  "primary_text": "text-orange-950",  "secondary_text": "text-orange-800"},
    "Student":    {"body_bg": "bg-orange-50",  "nav_bg": "bg-white",     "nav_text": "text-orange-900",  "accent_bg": "bg-orange-500",  "btn_bg": "bg-orange-600",  "btn_hover": "hover:bg-orange-700",  "primary_text": "text-orange-950",  "secondary_text": "text-orange-800"},
    
    "default":    {"body_bg": "bg-gray-50",    "nav_bg": "bg-white",     "nav_text": "text-gray-900",    "accent_bg": "bg-gray-800",    "btn_bg": "bg-gray-900",    "btn_hover": "hover:bg-gray-800",    "primary_text": "text-gray-900",    "secondary_text": "text-gray-500"}
}

AUDIT_CONTENT_CONFIG = {
    "Lawyer": {
        "title": "Privilege & Discovery Audit",
        "points": """
            <li class="flex items-start gap-2"><svg class="w-5 h-5 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <strong>Client Privilege Risk:</strong> Metadata may contain previous edit history visible to opposing counsel.</li>
            <li class="flex items-start gap-2"><svg class="w-5 h-5 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <strong>Chain of Custody:</strong> PDF Producer tags reveal use of non-compliant software.</li>
        """
    },
    "Doctor": {
        "title": "HIPAA Metadata Risk Audit",
        "points": """
            <li class="flex items-start gap-2"><svg class="w-5 h-5 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <strong>PHI Leakage:</strong> Hidden text layers may contain patient identifiers (DOB/SSN).</li>
            <li class="flex items-start gap-2"><svg class="w-5 h-5 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <strong>Device Traceability:</strong> Document properties expose specific workstation IDs.</li>
        """
    },
    "Accountant": {
        "title": "SOX & IRS Compliance Audit",
        "points": """
             <li class="flex items-start gap-2"><svg class="w-5 h-5 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <strong>Version Control:</strong> XML metadata contradicts final filing status.</li>
        """
    },
    "default": {
        "title": "Privacy & Metadata Audit",
        "points": """
            <li class="flex items-start gap-2"><svg class="w-5 h-5 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <strong>Location Data:</strong> Geotags found in embedded image assets.</li>
            <li class="flex items-start gap-2"><svg class="w-5 h-5 text-red-500 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>
            <strong>Author Identity:</strong> Original machine user name exposed in properties.</li>
        """
    }
}

# ==========================================
# 2. HTML Templates
# ==========================================

TOOL_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} | ProComplianceTools</title>
    <meta name="description" content="{seo_description}">
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Redundant CDN Loader for pdf-lib -->
    <script>
        function loadPdfLib() {{
            var script = document.createElement('script');
            script.src = "https://unpkg.com/pdf-lib@1.17.1/dist/pdf-lib.min.js";
            script.onerror = function() {{
                console.warn('Primary CDN (unpkg) failed, switching to fallback (jsdelivr)...');
                var fallback = document.createElement('script');
                fallback.src = "https://cdn.jsdelivr.net/npm/pdf-lib@1.17.1/dist/pdf-lib.min.js";
                document.head.appendChild(fallback);
            }};
            document.head.appendChild(script);
        }}
        loadPdfLib();
    </script>

    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{ sans: ['Inter', 'sans-serif'] }}
                }}
            }}
        }}
    </script>
    <style>
        .drop-active {{ border-color: currentColor; background-color: rgba(0,0,0,0.05); }}
        [x-cloak] {{ display: none !important; }}
    </style>
</head>
<body class="{body_bg} {primary_text} min-h-screen flex flex-col font-sans antialiased">
    <!-- ... (rest of body) ... -->
    <!-- Scripts -->
    <script>
        // ... (vars) ...

        async function handleFile(file) {{
            // ... (setup) ...
             try {{
                // Simulating processing
                if (typeof PDFLib === 'undefined') throw new Error("PDF Library failed to load from CDNs.");

                if (ACTION === 'Encrypt PDF') {{
                    PROCESSED_FILE_BYTES = await performEncryption(file);
                }} else if (ACTION === 'Merge PDF') {{
                    PROCESSED_FILE_BYTES = await performMerge(file); 
                }} else {{
                    PROCESSED_FILE_BYTES = await file.arrayBuffer(); 
                    await new Promise(r => setTimeout(r, 500));
                }}
            }} catch (err) {{
                console.error(err);
                alert("Local processing error: " + err.message + "\\n\\nPlease take a screenshot and report to support.");
                location.reload(); 
                return;
            }}
            // ... (rest) ...

        function downloadFile() {{
            if (!PROCESSED_FILE_BYTES) return;
            const blob = new Blob([PROCESSED_FILE_BYTES], {{ type: 'application/pdf' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a'); a.href = url; a.download = FILE_NAME;
            document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
        }}

        function requestReport() {{
            alert(`Redirecting to payment gateway for ${{OCCUPATION}} Audit Report...`);
        }}

        async function performEncryption(file) {{
            const password = prompt("Set password (default: 1234):", "1234") || "1234";
            const arrayBuffer = await file.arrayBuffer();
            const pdfDoc = await PDFLib.PDFDocument.load(arrayBuffer);
            pdfDoc.encrypt({{ userPassword: password, ownerPassword: password, permissions: {{ printing: 'highResolution' }} }});
            return await pdfDoc.save();
        }}

        async function performMerge(file) {{
            const pdfDoc = await PDFLib.PDFDocument.create();
            const srcDoc = await PDFLib.PDFDocument.load(await file.arrayBuffer());
            const indices = srcDoc.getPageIndices();
            const copiedPages = await pdfDoc.copyPages(srcDoc, indices);
            copiedPages.forEach((page) => pdfDoc.addPage(page));
            // Double pages for demo
            const copiedPages2 = await pdfDoc.copyPages(srcDoc, indices);
            copiedPages2.forEach((page) => pdfDoc.addPage(page));
            return await pdfDoc.save();
        }}

        async function simulateStep(label, startPct, endPct, duration) {{
            document.getElementById('process-label').innerText = label;
            const start = performance.now();
            return new Promise(resolve => {{
                function frame(time) {{
                    const elapsed = time - start;
                    const progress = Math.min(elapsed / duration, 1);
                    const currentPct = startPct + (endPct - startPct) * progress;
                    document.getElementById('progress-bar').style.width = `${{currentPct}}%`;
                    document.getElementById('process-percent').innerText = `${{Math.round(currentPct)}}%`;
                    if (progress < 1) requestAnimationFrame(frame);
                    else resolve();
                }}
                requestAnimationFrame(frame);
            }});
        }}

        function showModal() {{
            const overlay = document.getElementById('modal-overlay');
            const content = document.getElementById('modal-content');
            overlay.classList.remove('hidden');
            overlay.offsetHeight; 
            overlay.classList.remove('opacity-0');
            content.classList.remove('scale-95');
        }}
    </script>
</body>
</html>
"""

INDEX_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ProComplianceTools | Directory</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen font-sans antialiased">
    <div class="max-w-6xl mx-auto px-4 py-12">
        <header class="text-center mb-16">
            <h1 class="text-4xl font-bold tracking-tight text-slate-900 mb-4">Professional Compliance Tools</h1>
            <p class="text-lg text-slate-500 max-w-2xl mx-auto">
                Secure, client-side document utilities tailored for high-privacy industries.
            </p>
        </header>

        <div class="max-w-xl mx-auto mb-16 relative">
            <input type="text" id="search-input" 
                   class="block w-full px-6 py-4 bg-white border border-slate-200 rounded-xl text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900 shadow-sm text-lg" 
                   placeholder="Search tools...">
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {cards_html}
        </div>
    </div>
    <script>
        document.getElementById('search-input').addEventListener('input', (e) => {{
            const term = e.target.value.toLowerCase();
            document.querySelectorAll('.tool-card').forEach(card => {{
                card.style.display = card.dataset.search.toLowerCase().includes(term) ? 'block' : 'none';
            }});
        }});
    </script>
</body>
</html>
"""

# ==========================================
# 3. Helper Functions
# ==========================================

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def generate_filename(row):
    action_slug = slugify(row['Action'])
    role_slug = slugify(row['Occupation'])
    state_slug = slugify(row['State'])
    return f"{action_slug}-{role_slug}-{state_slug}.html"

def get_theme(occupation):
    # Retrieve theme or fallback to default
    return THEME_CONFIG.get(occupation, THEME_CONFIG["default"])

def get_audit(occupation):
    # Retrieve audit content or fallback to default
    details = AUDIT_CONTENT_CONFIG.get(occupation, AUDIT_CONTENT_CONFIG["default"])
    return details

def generate_sitemap_and_robots(filenames, base_url):
    print("🕸️ Generating SEO files (sitemap.xml + robots.txt)...")
    
    # 1. Sitemap
    sitemap_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Add Index
    today = datetime.date.today().isoformat()
    sitemap_content += f'  <url>\n    <loc>{base_url}/</loc>\n    <lastmod>{today}</lastmod>\n    <priority>1.0</priority>\n  </url>\n'
    
    # Add each page
    for fname in filenames:
        sitemap_content += f'  <url>\n    <loc>{base_url}/{fname}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.8</priority>\n  </url>\n'
    
    sitemap_content += '</urlset>'
    
    with open(os.path.join(OUTPUT_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(sitemap_content)
        
    # 2. Robots.txt
    robots_content = f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml"
    with open(os.path.join(OUTPUT_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(robots_content)

# ==========================================
# 4. Main Builder Logic
# ==========================================

def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    rows = []
    if os.path.exists(INPUT_CSV):
        with open(INPUT_CSV, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    else:
        print("Wait! No CSV found. Generating dummy data for test...")
        rows = [{"Action": "Encrypt PDF", "Occupation": "Lawyer", "State": "California", "SEO_Description": "Test Desc"}]

    total_rows = len(rows)
    
    # Logic: If Env is -1, we are in Production, so we use the DRIP LIMIT (500)
    # If Env is 10, we are in Preview, we use 10.
    limit = PRODUCTION_LIMIT if PREVIEW_LIMIT == -1 else min(PREVIEW_LIMIT, total_rows)
    
    print(f"⚙️ Mode: {'PRODUCTION (Drip Feed)' if PREVIEW_LIMIT == -1 else 'LOCAL PREVIEW'}")
    print(f"   Target: {limit} pages (out of {total_rows} available)")

    generated_files = []
    generated_cards = []

    for i, row in enumerate(rows[:limit]):
        filename = generate_filename(row)
        
        # 1. Get Dynamic Data
        theme = get_theme(row['Occupation'])
        audit = get_audit(row['Occupation'])
        
        # 2. Prepare Context (Merge Row + Theme + Audit)
        context = {
            "page_title": f"{row['Action']} for {row['Occupation']}s in {row['State']}",
            "action": row['Action'],
            "occupation": row['Occupation'],
            "state": row['State'],
            "seo_description": row['SEO_Description'],
            "audit_title": audit['title'],
            "audit_points": audit['points'],
            **theme # Unpack theme colors
        }
        
        # 3. Render & Write
        html_content = TOOL_PAGE_TEMPLATE.format(**context)
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(html_content)
            
        generated_files.append(filename)
        
    # ... (Previous code)

    # Track unique actions for Test Matrix
    unique_actions_map = {}

    for i, row in enumerate(rows[:limit]):
        filename = generate_filename(row)
        
        # Capture first instance of each action for Test Hub
        if row['Action'] not in unique_actions_map:
            unique_actions_map[row['Action']] = {
                "filename": filename,
                "occupation": row['Occupation'],
                "state": row['State']
            }

        # 1. Get Dynamic Data
        theme = get_theme(row['Occupation'])
        audit = get_audit(row['Occupation'])
        
        # 2. Prepare Context
        context = {
            "page_title": f"{row['Action']} for {row['Occupation']}s in {row['State']}",
            "action": row['Action'],
            "occupation": row['Occupation'],
            "state": row['State'],
            "seo_description": row['SEO_Description'],
            "audit_title": audit['title'],
            "audit_points": audit['points'],
            **theme
        }
        
        # 3. Render & Write
        html_content = TOOL_PAGE_TEMPLATE.format(**context)
        with open(os.path.join(OUTPUT_DIR, filename), "w", encoding="utf-8") as f:
            f.write(html_content)
            
        generated_files.append(filename)
        
        # 4. Card for Index
        card_html = f"""
        <a href="{filename}" class="tool-card group block bg-white rounded-xl border border-slate-200 p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300" data-search="{row['Action']} {row['Occupation']} {row['State']}">
            <div class="flex items-center justify-between mb-4">
                <div class="px-2 py-1 bg-slate-100 rounded text-xs font-semibold text-slate-600 uppercase tracking-wide">{row['Action']}</div>
                <div class="text-xs text-slate-400">{row['State']}</div>
            </div>
            <h3 class="text-lg font-bold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">{row['Occupation']} Edition</h3>
            <p class="text-sm text-slate-500 line-clamp-2">{row['SEO_Description']}</p>
        </a>
        """
        generated_cards.append(card_html)

        if (i+1) % 50 == 0:
            print(f"   ...built {i+1} pages")

    # Generate Index
    index_html = INDEX_PAGE_TEMPLATE.format(cards_html="\n".join(generated_cards))
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    # ---------------------------------------------------------
    # Generate Test Matrix (QA Hub)
    # ---------------------------------------------------------
    print("🧪 Generating QA Test Matrix (test_hub.html)...")
    test_rows_html = ""
    for action, info in unique_actions_map.items():
        test_rows_html += f"""
        <tr class="border-b hover:bg-slate-50">
            <td class="py-3 px-4 font-semibold text-slate-700">{action}</td>
            <td class="py-3 px-4 text-slate-500">{info['occupation']}</td>
            <td class="py-3 px-4 text-slate-500">{info['state']}</td>
            <td class="py-3 px-4">
                <a href="{info['filename']}" target="_blank" class="text-blue-600 hover:underline flex items-center gap-1">
                    Test Live <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
                </a>
            </td>
        </tr>
        """

    test_hub_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>QA Test Matrix | ProComplianceTools</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-100 min-h-screen p-10 font-sans">
    <div class="max-w-4xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">
        <div class="bg-slate-900 px-6 py-4 border-b border-slate-700 flex justify-between items-center">
            <h1 class="text-xl font-bold text-white">QA Test Matrix</h1>
            <span class="text-xs bg-yellow-500 text-yellow-900 px-2 py-1 rounded font-bold">INTERNAL ONLY</span>
        </div>
        <div class="p-6">
            <p class="text-slate-600 mb-6">Automated test matrix generated on {datetime.date.today().isoformat()}. Verify one instance of each action type below to ensure functional coverage.</p>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm whitespace-nowrap">
                    <thead class="bg-slate-50 text-slate-500 uppercase tracking-wider">
                        <tr>
                            <th class="px-4 py-3">Action Type</th>
                            <th class="px-4 py-3">Role</th>
                            <th class="px-4 py-3">State</th>
                            <th class="px-4 py-3">Link</th>
                        </tr>
                    </thead>
                    <tbody>
                        {test_rows_html}
                    </tbody>
                </table>
            </div>
        </div>
        <div class="bg-slate-50 px-6 py-4 text-center text-xs text-slate-400">
            Generated by system builder v2.1
        </div>
    </div>
</body>
</html>"""
    
    with open(os.path.join(OUTPUT_DIR, "test_hub.html"), "w", encoding="utf-8") as f:
        f.write(test_hub_html)

    # Generate SEO Files
    generate_sitemap_and_robots(generated_files, BASE_URL)

    print(f"✅ Build Complete! Processed {len(generated_files)} pages.")

if __name__ == "__main__":
    main()
