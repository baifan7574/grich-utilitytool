"""
GSC Excel数据分析脚本 - 分析从Google Search Console导出的Coverage数据
"""
import os
import sys
import pandas as pd
import json
from collections import defaultdict
import re

# 设置输出编码为UTF-8，解决Windows控制台编码问题
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def extract_industry_from_url(url):
    """从URL中提取行业信息"""
    url_lower = url.lower()
    
    # 医疗行业
    if any(x in url_lower for x in ['doctor', 'nurse', 'medical', 'physician', 'surgeon', 'clinic', 'therapist', 'counselor', 'health']):
        return 'Medical'
    
    # 法律行业
    if any(x in url_lower for x in ['lawyer', 'attorney', 'paralegal', 'legal', 'judge', 'defense']):
        return 'Lawyer'
    
    # 教育行业
    if any(x in url_lower for x in ['tutor', 'teacher', 'education', 'instructor', 'professor', 'school']):
        return 'Tutor'
    
    # 金融行业
    if any(x in url_lower for x in ['accountant', 'cpa', 'tax', 'finance', 'audit', 'bookkeeper']):
        return 'Finance'
    
    # 房地产行业
    if any(x in url_lower for x in ['real estate', 'realtor', 'broker', 'agent']):
        return 'RealEstate'
    
    return 'Other'

def analyze_excel_file(file_path):
    """分析Excel文件"""
    print(f"📂 正在读取文件: {file_path}")
    
    try:
        # 尝试读取Excel文件
        df = pd.read_excel(file_path)
        
        print(f"\n✅ 文件读取成功")
        print(f"📊 数据行数: {len(df)}")
        print(f"📋 列名: {list(df.columns)}")
        
        # 显示前几行数据
        print(f"\n📄 前5行数据预览:")
        print(df.head().to_string())
        
        # 查找URL列
        url_column = None
        for col in df.columns:
            if 'url' in col.lower() or 'page' in col.lower():
                url_column = col
                break
        
        if url_column is None:
            print("\n❌ 未找到URL列")
            return None
        
        print(f"\n🔍 找到URL列: {url_column}")
        
        # 检查列的数据类型
        print(f"\n🔍 列数据类型:")
        print(df[url_column].dtype)
        print(f"📄 前10个值:")
        print(df[url_column].head(10).to_string())
        
        # 如果列包含数字而非URL，说明这是汇总数据而非URL列表
        if df[url_column].dtype in ['int64', 'float64']:
            print(f"\n⚠️  检测到数值列，这是Coverage汇总数据而非URL列表")
            print(f"📊 数据分析:")
            print(f"  - 总天数: {len(df)}")
            print(f"  - 平均每日受影响页面: {df[url_column].mean():.2f}")
            print(f"  - 最大受影响页面: {df[url_column].max()}")
            print(f"  - 最小受影响页面: {df[url_column].min()}")
            print(f"  - 总受影响页面: {df[url_column].sum()}")
            
            # 生成汇总报告
            report = {
                'data_type': 'coverage_summary',
                'total_days': len(df),
                'total_affected_pages': int(df[url_column].sum()),
                'avg_affected_pages': float(df[url_column].mean()),
                'max_affected_pages': int(df[url_column].max()),
                'min_affected_pages': int(df[url_column].min()),
                'date_range': {
                    'start': str(df['Date'].min()),
                    'end': str(df['Date'].max())
                },
                'daily_data': df.to_dict('records')
            }
            return report
        
        # 提取所有URL
        urls = df[url_column].dropna().unique()
        print(f"📈 唯一URL数量: {len(urls)}")
        
        # 分析行业分布
        industry_stats = defaultdict(lambda: {'count': 0, 'urls': []})
        
        for url in urls:
            url_str = str(url)  # 确保转换为字符串
            industry = extract_industry_from_url(url_str)
            industry_stats[industry]['count'] += 1
            if len(industry_stats[industry]['urls']) < 10:  # 只保留前10个URL作为示例
                industry_stats[industry]['urls'].append(url_str)
        
        # 生成报告
        report = {
            'total_urls': len(urls),
            'total_rows': len(df),
            'columns': list(df.columns),
            'industry_distribution': {},
            'all_urls': list(urls)
        }
        
        for industry, data in sorted(industry_stats.items(), key=lambda x: x[1]['count'], reverse=True):
            report['industry_distribution'][industry] = {
                'count': data['count'],
                'percentage': round((data['count'] / len(urls)) * 100, 2) if urls else 0,
                'sample_urls': data['urls']
            }
        
        return report
        
    except Exception as e:
        print(f"\n❌ 读取文件失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("=" * 80)
    print("🚀 GSC Excel数据分析工具")
    print("=" * 80)
    
    # 尝试多个可能的文件路径
    possible_paths = [
        "D:/360Downloadshttps___scenro.com_-Coverage-Drilldown-2026-02-17.xlsx",
        "D:\\360Downloads\\https___scenro.com_-Coverage-Drilldown-2026-02-17.xlsx",
        "gsc_coverage_data.xlsx",
        "Coverage-Drilldown-2026-02-17.xlsx"
    ]
    
    report = None
    for path in possible_paths:
        print(f"\n🔍 尝试路径: {path}")
        report = analyze_excel_file(path)
        if report:
            break
    
    if not report:
        print("\n❌ 所有路径均失败，请手动指定文件路径")
        return
    
    # 保存报告
    output_file = 'gsc_excel_analysis_report.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 报告已保存到: {output_file}")
    
    # 根据数据类型打印不同的报告
    if report.get('data_type') == 'coverage_summary':
        print("\n" + "=" * 80)
        print("📊 Coverage汇总数据报告")
        print("=" * 80)
        print(f"\n📅 数据时间范围:")
        print(f"  开始: {report['date_range']['start']}")
        print(f"  结束: {report['date_range']['end']}")
        print(f"\n📈 受影响页面统计:")
        print(f"  总天数: {report['total_days']}")
        print(f"  总受影响页面: {report['total_affected_pages']}")
        print(f"  平均每日: {report['avg_affected_pages']:.2f}")
        print(f"  最大值: {report['max_affected_pages']}")
        print(f"  最小值: {report['min_affected_pages']}")
        print("\n" + "=" * 80)
        print("⚠️  注意: 这是Coverage汇总数据，不包含具体URL列表")
        print("💡 建议: 请从GSC导出'Pages'或'URL Inspection'数据以获取具体URL清单")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("📊 行业分布报告")
        print("=" * 80)
        for industry, data in sorted(report['industry_distribution'].items(), key=lambda x: x[1]['count'], reverse=True):
            print(f"\n{industry}:")
            print(f"  数量: {data['count']}")
            print(f"  占比: {data['percentage']}%")
            print(f"  示例URL:")
            for url in data['sample_urls']:
                print(f"    - {url}")
        
        print("\n" + "=" * 80)
        print(f"📈 总计: {report['total_urls']} 个唯一URL")
        print(f"📋 总数据行: {report['total_rows']}")
        print("=" * 80)

if __name__ == "__main__":
    main()
