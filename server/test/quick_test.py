#!/usr/bin/env python3
"""
快速测试脚本 - Smart ERP Agent
"""

import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import fetch_sales_data_for_query
from agent import get_sales_query_response

async def quick_test():
    """快速测试销售查询功能"""
    print("Smart ERP Agent 快速测试")
    print("=" * 40)
    
    test_queries = [
        "历史销售额多少？",
        "今日销售额",
        "本月销售额"
    ]
    
    for query in test_queries:
        print(f"\n🔍 测试查询: {query}")
        print("-" * 30)
        
        try:
            # 测试数据库函数
            db_result = await fetch_sales_data_for_query(query)
            print(f"📊 数据库返回: {len(db_result)} 条记录")
            if db_result:
                print(f"   首条数据: {db_result[0]}")
            
            # 测试智能体响应
            response, chart_data = await get_sales_query_response(query)
            print(f"🤖 AI响应: {response[:100]}...")
            print(f"📈 图表数据: {'有' if chart_data else '无'}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
    
    print("\n" + "=" * 40)
    print("快速测试完成!")

if __name__ == "__main__":
    asyncio.run(quick_test()) 