import csv
import random
import os

# ==========================================
# 1. 基础数据定义 (Foundation Data)
# ==========================================

# 10 Most Populous US States
STATES = [
    "California", "Texas", "Florida", "New York", "Pennsylvania",
    "Illinois", "Ohio", "Georgia", "North Carolina", "Michigan"
]

# 6 PDF Actions with specific context hooks
ACTIONS = {
    "Encrypt PDF": {
        "verb": "secure",
        "benefit": "ensure only authorized personnel can access sensitive files",
        "tech_angle": "AES-256 encryption"
    },
    "Merge PDF": {
        "verb": "consolidate",
        "benefit": "combine scattered evidence and reports into a single cohesive dossier",
        "tech_angle": "seamless document stitching"
    },
    "Word to PDF": {
        "verb": "convert",
        "benefit": "preserve formatting and prevent unauthorized editing of contracts",
        "tech_angle": "pixel-perfect layout preservation"
    },
    "Compress PDF": {
        "verb": "optimize",
        "benefit": "email large case files without hitting server attachment limits",
        "tech_angle": "lossless compression algorithms"
    },
    "Split PDF": {
        "verb": "extract",
        "benefit": "isolate specific pages from large regulatory filings",
        "tech_angle": "precision page extraction"
    },
    "OCR PDF": {
        "verb": "digitize",
        "benefit": "make scanned archives fully searchable and editable",
        "tech_angle": "optical character recognition"
    }
}

# 10 High Privacy Occupations with "Soul" (Keywords & Compliance)
OCCUPATIONS = {
    "Lawyer": {
        "compliance": "Attorney-Client Privilege",
        "pain_point": "handling discovery documents",
        "focus": "evidence admissibility",
        "tone": "strictly confidential"
    },
    "Doctor": {
        "compliance": "HIPAA regulations",
        "pain_point": "managing patient health records (PHI)",
        "focus": "patient privacy",
        "tone": "medically compliant"
    },
    "Accountant": {
        "compliance": "SOX and IRS guidelines",
        "pain_point": "preparing tax audits",
        "focus": "financial data integrity",
        "tone": "audit-ready"
    },
    "HR Manager": {
        "compliance": "GDPR and labor laws",
        "pain_point": "archiving employee contracts",
        "focus": "personnel data protection",
        "tone": "discreet"
    },
    "Detective": {
        "compliance": "Chain of Custody protocols",
        "pain_point": "compiling case reports",
        "focus": "investigative integrity",
        "tone": "forensic"
    },
    "Psychologist": {
        "compliance": "ethical confidentiality standards",
        "pain_point": "storing session notes",
        "focus": "client trust",
        "tone": "highly sensitive"
    },
    "Financial Advisor": {
        "compliance": "SEC cybersecurity rules",
        "pain_point": "sharing investment portfolios",
        "focus": "wealth management security",
        "tone": "fiduciary"
    },
    "Government Official": {
        "compliance": "classified information protocols",
        "pain_point": "transmitting inter-agency memos",
        "focus": "national data security",
        "tone": "official"
    },
    "R&D Scientist": {
        "compliance": "IP protection laws",
        "pain_point": "documenting patent findings",
        "focus": "intellectual property theft prevention",
        "tone": "proprietary"
    },
    "Journalist": {
        "compliance": "Source Protection principals",
        "pain_point": "protecting whistleblowers",
        "focus": "freedom of press safety",
        "tone": "encrypted and secure"
    }
}

# ==========================================
# 2. 核心逻辑：注入灵魂生成器 (Soul Injector)
# ==========================================

def generate_seo_description(state, role, action_name):
    """
    Generate a unique, high-quality SEO description.
    """
    action_data = ACTIONS[action_name]
    role_data = OCCUPATIONS[role]
    
    # Templates designed to sound human and professional
    templates = [
        (
            f"For professional {{role}}s in {{state}}, maintaining {{compliance}} is non-negotiable. "
            f"Use our {{action_name}} tool to {{benefit}}. "
            f"Whether you are {{pain_point}} or archiving records, ensure your workflow remains {{tone}}."
        ),
        (
            f"In the high-stakes world of {{state}}'s {{focus}} sector, a {{role}} cannot risk data breaches. "
            f"Effectively {{verb}} your documents with our {{action_name}} solution. "
            f"Designed for {{pain_point}}, it guarantees that specific {{compliance}} standards are met."
        ),
        (
            f"Securely {{verb}} your critical files using advanced {{tech_angle}}. "
            f"Tailored for the {{role}} in {{state}}, this tool addresses the unique challenge of {{pain_point}}. "
            f"Uphold {{compliance}} and protect your clients' interests with every document processed."
        ),
        (
            f"Streamline your workflow without compromising on {{compliance}}. "
            f"Our {{action_name}} utility allows every {{state}}-based {{role}} to {{benefit}}. "
            f"It is the ultimate utility for {{pain_point}}, ensuring your practice stays {{tone}} and efficient."
        )
    ]
    
    # Select a random template
    template = random.choice(templates)
    
    # Fill format
    description = template.format(
        state=state,
        role=role,
        action_name=action_name,
        compliance=role_data["compliance"],
        pain_point=role_data["pain_point"],
        focus=role_data["focus"],
        tone=role_data["tone"],
        verb=action_data["verb"],
        benefit=action_data["benefit"],
        tech_angle=action_data["tech_angle"]
    )
    
    return description

# ==========================================
# 3. 执行生成与导出 (Execution & Export)
# ==========================================

def main():
    data_rows = []
    
    print("🚀 Starting Data Mining Process...")
    
    # Cross-product generation
    for state in STATES:
        for role in OCCUPATIONS.keys():
            for action in ACTIONS.keys():
                desc = generate_seo_description(state, role, action)
                
                # Append to list
                data_rows.append({
                    "State": state,
                    "Occupation": role,
                    "Action": action,
                    "SEO_Description": desc
                })

    print(f"✅ Generated {len(data_rows)} unique data combinations.")

    # 1. Write to CSV
    csv_filename = "niche_data.csv"
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["State", "Occupation", "Action", "SEO_Description"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in data_rows:
            writer.writerow(row)
            
    print(f"💾 CSV Backup saved to: {os.path.abspath(csv_filename)}")

    # 2. Generate SQL Script
    sql_filename = "seed_data.sql"
    table_name = "niche_content" # Assuming a table name
    
    with open(sql_filename, mode="w", encoding="utf-8") as sqlfile:
        sqlfile.write(f"-- Automatic backup generated for Cloudflare D1\n")
        sqlfile.write(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, state TEXT, occupation TEXT, action TEXT, description TEXT);\n")
        sqlfile.write("BEGIN TRANSACTION;\n")
        
        for row in data_rows:
            # Escape single quotes for SQL
            safe_desc = row["SEO_Description"].replace("'", "''")
            safe_state = row["State"].replace("'", "''")
            
            sql = f"INSERT INTO {table_name} (state, occupation, action, description) VALUES ('{safe_state}', '{row['Occupation']}', '{row['Action']}', '{safe_desc}');\n"
            sqlfile.write(sql)
            
        sqlfile.write("COMMIT;\n")

    print(f"💾 SQL Script saved to: {os.path.abspath(sql_filename)}")
    print("🎉 Mission Complete.")

if __name__ == "__main__":
    main()
