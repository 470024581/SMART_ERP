#!/usr/bin/env python3
"""
简单API测试脚本
"""

import requests
import json

def test_query():
    """测试历史销售额查询"""
    print("正在测试历史销售额查询...")
    
    url = "http://localhost:8001/query"
    data = {"query": "历史销售额多少？"}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"HTTP状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功!")
            print(f"查询: {data['query']}")
            print(f"AI响应: {result['response']}")
            
            if result.get('chart_data'):
                print(f"图表类型: {result['chart_data']['type']}")
                print(f"图表标签: {result['chart_data']['labels']}")
            else:
                print("无图表数据")
            print("-" * 50)
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"错误内容: {response.text}")
    except Exception as e:
        print(f"❌ 连接错误: {e}")
        print("请确保服务器运行在 http://localhost:8001")
        print("运行命令: python test/start_server.py")

if __name__ == "__main__":
    test_query() 