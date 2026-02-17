import csv
import os

# ==========================================
# GRICH 项目协议 (V42.5) - 脚本 1：优先级矿机 (Medical First)
# ==========================================
# 功能：生成 20,000+ 行职业数据，Medical Specialist 优先级最高
# 优化：基于 2026-02-02 创始人简报，Medical 已验证 100% CTR
# ==========================================

OUTPUT_FILE = "professions.csv"

# ⭐ 优先级 1：医疗相关（已验证高转化）
MEDICAL_PROFESSIONS = [
    # 医生类
    "Doctor", "Surgeon", "Physician", "Medical Specialist", "Family Doctor",
    "Pediatrician", "Internist", "Cardiologist", "Dermatologist", "Neurologist",
    "Oncologist", "Radiologist", "Anesthesiologist", "Psychiatrist", "Orthopedist",
    # 护理类
    "Nurse", "Registered Nurse", "Nurse Practitioner", "Medical Assistant", "Nursing Specialist",
    # 牙科类
    "Dentist", "Orthodontist", "Dental Hygienist", "Dental Surgeon",
    # 其他医疗
    "Pharmacist", "Physical Therapist", "Occupational Therapist", "Chiropractor",
    "Lab Technician", "Medical Technician", "Respiratory Therapist"
]

# 优先级 2：法律相关（有展示但需优化）
LEGAL_PROFESSIONS = [
    "Lawyer", "Attorney", "Legal Consultant", "Paralegal", "Defense Attorney", 
    "Corporate Lawyer", "Family Lawyer", "Immigration Lawyer", "Criminal Lawyer",
    "Estate Planning Lawyer"
]

# 优先级 3：教育相关（高排名待优化）
EDUCATION_PROFESSIONS = [
    "Teacher", "Professor", "Tutor", "Education Coordinator", "School Principal", 
    "Academic Advisor", "Educational Consultant"
]

# 优先级 4：金融/会计
FINANCE_PROFESSIONS = [
    "Accountant", "CPA", "Tax Auditor", "Financial Analyst", "Investment Banker", 
    "Bookkeeper", "Actuary", "Financial Planner"
]

# 优先级 5：房地产
REALESTATE_PROFESSIONS = [
    "Real Estate Agent", "Broker", "Property Manager", "Real Estate Consultant", 
    "Appraiser"
]

# 优先级 6：工程师
ENGINEERING_PROFESSIONS = [
    "Engineer", "Software Developer", "Architect", "Civil Engineer", 
    "Mechanical Engineer", "Data Scientist", "Electrical Engineer"
]

# 合并所有职业（医疗优先）
ALL_PROFESSIONS = (
    MEDICAL_PROFESSIONS +       # 30+ 职业
    LEGAL_PROFESSIONS +         # 10 职业
    EDUCATION_PROFESSIONS +     # 7 职业
    FINANCE_PROFESSIONS +       # 8 职业
    REALESTATE_PROFESSIONS +    # 5 职业
    ENGINEERING_PROFESSIONS     # 7 职业
)

# 级别前缀（10个）
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

# ⭐ 高优先级州（人口大州）
HIGH_PRIORITY_STATES = [
    "California", "Texas", "Florida", "New York", "Pennsylvania", 
    "Illinois", "Ohio", "Georgia", "North Carolina", "Michigan"
]

def generate_data():
    count = 0
    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['profession', 'slug', 'state', 'priority'])
        
        # 优先生成：高优先级州 × 医疗职业
        print("🏥 生成优先级数据：Medical × 高人口州...")
        for state in HIGH_PRIORITY_STATES:
            for prof_base in MEDICAL_PROFESSIONS:
                for sub in SUB_PROFESSIONS:
                    full_profession = sub.format(prof_base)
                    clean_state = state.lower().replace(' ', '-')
                    clean_prof = full_profession.lower().replace(' ', '-')
                    slug = f"{clean_state}-{clean_prof}-expert"
                    
                    writer.writerow([full_profession, slug, state, 'HIGH'])
                    count += 1
        
        print(f"   ✅ 优先级数据: {count} 行")
        
        # 生成全量数据：所有州 × 所有职业
        print("📊 生成全量数据：所有州 × 所有职业...")
        initial_count = count
        
        for state in STATES:
            for prof_base in ALL_PROFESSIONS:
                for sub in SUB_PROFESSIONS:
                    full_profession = sub.format(prof_base)
                    clean_state = state.lower().replace(' ', '-')
                    clean_prof = full_profession.lower().replace(' ', '-')
                    slug = f"{clean_state}-{clean_prof}-expert"
                    
                    # 标记优先级
                    priority = 'NORMAL'
                    if state in HIGH_PRIORITY_STATES and prof_base in MEDICAL_PROFESSIONS:
                        priority = 'HIGH'  # 已在上面生成过，这里会重复但无妨
                    elif prof_base in MEDICAL_PROFESSIONS:
                        priority = 'MEDIUM'
                    
                    writer.writerow([full_profession, slug, state, priority])
                    count += 1
        
        print(f"   ✅ 全量数据: {count - initial_count} 行")
                
    print("\n" + "=" * 60)
    print(f"✅ 成功！已生成 {count} 行数据到 {OUTPUT_FILE}")
    print("=" * 60)
    print(f"\n📊 数据结构:")
    print(f"  • 总职业类别: {len(ALL_PROFESSIONS)} 个")
    print(f"  • 医疗相关: {len(MEDICAL_PROFESSIONS)} 个 ⭐ 优先级最高")
    print(f"  • 法律相关: {len(LEGAL_PROFESSIONS)} 个")
    print(f"  • 教育相关: {len(EDUCATION_PROFESSIONS)} 个")
    print(f"  • 州覆盖数: {len(STATES)} 个")
    print(f"  • 级别前缀: {len(SUB_PROFESSIONS)} 个")
    print(f"\n🎯 预计生成页面数: {count} 个")
    print(f"💡 建议: 优先部署 HIGH priority 页面（Medical × 高人口州）")
    print(f"\n下一步: 运行 step2_site_builder.py 构建网站")

if __name__ == "__main__":
    generate_data()
