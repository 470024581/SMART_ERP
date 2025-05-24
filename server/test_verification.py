#!/usr/bin/env python3
"""
直接验证Smart ERP Agent修复
"""

import asyncio
import sqlite3
import sys
from pathlib import Path

# 添加当前目录到模块路径
sys.path.insert(0, str(Path(__file__).parent))

from db import fetch_sales_data_for_query, get_db_connection
from agent import get_sales_query_response

def check_database():
    """检查数据库状态"""
    print("=== 🔍 数据库状态检查 ===")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查销售数据
        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(total_amount) FROM sales")
        total_sales_result = cursor.fetchone()
        total_sales = total_sales_result[0] if total_sales_result[0] else 0
        
        print(f"✅ 数据库连接成功")
        print(f"📊 销售记录: {sales_count} 条")
        print(f"💰 总销售额: ¥{total_sales:.2f}")
        
        conn.close()
        return sales_count > 0
        
    except Exception as e:
        print(f"❌ 数据库错误: {e}")
        return False

async def test_historical_sales_query():
    """测试历史销售额查询修复"""
    print("\n=== 🎯 历史销售额查询测试 ===")
    
    query = "历史销售额多少？"
    print(f"📝 测试查询: '{query}'")
    
    try:
        # 测试数据库函数
        print("\n1️⃣ 测试数据库函数...")
        db_result = await fetch_sales_data_for_query(query)
        
        if db_result:
            print(f"✅ 数据库查询成功: {len(db_result)} 条记录")
            first_result = db_result[0]
            
            if "total_sales" in first_result:
                print(f"   总销售额: ¥{first_result['total_sales']:.2f}")
                print(f"   总订单数: {first_result.get('total_orders', 'N/A')}")
                print(f"   产品种类: {first_result.get('unique_products', 'N/A')}")
                print(f"   平均订单: ¥{first_result.get('avg_order_value', 0):.2f}")
            else:
                print(f"   返回数据: {first_result}")
        else:
            print("❌ 数据库查询返回空结果")
            return False
        
        # 测试智能体响应
        print("\n2️⃣ 测试智能体响应...")
        response, chart_data = await get_sales_query_response(query)
        
        print(f"🤖 AI响应: {response}")
        print(f"📈 图表数据: {'有' if chart_data else '无'}")
        
        if chart_data:
            print(f"   图表类型: {chart_data.get('type', 'N/A')}")
        
        # 检查是否修复成功
        success_indicators = [
            "总销售额" in response or "历史销售" in response,
            "无法找到" not in response,
            "无法访问" not in response,
            "很抱歉" not in response
        ]
        
        if all(success_indicators):
            print("✅ 修复验证成功! 历史销售额查询现在返回实际数据")
            return True
        else:
            print("❌ 修复未完全成功，响应仍包含错误信息")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

async def test_other_queries():
    """测试其他查询类型"""
    print("\n=== 📊 其他查询测试 ===")
    
    test_queries = [
        "今日销售额",
        "本月销售额", 
        "总销售额",
        "全部销售额",
        "销售情况怎么样？"
    ]
    
    success_count = 0
    
    for query in test_queries:
        print(f"\n📝 测试: '{query}'")
        try:
            db_result = await fetch_sales_data_for_query(query)
            if db_result and db_result[0].get("total_sales", 0) > 0:
                print(f"   ✅ 成功: ¥{db_result[0]['total_sales']:.2f}")
                success_count += 1
            else:
                print(f"   ⚠️  返回: {db_result}")
        except Exception as e:
            print(f"   ❌ 错误: {e}")
    
    print(f"\n📈 其他查询成功率: {success_count}/{len(test_queries)}")
    return success_count

async def main():
    """主验证函数"""
    print("🔧 Smart ERP Agent 修复验证")
    print("=" * 50)
    
    # 检查数据库
    db_ok = check_database()
    if not db_ok:
        print("\n❌ 数据库检查失败，无法继续验证")
        return
    
    # 测试历史销售额查询修复
    historical_ok = await test_historical_sales_query()
    
    # 测试其他查询
    other_success = await test_other_queries()
    
    # 总结
    print("\n" + "=" * 50)
    print("🎉 验证总结:")
    print(f"   数据库状态: {'✅ 正常' if db_ok else '❌ 异常'}")
    print(f"   历史销售额修复: {'✅ 成功' if historical_ok else '❌ 失败'}")
    print(f"   其他查询: {other_success} 个成功")
    
    if historical_ok:
        print("\n🎊 恭喜！历史销售额查询修复验证成功！")
        print("现在'历史销售额多少？'查询会返回实际的销售数据而不是错误信息。")
        print("\n🚀 下一步可以:")
        print("1. 启动服务器: python main.py 或 uvicorn main:app --reload --port 8001")
        print("2. 访问 http://localhost:8001 测试Web界面")
        print("3. 使用API: POST /query 测试各种查询")
    else:
        print("\n⚠️  修复验证未完全成功，可能需要进一步检查")

if __name__ == "__main__":
    asyncio.run(main()) 