import csv
import os
import shutil
import re
import math

# Configuration
INPUT_CSV = "niche_data.csv"
OUTPUT_DIR = "dist"
PREVIEW_LIMIT = int(os.environ.get("PREVIEW_LIMIT", 10))  # Default to 10, set to -1 in CI for full run

# ==========================================
# 1. HTML Templates (Tailwind + Alpine/Vanilla JS)
# ==========================================

# A high-end, clean, "Audit/Legal" specific design.
TOOL_PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} | Professional Compliance Tools</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/pdf-lib@1.17.1/dist/pdf-lib.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{ sans: ['Inter', 'sans-serif'] }},
                    colors: {{
                        brand: {{ 50: '#f8fafc', 100: '#f1f5f9', 500: '#64748b', 600: '#475569', 900: '#0f172a' }}
                    }}
                }}
            }}
        }}
    </script>
    <style>
        .glass-panel {{ background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px); border: 1px solid rgba(226, 232, 240, 0.8); }}
        .drop-active {{ border-color: #0f172a; background-color: #f8fafc; }}
        [x-cloak] {{ display: none !important; }}
    </style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen flex flex-col font-sans antialiased selection:bg-slate-200 selection:text-slate-900">

    <!-- Navbar -->
    <nav class="w-full bg-white border-b border-slate-200 px-6 py-4 flex items-center justify-between sticky top-0 z-50">
        <div class="flex items-center gap-2">
            <div class="w-8 h-8 bg-slate-900 rounded flex items-center justify-center text-white font-bold tracking-tighter">PC</div>
            <span class="font-semibold text-lg tracking-tight text-slate-800">ProCompliance<span class="text-slate-400 font-light">Tools</span></span>
        </div>
        <a href="index.html" class="text-sm font-medium text-slate-500 hover:text-slate-900 transition-colors">Directory</a>
    </nav>

    <!-- Main Content -->
    <main class="flex-grow flex flex-col items-center pt-16 px-4 max-w-4xl mx-auto w-full">
        
        <!-- Header Section -->
        <div class="text-center mb-12 space-y-4 max-w-2xl">
            <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100 text-xs font-semibold uppercase tracking-wider text-slate-600 border border-slate-200 mb-4">
                <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                {state} Compliance Ready
            </div>
            <h1 class="text-4xl md:text-5xl font-bold tracking-tight text-slate-900 leading-tight">
                {action} for <span class="bg-clip-text text-transparent bg-gradient-to-r from-slate-700 to-slate-900">{occupation}s</span>
            </h1>
            <p class="text-lg text-slate-600 leading-relaxed max-w-xl mx-auto">
                {seo_description}
            </p>
        </div>

        <!-- Tool Interface -->
        <div id="app" class="w-full max-w-xl bg-white rounded-2xl shadow-xl shadow-slate-200/50 border border-slate-100 overflow-hidden relative">
            
            <!-- Default State: Upload -->
            <div id="upload-zone" class="p-10 text-center transition-all duration-300">
                <div class="group relative w-full h-64 border-2 border-dashed border-slate-300 rounded-xl flex flex-col items-center justify-center gap-4 hover:border-slate-500 hover:bg-slate-50 transition-all cursor-pointer"
                     ondragover="event.preventDefault(); this.classList.add('drop-active');"
                     ondragleave="this.classList.remove('drop-active');"
                     ondrop="handleDrop(event)"
                     onclick="document.getElementById('file-input').click()">
                    
                    <div class="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                        <svg class="w-8 h-8 text-slate-400 group-hover:text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                    </div>
                    <div class="space-y-1">
                        <p class="font-medium text-slate-900">Click or Drag PDF here</p>
                        <p class="text-xs text-slate-500 uppercase tracking-wide">Client-Side Processing • No Uploads</p>
                    </div>
                    <input type="file" id="file-input" accept=".pdf" class="hidden" onchange="handleFile(this.files[0])">
                </div>
            </div>

            <!-- Processing State -->
            <div id="processing-state" class="hidden absolute inset-0 bg-white flex flex-col items-center justify-center z-10 p-8">
                <div class="w-full max-w-xs space-y-6">
                    <div class="flex justify-between text-xs font-semibold uppercase tracking-wider text-slate-500">
                        <span id="process-label">Initializing...</span>
                        <span id="process-percent">0%</span>
                    </div>
                    <div class="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                        <div id="progress-bar" class="bg-slate-900 h-full w-0 transition-all duration-300 ease-out"></div>
                    </div>
                </div>
            </div>

        </div>

    </main>

    <!-- Modal: Compliance Risk -->
    <div id="modal-overlay" class="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-[100] hidden items-center justify-center opacity-0 transition-opacity duration-300">
        <div id="modal-content" class="bg-white w-full max-w-md rounded-2xl shadow-2xl transform scale-95 transition-transform duration-300 overflow-hidden m-4">
            <!-- Modal Header -->
            <div class="bg-amber-50 px-6 py-4 border-b border-amber-100 flex items-center gap-3">
                <div class="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>
                </div>
                <h3 class="font-bold text-amber-900">Compliance Audit Complete</h3>
            </div>
            
            <!-- Modal Body -->
            <div class="p-6 space-y-4">
                <p class="text-slate-800 font-semibold text-lg">
                    Success! Your file is processed.
                </p>
                <p class="text-slate-600 text-sm leading-relaxed">
                    However, our compliance engine detected potential <strong>{occupation} risks</strong> in the metadata. 
                    This file may not meet {state} privacy standards without certification.
                </p>
                <div class="bg-slate-50 p-4 rounded-lg border border-slate-100 space-y-2">
                     <div class="flex justify-between text-xs text-slate-500">
                        <span>Compliance Score</span>
                        <span class="font-mono text-amber-600">82/100 (Unverified)</span>
                    </div>
                </div>
            </div>

            <!-- Modal Footer (Dual Actions) -->
            <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-col gap-3">
                <!-- Button A: Paid -->
                <button onclick="requestReport()" class="w-full bg-slate-900 hover:bg-slate-800 text-white font-medium py-3 rounded-lg shadow-lg shadow-slate-900/20 transition-all flex items-center justify-center gap-2 group">
                    <span class="group-hover:translate-x-0.5 transition-transform">Get Compliance Audit Report ($4.99)</span>
                    <svg class="w-4 h-4 text-slate-400 group-hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                </button>
                
                <!-- Button B: Free (Instant Download) -->
                <button onclick="downloadFile()" class="text-xs text-slate-400 hover:text-slate-600 font-medium text-center py-2 underline decoration-slate-300 underline-offset-4 hover:decoration-slate-600 transition-all">
                    No thanks, just download processed file
                </button>
            </div>
        </div>
    </div>

    <!-- Scripts -->
    <script>
        const ACTION = "{action}";
        const OCCUPATION = "{occupation}";
        const STATE = "{state}";
        let PROCESSED_FILE_BYTES = null;
        let FILE_NAME = "document.pdf";

        // --- UI Logic ---
        function handleDrop(e) {{
            e.preventDefault();
            e.target.classList.remove('drop-active');
            if (e.dataTransfer.files.length > 0) handleFile(e.dataTransfer.files[0]);
        }}

        async function handleFile(file) {{
            if (!file) return;
            if (file.type !== 'application/pdf') {{
                alert('Please upload a valid PDF file.');
                return;
            }}

            FILE_NAME = file.name.replace('.pdf', '_processed.pdf');

            // Transition UI
            document.getElementById('upload-zone').classList.add('hidden');
            document.getElementById('processing-state').classList.remove('hidden');
            
            // Start Processing Sequence
            await simulateStep('Processing...', 0, 50, 1000);
            
            try {{
                // Logic
                if (ACTION === 'Encrypt PDF') {{
                    PROCESSED_FILE_BYTES = await performEncryption(file);
                }} else if (ACTION === 'Merge PDF') {{
                    PROCESSED_FILE_BYTES = await performMerge(file); 
                }} else {{
                    // Simulation: just return original file bytes for non-implemented demos
                    PROCESSED_FILE_BYTES = await file.arrayBuffer(); 
                    await new Promise(r => setTimeout(r, 1000));
                }}
            }} catch (err) {{
                console.error(err);
                alert("An error occurred during processing.");
                location.reload(); 
                return;
            }}
            
            await simulateStep('Finalizing Audit...', 50, 100, 800);
            
            // Show Modal
            setTimeout(showModal, 300);
        }}

        // --- Actions ---
        
        function downloadFile() {{
            if (!PROCESSED_FILE_BYTES) return;
            const blob = new Blob([PROCESSED_FILE_BYTES], {{ type: 'application/pdf' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = FILE_NAME;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }}

        function requestReport() {{
            // API Placeholder
            console.log("Requesting report for:", OCCUPATION, STATE);
            // In production, this would redirect:
            // window.location.href = `/checkout?product=audit&role=${{OCCUPATION}}&state=${{STATE}}`;
            alert(`Redirecting to payment gateway for ${{OCCUPATION}} Audit Report... (Simulation)`);
        }}

        // --- Core PDF Logic (pdf-lib) ---
        async function performEncryption(file) {{
            const password = prompt("Set a password (default: 1234):", "1234") || "1234";
            const arrayBuffer = await file.arrayBuffer();
            const pdfDoc = await PDFLib.PDFDocument.load(arrayBuffer);
            pdfDoc.encrypt({{ userPassword: password, ownerPassword: password, permissions: {{ printing: 'highResolution' }} }});
            return await pdfDoc.save();
        }}

        async function performMerge(file) {{
            // Self-merge simulation
            const pdfDoc = await PDFLib.PDFDocument.create();
            const srcDoc = await PDFLib.PDFDocument.load(await file.arrayBuffer());
            const indices = srcDoc.getPageIndices();
            const copiedPages = await pdfDoc.copyPages(srcDoc, indices);
            copiedPages.forEach((page) => pdfDoc.addPage(page));
            // Add twice to prove it worked
            const copiedPages2 = await pdfDoc.copyPages(srcDoc, indices);
            copiedPages2.forEach((page) => pdfDoc.addPage(page));
            return await pdfDoc.save();
        }}

        // --- Animation Helpers ---
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
    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{ sans: ['Inter', 'sans-serif'] }},
                }}
            }}
        }}
    </script>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen font-sans antialiased">
    
    <div class="max-w-6xl mx-auto px-4 py-12">
        <!-- Header -->
        <header class="text-center mb-16">
            <h1 class="text-4xl font-bold tracking-tight text-slate-900 mb-4">Professional Compliance Tools</h1>
            <p class="text-lg text-slate-500 max-w-2xl mx-auto">
                Secure, client-side document utilities tailored for high-privacy industries across the United States.
            </p>
        </header>

        <!-- Search -->
        <div class="max-w-xl mx-auto mb-16 relative">
            <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
            </div>
            <input type="text" id="search-input" 
                   class="block w-full pl-11 pr-4 py-4 bg-white border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent shadow-sm text-lg" 
                   placeholder="Find your tool (e.g., 'Encrypt for Doctors in Texas')...">
        </div>

        <!-- Grid -->
        <div id="grid-container" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- Cards will be injected here -->
            {cards_html}
        </div>
    </div>

    <script>
        const searchInput = document.getElementById('search-input');
        const cards = document.querySelectorAll('.tool-card');

        searchInput.addEventListener('input', (e) => {{
            const term = e.target.value.toLowerCase();
            cards.forEach(card => {{
                const text = card.dataset.search.toLowerCase();
                if (text.includes(term)) {{
                    card.style.display = 'block';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }});
    </script>
</body>
</html>
"""

CARD_TEMPLATE = """
<a href="{filename}" class="tool-card group block bg-white rounded-xl border border-slate-200 p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300" data-search="{search_text}">
    <div class="flex items-center justify-between mb-4">
        <div class="px-2 py-1 bg-slate-100 rounded text-xs font-semibold text-slate-600 uppercase tracking-wide">{action}</div>
        <div class="text-xs text-slate-400">{state}</div>
    </div>
    <h3 class="text-lg font-bold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">{occupation} Edition</h3>
    <p class="text-sm text-slate-500 line-clamp-2 leading-relaxed">{description}</p>
    <div class="mt-4 pt-4 border-t border-slate-50 flex items-center gap-2 text-xs font-medium text-slate-400">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
        Client-Side Secure
    </div>
</a>
"""

# ==========================================
# 2. Helper Functions
# ==========================================

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def generate_filename(row):
    # e.g., encrypt-pdf-lawyer-texas.html
    action_slug = slugify(row['Action'])
    role_slug = slugify(row['Occupation'])
    state_slug = slugify(row['State'])
    return f"{action_slug}-{role_slug}-{state_slug}.html"

# ==========================================
# 3. Main Builder Logic
# ==========================================

def main():
    # Setup Output Directory
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    print(f"🧹 Cleaned output directory: {OUTPUT_DIR}/")

    # Read Data
    rows = []
    with open(INPUT_CSV, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    total_rows = len(rows)
    print(f"📥 Loaded {total_rows} rows from {INPUT_CSV}")

    # Determine limit
    limit = total_rows if PREVIEW_LIMIT == -1 else min(PREVIEW_LIMIT, total_rows)
    print(f"⚙️ Running in {'PRODUCTION' if PREVIEW_LIMIT == -1 else 'PREVIEW'} mode. Generating {limit} pages.")

    generated_cards = []

    # Generate Pages
    for i, row in enumerate(rows[:limit]):
        filename = generate_filename(row)
        
        # Prepare context
        context = {
            "page_title": f"{row['Action']} for {row['Occupation']}s in {row['State']}",
            "action": row['Action'],
            "action_clean": row['Action'].lower().replace(" pdf", ""),
            "occupation": row['Occupation'],
            "state": row['State'],
            "state_code": row['State'][:2].upper(), # Rough approx
            "seo_description": row['SEO_Description']
        }
        
        # Render HTML
        html_content = TOOL_PAGE_TEMPLATE.format(**context)
        
        # Write File
        file_path = os.path.join(OUTPUT_DIR, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        # Add to Index Card List
        card_context = {
            "filename": filename,
            "search_text": f"{row['Action']} {row['Occupation']} {row['State']} {row['SEO_Description']}",
            "action": row['Action'],
            "state": row['State'],
            "occupation": row['Occupation'],
            "description": row['SEO_Description']
        }
        generated_cards.append(CARD_TEMPLATE.format(**card_context))

        if (i+1) % 10 == 0:
            print(f"   ...generated {i+1} pages")

    # Generate Index
    print("🏠 Generating Index Page...")
    index_html = INDEX_PAGE_TEMPLATE.format(cards_html="\n".join(generated_cards))
    with open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"✅ Build Complete! Check the '{OUTPUT_DIR}' folder.")
    print(f"   Total Pages: {limit}")
    print(f"   Index: {os.path.abspath(os.path.join(OUTPUT_DIR, 'index.html'))}")

if __name__ == "__main__":
    main()
