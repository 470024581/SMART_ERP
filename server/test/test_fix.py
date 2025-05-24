#!/usr/bin/env python3
"""
测试销售报告修复
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import fetch_sales_data_for_query
from agent import get_sales_query_response

async def test_db_function():
    """测试数据库函数"""
    print("=== 测试数据库函数 ===")
    
    queries = [
        "历史销售额多少？",
        "今日销售额",
        "本月销售额",
        "销售情况如何？"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        try:
            result = await fetch_sales_data_for_query(query)
            print(f"数据库返回: {result}")
        except Exception as e:
            print(f"错误: {e}")

async def test_agent_function():
    """测试智能体函数"""
    print("\n=== 测试智能体函数 ===")
    
    query = "历史销售额多少？"
    print(f"\n查询: {query}")
    try:
        response, chart_data = await get_sales_query_response(query)
        print(f"AI响应: {response}")
        if chart_data:
            print(f"图表数据: {chart_data}")
        else:
            print("无图表数据")
    except Exception as e:
        print(f"错误: {e}")

async def main():
    """主测试函数"""
    print("Smart ERP Agent 修复验证测试")
    print("=" * 50)
    
    await test_db_function()
    await test_agent_function()
    
    print("\n" + "=" * 50)
    print("测试完成!")

if __name__ == "__main__":
    asyncio.run(main()) 