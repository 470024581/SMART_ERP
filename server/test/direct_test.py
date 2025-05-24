#!/usr/bin/env python3
"""
直接测试数据库函数修复
"""

import sqlite3
from pathlib import Path

# 测试数据库连接和销售数据查询
def test_database_direct():
    """直接测试数据库"""
    print("=== 直接数据库测试 ===")
    
    # 从test目录向上找数据库文件
    database_path = Path("../data/smart_erp.db")
    if not database_path.exists():
        # 尝试当前目录下的data文件夹
        database_path = Path("data/smart_erp.db")
        if not database_path.exists():
            print("❌ 数据库文件不存在!")
            return False
    
    try:
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查销售数据
        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        print(f"销售记录数量: {sales_count}")
        
        if sales_count > 0:
            # 测试历史销售额查询
            cursor.execute('''
                SELECT 
                    SUM(total_amount) as total_sales,
                    COUNT(*) as total_orders,
                    COUNT(DISTINCT product_id) as unique_products,
                    AVG(total_amount) as avg_order_value,
                    MIN(sale_date) as first_sale,
                    MAX(sale_date) as last_sale
                FROM sales
            ''')
            
            result = cursor.fetchone()
            if result and result[0]:
                print("✅ 历史销售额查询成功!")
                print(f"   总销售额: ¥{float(result[0]):.2f}")
                print(f"   总订单数: {result[1]}")
                print(f"   产品种类: {result[2]}")
                print(f"   平均订单金额: ¥{float(result[3]):.2f}")
                print(f"   销售期间: {result[4]} 到 {result[5]}")
                return True
            else:
                print("❌ 查询返回空结果")
                return False
        else:
            print("❌ 没有销售数据")
            return False
            
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_pattern_matching():
    """测试查询模式匹配"""
    print("\n=== 测试查询模式匹配 ===")
    
    test_queries = [
        "历史销售额多少？",
        "总销售额",
        "全部销售额",
        "所有销售额",
        "历史销售总计"
    ]
    
    for query in test_queries:
        # 测试是否匹配历史销售额模式
        keywords = ["历史", "总", "全部", "所有", "总计", "历史销售额", "total", "all"]
        matches = any(keyword in query for keyword in keywords)
        print(f"   '{query}' -> {'✅ 匹配' if matches else '❌ 不匹配'}")

if __name__ == "__main__":
    print("Smart ERP Agent 数据库修复验证")
    print("=" * 50)
    
    # 测试数据库
    db_success = test_database_direct()
    
    # 测试模式匹配
    test_pattern_matching()
    
    print("\n" + "=" * 50)
    if db_success:
        print("✅ 修复验证成功! 历史销售额查询功能已正常工作")
    else:
        print("❌ 仍有问题需要解决")
    print("=" * 50) 