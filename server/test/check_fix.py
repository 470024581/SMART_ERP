#!/usr/bin/env python3
"""
快速检查Smart ERP Agent修复状态
"""

import os
import sqlite3
from pathlib import Path

def check_database():
    """检查数据库状态"""
    print("=== 数据库检查 ===")
    
    # 从test目录向上找数据库文件
    db_path = Path("../data/smart_erp.db")
    if not db_path.exists():
        # 尝试当前目录下的data文件夹
        db_path = Path("data/smart_erp.db")
        if not db_path.exists():
            print("❌ 数据库文件不存在")
            return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查销售数据
        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(total_amount) FROM sales")
        total_sales = cursor.fetchone()[0]
        
        print(f"✅ 数据库连接正常")
        print(f"   销售记录: {sales_count} 条")
        print(f"   总销售额: ¥{total_sales:.2f}" if total_sales else "   总销售额: ¥0.00")
        
        conn.close()
        return sales_count > 0
        
    except Exception as e:
        print(f"❌ 数据库错误: {e}")
        return False

def check_files():
    """检查关键文件"""
    print("\n=== 文件检查 ===")
    
    required_files = [
        "../main.py",
        "../agent.py", 
        "../db.py",
        "../models.py",
        "../report.py",
        "../config.py"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file.replace('../', '')}")
        else:
            print(f"❌ {file.replace('../', '')} 缺失")
            all_exist = False
    
    return all_exist

def check_config():
    """检查配置"""
    print("\n=== 配置检查 ===")
    
    try:
        # 添加父目录到path
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        import config
        api_key = getattr(config, 'OPENAI_API_KEY', '')
        base_url = getattr(config, 'OPENAI_BASE_URL', '')
        model = getattr(config, 'OPENAI_MODEL', '')
        
        print(f"✅ 配置文件加载成功")
        print(f"   API Key: {'已设置' if api_key else '未设置'}")
        print(f"   Base URL: {base_url or '默认'}")
        print(f"   模型: {model or '默认'}")
        
        return True
    except Exception as e:
        print(f"❌ 配置错误: {e}")
        return False

def test_pattern_matching():
    """测试查询模式匹配"""
    print("\n=== 查询模式测试 ===")
    
    test_cases = [
        ("历史销售额多少？", ["历史", "总", "全部", "所有", "总计", "历史销售额", "total", "all"]),
        ("今日销售额", ["今日", "今天", "today"]),
        ("本月销售额", ["本月销售额", "this month"]),
        ("销售情况", ["销售情况", "销售状况", "销售如何", "销售怎么样"])
    ]
    
    for query, keywords in test_cases:
        matches = any(keyword in query for keyword in keywords)
        print(f"   '{query}' -> {'✅ 匹配' if matches else '❌ 不匹配'}")
    
    return True

def main():
    """主检查函数"""
    print("Smart ERP Agent 修复状态检查")
    print("=" * 50)
    
    checks = [
        ("数据库", check_database()),
        ("文件", check_files()),
        ("配置", check_config()),
        ("模式匹配", test_pattern_matching())
    ]
    
    print("\n" + "=" * 50)
    print("检查总结:")
    
    passed = 0
    for name, result in checks:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体状态: {passed}/{len(checks)} 项检查通过")
    
    if passed == len(checks):
        print("🎉 所有检查通过! 修复应该已经生效")
        print("\n下一步:")
        print("1. 运行: python ../start_server.py")
        print("2. 访问: http://localhost:8001")
        print("3. 测试: '历史销售额多少？'")
        print("4. 或打开: test_fix_page.html")
    else:
        print("⚠️  存在问题，需要进一步修复")

if __name__ == "__main__":
    main() 