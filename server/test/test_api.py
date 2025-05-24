#!/usr/bin/env python3
"""
API测试脚本 - Smart ERP Agent

测试所有API端点的功能
"""

import requests
import json
import time
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8001"

def test_endpoint(method: str, endpoint: str, data: Dict[str, Any] = None, 
                 description: str = "") -> Dict[str, Any]:
    """测试单个API端点"""
    url = f"{BASE_URL}{endpoint}"
    
    print(f"\n{'='*60}")
    print(f"测试: {description}")
    print(f"请求: {method} {endpoint}")
    if data:
        print(f"数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    print(f"{'='*60}")
    
    try:
        if method.upper() == "GET":
            response = requests.get(url)
        elif method.upper() == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"❌ 不支持的HTTP方法: {method}")
            return {"error": f"不支持的HTTP方法: {method}"}
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功")
            print(f"响应预览: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}...")
            return result
        else:
            print(f"❌ 失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return {"error": response.text, "status_code": response.status_code}
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 请确保API服务器正在运行 (python test/start_server.py)")
        return {"error": "连接失败"}
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return {"error": str(e)}

def test_query(query):
    """测试查询功能"""
    url = f"{BASE_URL}/query"
    data = {"query": query}
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"查询: {query}")
            print(f"响应: {result['response']}")
            if result.get('chart_data'):
                print(f"图表数据: {result['chart_data']['type']}")
            print("-" * 50)
        else:
            print(f"错误: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"连接错误: {e}")

def main():
    """主测试函数"""
    print("Smart ERP Agent API 测试套件")
    print("="*60)
    
    # 测试健康检查
    test_endpoint("GET", "/ping", description="健康检查")
    
    # 测试系统信息
    test_endpoint("GET", "/api/v1/info", description="系统信息")
    
    # 测试销售查询API
    sales_queries = [
        {"query": "本月销售额多少？"},
        {"query": "过去7天每天的销售额是多少？"},
        {"query": "今日销售情况如何？"},
        {"query": "历史销售额多少？"}  # 重点测试修复的查询
    ]
    
    for query_data in sales_queries:
        test_endpoint("POST", "/query", query_data, 
                     f"销售查询API - {query_data['query']}")
        time.sleep(1)  # 避免请求过快
    
    print(f"\n{'='*60}")
    print("快速查询测试")
    print(f"{'='*60}")
    
    # 测试多种查询
    queries = [
        "历史销售额多少？",
        "今日销售额", 
        "本月销售额",
        "过去7天销售",
        "销售情况怎么样？",
        "总销售额",
        "全部销售额"
    ]
    
    for query in queries:
        test_query(query)

    print(f"\n{'='*60}")
    print("API测试完成!")
    print("请检查上述输出以确认所有功能正常工作")
    print(f"{'='*60}")

if __name__ == "__main__":
    main() 