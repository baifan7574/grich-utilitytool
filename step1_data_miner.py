import csv
import os

# ==========================================
# GRICH 项目协议 (V42.4) - 脚本 1：全量数据生成器 (终极版)
# ==========================================
# 功能：生成 10,000+ 行职业数据，确保配色系统能正确识别关键词
# ==========================================

OUTPUT_FILE = "professions.csv"

# 扩充职业关键词（确保能精准触发脚本二的颜色系统：蓝/绿/黑/橙/红/紫）
PROFESSIONS = [
    # Lawyer (蓝色)
    "Lawyer", "Attorney", "Legal Consultant", "Paralegal", "Defense Attorney", "Corporate Lawyer", "Family Lawyer",
    # Doctor/Medical (绿色)
    "Doctor", "Surgeon", "Physician", "Dentist", "Pediatrician", "Medical Specialist", "Chiropractor",
    "Nurse", "Registered Nurse", "Medical Assistant", "Pharmacist", "Lab Technician", "Physical Therapist",
    # Accountant/Finance (黑色)
    "Accountant", "CPA", "Tax Auditor", "Financial Analyst", "Investment Banker", "Bookkeeper", "Actuary",
    # Teacher/Education (橙色)
    "Teacher", "Professor", "Tutor", "Education Coordinator", "School Principal", "Academic Advisor",
    # Real Estate (红色)
    "Real Estate Agent", "Broker", "Property Manager", "Real Estate Consultant", "Appraiser",
    # Engineer (青色)
    "Engineer", "Software Developer", "Architect", "Civil Engineer", "Mechanical Engineer", "Data Scientist"
]

# 扩充细分职业以达到 10,000+ 规模
# 我们将职业库扩展到 200+ 个变体，结合 51 个地区（50州 + DC）
SUB_PROFESSIONS = [
    "Senior {}", "Junior {}", "Certified {}", "Professional {}", "Licensed {}", 
    "Lead {}", "Assistant {}", "Associate {}", "Expert {}", "Consulting {}"
]

# 50 个州 + 华盛顿特区
STATES = [
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", 
    "Delaware", "District of Columbia", "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", 
    "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine", "Maryland", "Massachusetts", 
    "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", 
    "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", 
    "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", 
    "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", 
    "Wisconsin", "Wyoming"
]

def generate_data():
    count = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['profession', 'slug', 'state'])
        
        for state in STATES:
            for prof_base in PROFESSIONS:
                for sub in SUB_PROFESSIONS:
                    # 组合出细分职业名，例如：Senior Lawyer
                    full_profession = sub.format(prof_base)
                    
                    # 生成 SEO 友好的 URL 路径，例如：california-senior-lawyer-expert
                    # 替换空格和特殊字符
                    clean_state = state.lower().replace(' ', '-')
                    clean_prof = full_profession.lower().replace(' ', '-')
                    slug = f"{clean_state}-{clean_prof}-expert"
                    
                    writer.writerow([full_profession, slug, state])
                    count += 1
                
    print(f"Success! Generated {count} rows in {OUTPUT_FILE}")
    print("--------------------------------------------------")
    print(f"数据量确认: {count} 行 (已超过 10,000 行目标)")
    print("下一步操作: 请将生成的 professions.csv 交给脚本二运行构建。")

if __name__ == "__main__":
    generate_data()