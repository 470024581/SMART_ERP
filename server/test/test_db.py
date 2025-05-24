#!/usr/bin/env python3
"""
测试数据库功能
"""

import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from db import (
    check_database_exists,
    fetch_all_products,
    fetch_sales_data_for_query,
    get_product_details,
    initialize_app_database
)

async def test_database_functions():
    """测试数据库各种功能"""
    print("Smart ERP Agent 数据库功能测试")
    print("=" * 50)
    
    # 测试数据库状态
    print("\n1. 检查数据库状态")
    db_exists = check_database_exists()
    print(f"   数据库状态: {'✅ 存在' if db_exists else '❌ 不存在'}")
    
    if not db_exists:
        print("   正在初始化数据库...")
        initialize_app_database()
    
    # 测试产品查询
    print("\n2. 测试产品查询")
    try:
        products = await fetch_all_products()
        print(f"   产品总数: {len(products)}")
        if products:
            print(f"   首个产品: {products[0]}")
            
            # 测试产品详情
            product_detail = await get_product_details(products[0]['product_id'])
            print(f"   产品详情: {product_detail}")
    except Exception as e:
        print(f"   ❌ 产品查询错误: {e}")
    
    # 测试销售查询
    print("\n3. 测试销售查询")
    test_queries = [
        "历史销售额多少？",
        "今日销售额",
        "本月销售额",
        "过去7天销售",
        "销售情况怎么样？"
    ]
    
    for query in test_queries:
        try:
            result = await fetch_sales_data_for_query(query)
            print(f"   '{query}': {len(result)} 条记录")
            if result:
                print(f"      数据样例: {result[0]}")
        except Exception as e:
            print(f"   ❌ '{query}': {e}")
    
    print("\n" + "=" * 50)
    print("数据库测试完成!")

if __name__ == "__main__":
    asyncio.run(test_database_functions()) 