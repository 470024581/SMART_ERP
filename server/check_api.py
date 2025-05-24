#!/usr/bin/env python3
"""
API连通性检查脚本
用于验证所有API端点是否正常工作
"""

import asyncio
import json
from typing import Dict, Any
import sys
from pathlib import Path

# 添加当前目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from app.main import app

class APIChecker:
    """API检查器"""
    
    def __init__(self):
        self.client = TestClient(app)
        self.test_results = []
    
    def test_endpoint(self, method: str, url: str, data: Dict[str, Any] = None, 
                     expected_status: int = 200, description: str = ""):
        """测试单个API端点"""
        try:
            if method.upper() == "GET":
                response = self.client.get(url)
            elif method.upper() == "POST":
                response = self.client.post(url, json=data)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            success = response.status_code == expected_status
            result = {
                "method": method.upper(),
                "url": url,
                "description": description,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "success": success,
                "response_size": len(response.text),
                "error": None if success else f"状态码错误: {response.status_code}"
            }
            
            if success and response.headers.get("content-type", "").startswith("application/json"):
                try:
                    response_json = response.json()
                    result["has_data"] = "data" in response_json or "success" in response_json
                    if "success" in response_json:
                        result["api_success"] = response_json["success"]
                except:
                    result["has_data"] = False
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            result = {
                "method": method.upper(),
                "url": url,
                "description": description,
                "status_code": None,
                "expected_status": expected_status,
                "success": False,
                "response_size": 0,
                "error": str(e)
            }
            self.test_results.append(result)
            return result
    
    def run_all_tests(self):
        """运行所有API测试"""
        print("🔍 开始API连通性检查...")
        print("=" * 60)
        
        # 基础健康检查
        self.test_endpoint("GET", "/ping", description="健康检查")
        self.test_endpoint("GET", "/", description="根路径")
        
        # 智能问答API
        self.test_endpoint("POST", "/api/v1/query", 
                          data={"query": "今日销售额"},
                          description="智能问答 - 销售查询")
        
        # 库存管理API  
        self.test_endpoint("GET", "/api/v1/inventory", description="获取库存列表")
        self.test_endpoint("GET", "/api/v1/inventory/alerts", description="获取库存预警")
        self.test_endpoint("GET", "/api/v1/inventory/alerts?threshold=30", description="自定义阈值库存预警")
        
        # 销售数据API
        self.test_endpoint("GET", "/api/v1/sales", description="获取销售数据")
        self.test_endpoint("GET", "/api/v1/sales?range=day", description="获取日销售数据")
        self.test_endpoint("GET", "/api/v1/sales?range=month", description="获取月销售数据")
        self.test_endpoint("GET", "/api/v1/sales/products", description="获取产品销量排行")
        
        # 报表API
        self.test_endpoint("POST", "/api/v1/reports/generate",
                          data={"type": "daily"},
                          description="生成日报表")
        self.test_endpoint("GET", "/api/v1/reports", description="获取报表列表")
        
        # 数据分析API
        self.test_endpoint("GET", "/api/v1/analytics/dashboard", description="获取仪表板数据")
        self.test_endpoint("GET", "/api/v1/analytics/trends", description="获取趋势分析")
        self.test_endpoint("GET", "/api/v1/analytics/trends?metric=sales&timeRange=week", 
                          description="自定义趋势分析")
        
        # 认证API
        self.test_endpoint("POST", "/api/v1/auth/login",
                          data={"username": "admin", "password": "admin123"},
                          description="用户登录")
        self.test_endpoint("POST", "/api/v1/auth/logout", description="用户登出")
        
        # 显示结果
        self.display_results()
    
    def display_results(self):
        """显示测试结果"""
        print("\n📊 测试结果汇总")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        
        for result in self.test_results:
            status_icon = "✅" if result["success"] else "❌"
            status_info = f"{result['status_code']}" if result['status_code'] else "ERROR"
            
            print(f"{status_icon} {result['method']:4} {result['url']:35} | {status_info:3} | {result['description']}")
            
            if not result["success"] and result["error"]:
                print(f"    💥 错误: {result['error']}")
            elif result.get("has_data"):
                data_info = "✓ 有数据" if result.get("api_success", True) else "⚠ API返回失败"
                print(f"    📦 {data_info}")
        
        print("\n" + "=" * 60)
        print(f"📈 总计: {total_tests} 个测试")
        print(f"✅ 成功: {successful_tests} 个")
        print(f"❌ 失败: {total_tests - successful_tests} 个")
        print(f"📊 成功率: {(successful_tests/total_tests)*100:.1f}%")
        
        if successful_tests == total_tests:
            print("\n🎉 所有API端点测试通过！")
        else:
            print(f"\n⚠️  有 {total_tests - successful_tests} 个API端点需要检查")
        
        return successful_tests == total_tests

def main():
    """主函数"""
    print("🚀 SmartERP API 连通性检查工具")
    print("=" * 60)
    
    checker = APIChecker()
    
    try:
        success = checker.run_all_tests()
        
        print("\n💡 建议:")
        if success:
            print("- 所有API正常，可以启动前端应用进行测试")
            print("- 确保前端配置的API地址正确")
        else:
            print("- 检查失败的API端点对应的代码逻辑")
            print("- 确认数据库数据是否正确加载")
            print("- 查看详细错误信息进行调试")
        
        print("\n🔗 有用链接:")
        print("- API文档: http://localhost:8000/docs")
        print("- 数据库检查: python scripts/check_database.py")
        print("- 启动服务: python start.py")
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n❌ 检查过程中发生错误: {e}")
        return 1

if __name__ == "__main__":
    import os
    # 确保在正确的目录运行
    os.chdir(Path(__file__).resolve().parent)
    exit_code = main()
    sys.exit(exit_code) 