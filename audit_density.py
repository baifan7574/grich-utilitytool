
import os
import random
from bs4 import BeautifulSoup

def analyze_density():
    # Only pull from dist/p which contains the generated html files
    file_dir = r"d:\quicktoolshub\rader\scenro\dist\p"
    if not os.path.isdir(file_dir):
        print(f"Directory not found: {file_dir}")
        return

    files = [f for f in os.listdir(file_dir) if f.endswith(".html")]
    if not files:
        print("No HTML files found in dist/p")
        return

    # Randomly select 3 files
    selected_files = random.sample(files, 3)
    
    print("=== DENSITY AUDIT START ===")
    
    for filename in selected_files:
        path = os.path.join(file_dir, filename)
        
        # Derive primary keyword from filename (rough approximation)
        # e.g. "alabama-assistant-academic-advisor-expert.html" -> "assistant academic advisor"
        # Removing state and 'expert' suffix
        parts = filename.replace(".html", "").split("-")
        # Removing start 'alabama' (or whatever state) and end 'expert'
        # Heuristic: State is usually first. But state can be multi-word (New York).
        # We know the structure is {state}-{profession}-expert.html from step2_site_builder.py
        # profession might be "assistant-academic-advisor"
        
        keyword_parts = parts[1:-1] # Skip first (state) and last (expert)
        keyword = " ".join(keyword_parts).lower()
        if not keyword:
            keyword = " ".join(parts).lower() # Fallback

        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        
        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True).lower()
        words = text.split()
        total_words = len(words)
        
        # Count keyword occurrences
        # Simple string count in text
        count = text.count(keyword)
        
        # Calculate Density
        # Keyword word count
        kw_len = len(keyword.split())
        # Density = (Count * kw_len) / Total Words
        density = (count * kw_len) / total_words if total_words > 0 else 0
        
        print(f"\n[Page]: {filename}")
        print(f"[Target Keyword]: '{keyword}'")
        print(f"[Total Words]: {total_words}")
        print(f"[Keyword Count]: {count}")
        print(f"[Density]: {density:.2%}")
        
        if 0.01 <= density <= 0.035:
            print("STATUS: HEALTHY (1% - 3.5%)")
        elif density < 0.01:
            print("STATUS: LOW (Consider adding synonyms)")
        else:
            print("STATUS: HIGH (Risk of stuffing)")

    print("\n=== DENSITY AUDIT END ===")

if __name__ == "__main__":
    analyze_density()
