#!/usr/bin/env python3
"""
简单功能测试
"""

import asyncio
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from db import fetch_sales_data_for_query

def test_server_connection():
    """测试服务器连接"""
    print("=== 服务器连接测试 ===")
    
    try:
        response = requests.get("http://localhost:8001/ping", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器连接正常")
            return True
        else:
            print(f"❌ 服务器响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接服务器: {e}")
        print("请确保运行: python test/start_server.py")
        return False

async def test_database_query():
    """测试数据库查询"""
    print("\n=== 数据库查询测试 ===")
    
    try:
        result = await fetch_sales_data_for_query("历史销售额多少？")
        if result:
            print(f"✅ 数据库查询成功，返回 {len(result)} 条记录")
            print(f"   数据样例: {result[0]}")
            return True
        else:
            print("❌ 数据库查询返回空结果")
            return False
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
        return False

def test_api_query():
    """测试API查询"""
    print("\n=== API查询测试 ===")
    
    try:
        response = requests.post(
            "http://localhost:8001/query",
            json={"query": "历史销售额多少？"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('response') and not result['response'].includes('无法找到'):
                print("✅ API查询成功")
                print(f"   AI响应: {result['response'][:100]}...")
                print(f"   图表数据: {'有' if result.get('chart_data') else '无'}")
                return True
            else:
                print("❌ API返回空响应或错误")
                print(f"   响应: {result.get('response', 'N/A')}")
                return False
        else:
            print(f"❌ API调用失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API调用异常: {e}")
        return False

async def main():
    """主测试函数"""
    print("Smart ERP Agent 简单功能测试")
    print("=" * 40)
    
    tests = [
        ("服务器连接", test_server_connection()),
        ("数据库查询", await test_database_query()),
        ("API查询", test_api_query())
    ]
    
    print("\n" + "=" * 40)
    print("测试结果总结:")
    
    passed = 0
    for name, result in tests:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体状态: {passed}/{len(tests)} 项测试通过")
    
    if passed == len(tests):
        print("🎉 所有测试通过!")
    else:
        print("⚠️  存在问题需要检查")

if __name__ == "__main__":
    asyncio.run(main()) 