from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict

# Import Pydantic models from .models
from .models import (
    QueryRequest,
    SalesQueryResponse,
    InventoryQueryRequest,
    InventoryResponse,
    SalesReportResponse,
    QueryResponse,  # Legacy
    ReportResponse  # Legacy
)

# Import initialization function (assuming it's in .agent)
from .agent import initialize_app_state

# Import agent functions (assuming they are in .agent)
from .agent import (
    get_answer_from_erp,
    get_daily_sales_report_response_from_agent,
    get_sales_query_response, # Legacy
    get_inventory_check_response, # Legacy
)

from . import routes # Import the routes module

app = FastAPI(title="SmartERP AI Assistant API", version="0.3.0")

# CORS Middleware Configuration
origins = [
    "http://localhost:3000",  # Allow your React frontend origin
    # You can add other origins here if needed, e.g., your deployed frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, OPTIONS, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include the router from routes.py
app.include_router(routes.router) # This line registers all routes from routes.py

@app.on_event("startup")
async def startup_event():
    """Initialize application state (e.g., DB schema, API keys) on startup."""
    print("Application starting up...")
    initialize_app_state()
    print("Application startup completed.")

@app.get("/ping", tags=["Health Check"])
async def ping():
    """
    A simple ping endpoint to check if the API is running.
    """
    return {"status": "ok", "message": "pong!", "version": "0.2.0"}

# New API endpoints - per user requirements

@app.post("/api/v1/sales_query", response_model=SalesQueryResponse, tags=["Sales Queries"])
async def sales_query_new(request: QueryRequest):
    """
    Natural language sales Q&A API (Features 1 & 3)
    
    Processes natural language sales queries, supports chart data generation.
    - **query**: Natural language question (e.g., "What are the daily sales for the past 7 days?")
    
    Returns an answer and JSON formatted data suitable for frontend chart libraries like Chart.js.
    """
    try:
        result = await get_answer_from_erp(request.query, "sales")
        return SalesQueryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing sales query: {str(e)}")

@app.post("/api/v1/inventory_check", response_model=InventoryResponse, tags=["Inventory"])
async def inventory_check_new(request: InventoryQueryRequest):
    """
    Intelligent inventory check API (Feature 2)
    
    Supports natural language inventory queries and conditional filtering.
    - **query**: Natural language inventory question (e.g., "Which products have stock below 50?")
    - **threshold**: Stock threshold (optional, default 50)
    
    Returns a list of low-stock products and related suggestions.
    """
    try:
        query_with_threshold = request.query
        if request.threshold != 50:
            query_with_threshold = f"Which products have stock below {request.threshold}?" # Example of how to rephrase in English if needed
        
        result = await get_answer_from_erp(query_with_threshold, "inventory")
        return InventoryResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing inventory query: {str(e)}")

@app.get("/api/v1/reports/sales_daily", response_model=SalesReportResponse, tags=["Reports"])
async def sales_daily_report():
    """
    Automated report generation API (Feature 4)
    
    Generates daily sales reports using LLM combined with database data to produce formatted text summaries and sales data overviews.
    Includes:
    - Intelligently generated sales summary
    - Detailed sales data
    - Data format suitable for chart display
    """
    try:
        summary, report_data, chart_data = await get_daily_sales_report_response_from_agent()
        from datetime import datetime
        report_date_str = report_data.get("report_date", datetime.utcnow().strftime("%Y-%m-%d"))
        
        return SalesReportResponse(
            summary=summary,
            report_date=report_date_str, 
            data=report_data,
            chart_data=chart_data,
            success=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating sales report: {str(e)}")

# Legacy API endpoints (backward compatibility)

@app.post("/api/v1/sales/query", response_model=QueryResponse, tags=["Sales & Queries (Legacy)"])
async def sales_query_legacy(request: QueryRequest):
    """
    Processes natural language sales queries (backward compatible version).
    - **query**: Natural language question (e.g., "What are this month's sales?", "What are the daily sales for the past 7 days?")
    """
    answer, chart_data = await get_sales_query_response(request.query)
    return QueryResponse(answer=answer, data_for_chart=chart_data)

@app.get("/api/v1/inventory/check", response_model=Dict, tags=["Inventory (Legacy)"])
async def inventory_check_legacy():
    """
    Checks for low-stock products (backward compatible version).
    Identifies products with low stock and provides AI-generated restocking suggestions.
    """
    low_stock_items, suggestions = await get_inventory_check_response()
    return {
        "low_stock_items": low_stock_items,
        "suggestions": suggestions
    }

@app.get("/api/v1/reports/daily_sales", response_model=ReportResponse, tags=["Reports (Legacy)"])
async def daily_sales_report_legacy():
    """
    Generates daily sales report (backward compatible version).
    Response includes text summary and structured data, suitable for chart display.
    """
    summary, report_data, chart_data = await get_daily_sales_report_response_from_agent()
    return ReportResponse(summary=summary, report_data=report_data, data_for_chart=chart_data)

# API documentation enhancement endpoint

@app.get("/api/v1/info", tags=["System Info"])
async def api_info():
    """
    Get API system information and feature overview.
    """
    return {
        "name": "SmartERP AI Assistant API",
        "version": "0.2.0",
        "features": {
            "1": "Natural Language Sales Q&A (supports chart data generation)",
            "2": "Intelligent Inventory Check (supports natural language queries)",
            "3": "Automated Report Generation (AI-driven sales analysis)",
            "4": "SQLite Database Backend (CSV auto-import)"
        },
        "new_endpoints": [
            "POST /api/v1/sales_query",
            "POST /api/v1/inventory_check", 
            "GET /api/v1/reports/sales_daily"
        ],
        "legacy_endpoints": [
            "POST /api/v1/sales/query",
            "GET /api/v1/inventory/check",
            "GET /api/v1/reports/daily_sales"
        ],
        "database": "SQLite with automatic CSV import",
        "ai_powered": True,
        "chart_support": "Chart.js compatible data format"
    }

# Example of how to run directly (though uvicorn command is more common for production)
if __name__ == "__main__":
    import uvicorn
    print("Starting FastAPI server directly. For production, use: uvicorn main:app --reload")
    uvicorn.run(app, host="0.0.0.0", port=8000) 