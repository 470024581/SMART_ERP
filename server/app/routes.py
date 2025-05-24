from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form, BackgroundTasks
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import uuid
import aiofiles
from pathlib import Path
from .models import (
    QueryRequest, QueryResponse, 
    SalesQueryResponse, InventoryResponse, InventoryQueryRequest,
    SalesReportResponse, BaseResponse,
    DataSourceCreate, DataSourceUpdate, DataSource, DataSourceResponse, DataSourceListResponse,
    FileInfo, FileListResponse, ProcessingStatus, FileType, DataSourceType
)
from .agent import (
    get_answer_from_erp, 
    initialize_app_state
)
from .db import (
    fetch_all_products,
    fetch_low_stock_products,
    fetch_sales_data_for_query,
    get_db_connection,
    # Data source management functions
    get_datasources, get_datasource, create_datasource, update_datasource,
    delete_datasource, set_active_datasource, get_active_datasource,
    # File management functions
    save_file_info, get_files_by_datasource, update_file_processing_status,
    delete_file_record_and_associated_data
)
from .utils import (
    format_currency, format_percentage, calculate_growth_rate,
    get_status_by_stock_level, get_alert_level_by_stock,
    format_chart_data_for_frontend, create_line_chart_dataset,
    create_bar_chart_dataset, create_doughnut_chart_dataset,
    get_time_range_dates, create_api_response, format_sql_date,
    safe_divide, calculate_percentage_distribution, get_suggested_order_quantity,
    generate_report_id, parse_query_intent
)
from .file_processor import process_uploaded_file
import json
import sqlite3
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/v1", tags=["Smart ERP API"])

# File upload directory configuration
UPLOAD_DIR = Path(__file__).resolve().parent.parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

SAMPLE_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_sales"
# Ensure sample data directory exists (though generator script also does this)
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

# ==================== Sample Data API ======================

@router.get("/sample-data-files", summary="List Sample Sales Data CSV Files")
async def list_sample_data_files():
    """Lists available sample sales data CSV files."""
    try:
        files = []
        if SAMPLE_DATA_DIR.exists() and SAMPLE_DATA_DIR.is_dir():
            for item in os.listdir(SAMPLE_DATA_DIR):
                if item.startswith("sample_sales_") and item.endswith(".csv"):
                    files.append({
                        "filename": item,
                        "year": item.replace("sample_sales_", "").replace(".csv", "")
                    })
        # Sort by year if possible
        files.sort(key=lambda x: x.get("year", ""))
        return {"success": True, "data": files}
    except Exception as e:
        return {"success": False, "error": f"Failed to list sample data files: {str(e)}", "data": []}

@router.get("/sample-data-files/{filename}", summary="Download Sample Sales Data CSV File")
async def download_sample_data_file(filename: str):
    """Downloads a specific sample sales data CSV file."""
    try:
        if not (filename.startswith("sample_sales_") and filename.endswith(".csv") and ".." not in filename):
            raise HTTPException(status_code=400, detail="Invalid filename requested.")
            
        file_path = SAMPLE_DATA_DIR / filename
        if not file_path.is_file():
            raise HTTPException(status_code=404, detail="Sample data file not found.")
        
        return FileResponse(file_path, media_type='text/csv', filename=filename)
    except HTTPException:
        raise
    except Exception as e:
        # Log the error for server-side diagnosis
        # logger.error(f"Error downloading sample file {filename}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Could not download file: {str(e)}")

# ==================== Data Source Management API ====================

@router.get("/datasources", response_model=DataSourceListResponse, summary="Get Data Source List")
async def get_datasources_list():
    """Get a list of all data sources"""
    try:
        datasources = await get_datasources()
        return DataSourceListResponse(
            success=True,
            data=datasources,
            message=f"Retrieved {len(datasources)} data sources"
        )
    except Exception as e:
        return DataSourceListResponse(
            success=False,
            error=f"Failed to retrieve data source list: {str(e)}",
            data=[]
        )

@router.post("/datasources", response_model=DataSourceResponse, summary="Create Data Source")
async def create_datasource_api(request: DataSourceCreate):
    """Create a new data source"""
    try:
        datasource = await create_datasource(
            name=request.name,
            description=request.description,
            ds_type=request.type.value
        )
        
        if datasource:
            return DataSourceResponse(
                success=True,
                data=DataSource(**datasource),
                message=f"Data source '{request.name}' created successfully"
            )
        else:
            # This case (returning None from create_datasource) implies name already exists or other creation failure handled in db.py
            # db.py create_datasource now raises an exception for UNIQUE constraint, so this path might not be hit for name conflict.
            # However, keeping a generic error for other potential None returns.
            return DataSourceResponse(
                success=False,
                error="Failed to create data source. Name might already exist or another issue occurred."
            )
    except sqlite3.IntegrityError as ie: # Specific handling for unique name constraint
         if "UNIQUE constraint failed: datasources.name" in str(ie):
            return DataSourceResponse(success=False, error=f"Data source name '{request.name}' already exists.")
         return DataSourceResponse(success=False, error=f"Database integrity error: {str(ie)}")
    except Exception as e:
        return DataSourceResponse(
            success=False,
            error=f"Failed to create data source: {str(e)}"
        )

@router.get("/datasources/active", response_model=DataSourceResponse, summary="Get Active Data Source")
async def get_active_datasource_api():
    """Get the currently active data source"""
    try:
        datasource_dict = await get_active_datasource()
        if datasource_dict:
            print("[DEBUG] Raw datasource_dict from DB from get_active_datasource():")
            for key, value in datasource_dict.items():
                print(f"[DEBUG]   {key}: {value} (Type: {type(value)})")

            try:
                if 'type' not in datasource_dict or datasource_dict['type'] is None:
                    error_msg = f"Data source type is missing or null in database for active data source ID {datasource_dict.get('id')}."
                    print(f"[API Error] {error_msg}")
                    raise HTTPException(status_code=500, detail=f"Invalid data source configuration: {error_msg}")
                
                # Ensure 'created_at' and 'updated_at' are valid datetime strings or already datetime objects
                # Pydantic v2 is generally good at parsing ISO 8601 strings.
                # If they are stored as Unix timestamps (integers/floats), explicit conversion might be needed.
                # For now, let's assume they are strings or Pydantic can handle them.
                # The debug prints above will reveal their actual types from the DB.

                datasource_dict['type'] = DataSourceType(datasource_dict['type'])
            except ValueError as ve: # Handles issues with DataSourceType conversion
                error_msg = f"Invalid data source type value '{datasource_dict.get('type')}' found in database for active data source ID {datasource_dict.get('id')}. Expected one of {list(DataSourceType.__members__.keys())}. Error: {ve}"
                print(f"[API Error] {error_msg}")
                raise HTTPException(status_code=500, detail=f"Invalid data source configuration: {error_msg}")
            except Exception as data_prep_error: # Catch any other errors during data preparation for the model
                error_msg = f"Error preparing data for DataSource model for ID {datasource_dict.get('id')}: {str(data_prep_error)}"
                print(f"[API Error] {error_msg}")
                import traceback
                traceback.print_exc()
                raise HTTPException(status_code=500, detail=f"Internal server error during data preparation: {error_msg}")

            try:
                print(f"[DEBUG] datasource_dict before Pydantic validation: {datasource_dict}")
                datasource_model = DataSource(**datasource_dict)
                print("[DEBUG] Successfully created DataSource model.")
            except Exception as pydantic_error: # Catch Pydantic validation errors specifically
                error_msg = f"Pydantic validation error for DataSource ID {datasource_dict.get('id')}: {str(pydantic_error)}"
                print(f"[API Error] {error_msg}")
                import traceback
                traceback.print_exc() # Print full traceback for Pydantic error
                # It's possible the 422 is generated by FastAPI before this if the structure is very off,
                # but if it's a validation error within Pydantic, this should catch it.
                raise HTTPException(status_code=422, detail=f"Data validation failed for active data source: {error_msg}")


            return DataSourceResponse(
                success=True,
                data=datasource_model,
                message="Active data source retrieved successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="No active data source found or set.")
            
    except HTTPException: 
        raise
    except Exception as e:
        error_id = uuid.uuid4()
        print(f"[API Error - ID: {error_id}] Unexpected error in get_active_datasource_api: {str(e)}")
        import traceback
        traceback.print_exc()
        return DataSourceResponse(
            success=False,
            error=f"Failed to retrieve active data source. An internal server error occurred. Error ID: {error_id}",
            data=None
        )

@router.get("/datasources/{datasource_id}", response_model=DataSourceResponse, summary="Get Specific Data Source")
async def get_datasource_detail(datasource_id: int):
    """Get detailed information for a specific data source"""
    try:
        datasource = await get_datasource(datasource_id)
        if datasource:
            return DataSourceResponse(
                success=True,
                data=DataSource(**datasource),
                message="Data source retrieved successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Data source not found")
    except HTTPException:
        raise
    except Exception as e:
        return DataSourceResponse(
            success=False,
            error=f"Failed to retrieve data source: {str(e)}"
        )

@router.put("/datasources/{datasource_id}", response_model=DataSourceResponse, summary="Update Data Source")
async def update_datasource_api(datasource_id: int, request: DataSourceUpdate):
    """Update data source information"""
    try:
        datasource = await update_datasource(
            datasource_id=datasource_id,
            name=request.name,
            description=request.description
        )
        if datasource:
            return DataSourceResponse(
                success=True,
                data=DataSource(**datasource),
                message="Data source updated successfully"
            )
        else:
            # This implies either not found or name conflict during update
            raise HTTPException(status_code=404, detail="Data source not found or name already in use by another data source.")
    except sqlite3.IntegrityError as ie:
         if "UNIQUE constraint failed: datasources.name" in str(ie):
            return DataSourceResponse(success=False, error=f"Data source name '{request.name}' is already in use.")
         return DataSourceResponse(success=False, error=f"Database integrity error during update: {str(ie)}")
    except HTTPException:
        raise
    except Exception as e:
        return DataSourceResponse(
            success=False,
            error=f"Failed to update data source: {str(e)}"
        )

@router.delete("/datasources/{datasource_id}", response_model=BaseResponse, summary="Delete Data Source")
async def delete_datasource_api(datasource_id: int):
    """Delete a specific data source"""
    try:
        if datasource_id == 1: # Default ERP data source ID
            raise HTTPException(status_code=400, detail="Default ERP data source cannot be deleted.")
        
        success = await delete_datasource(datasource_id)
        if success:
            return BaseResponse(
                success=True,
                message="Data source deleted successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Data source not found")
    except HTTPException:
        raise
    except Exception as e:
        return BaseResponse(
            success=False,
            error=f"Failed to delete data source: {str(e)}"
        )

@router.post("/datasources/{datasource_id}/activate", response_model=BaseResponse, summary="Activate Data Source")
async def activate_datasource(datasource_id: int):
    """Set the specified data source as the currently active one"""
    try:
        success = await set_active_datasource(datasource_id)
        if success:
            return BaseResponse(
                success=True,
                message="Data source activated successfully"
            )
        else:
            raise HTTPException(status_code=404, detail="Data source not found")
    except HTTPException:
        raise
    except Exception as e:
        return BaseResponse(
            success=False,
            error=f"Failed to activate data source: {str(e)}"
        )

@router.put("/datasources/{datasource_id}/deactivate", response_model=BaseResponse, summary="Deactivate Data Source (sets Default as Active)")
async def deactivate_datasource_api(datasource_id: int):
    """Deactivate a specific data source and set the default ERP data source as active"""
    try:
        if datasource_id == 1: # Default ERP data source ID
            raise HTTPException(status_code=400, detail="Default ERP data source cannot be deactivated.")
        
        success = await set_active_datasource(1) # Set default ERP data source as active
        if success:
            return BaseResponse(
                success=True,
                message="Data source deactivated successfully and default ERP data source activated"
            )
        else:
            raise HTTPException(status_code=404, detail="Data source not found")
    except HTTPException:
        raise
    except Exception as e:
        return BaseResponse(
            success=False,
            error=f"Failed to deactivate data source: {str(e)}"
        )

# ==================== File Management API ====================

@router.post("/datasources/{datasource_id}/files/upload", summary="Upload File to Data Source")
async def upload_file(
    datasource_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None # Keep BackgroundTasks for consistency
):
    """Upload a file to the specified data source"""
    try:
        target_datasource = await get_datasource(datasource_id)
        if not target_datasource:
            raise HTTPException(status_code=404, detail="Data source not found")
        
        file_extension = Path(file.filename).suffix.lower()
        
        # Determine allowed extensions based on datasource type
        allowed_extensions = set()
        if target_datasource.get('type') == DataSourceType.SQL_TABLE_FROM_FILE.value:
            allowed_extensions = {'.csv', '.xlsx'}
        else:
            # For KNOWLEDGE_BASE and other types (including DEFAULT, though it doesn't typically have uploads here)
            allowed_extensions = {'.pdf', '.txt', '.docx', '.csv', '.xlsx'}

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type for this data source. Supported types: {', '.join(allowed_extensions)}"
            )
        
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        file_size = len(content)
        # Ensure file_type is just the extension without the dot, matching FileType enum values
        file_type_value = file_extension[1:] 
        if file_type_value not in FileType.__members__.values():
             raise HTTPException(status_code=400, detail=f"Invalid file type for processing: {file_type_value}")

        file_id = await save_file_info(
            filename=unique_filename,
            original_filename=file.filename,
            file_type=file_type_value,
            file_size=file_size,
            datasource_id=datasource_id
        )
        
        if file_id:
            # Add file processing to background tasks
            background_tasks.add_task(
                process_uploaded_file, 
                file_id,                   # 1. file_id
                target_datasource['id'],   # 2. datasource_id (Corrected order)
                file_path,                 # 3. file_path (Corrected order)
                file.filename,             # 4. original_filename
                file_type_value            # 5. file_type
            )
            return {"success": True, "message": "File uploaded successfully and processing started.", "file_id": file_id, "filename": unique_filename}
        else:
            # Cleanup uploaded file if DB entry failed
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail="Failed to save file information to database.")

    except HTTPException:
        raise
    except Exception as e:
        # General error, attempt cleanup if file_path was defined
        if 'file_path' in locals() and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e_remove:
                # Log this failure, but the primary error is more important to report
                print(f"Failed to remove partially uploaded file {file_path}: {e_remove}")
        return {"success": False, "error": f"File upload failed: {str(e)}"}

@router.get("/datasources/{datasource_id}/files", response_model=FileListResponse, summary="Get Data Source File List")
async def get_datasource_files(datasource_id: int):
    """Get all files for a specific data source"""
    try:
        datasource = await get_datasource(datasource_id)
        if not datasource:
            raise HTTPException(status_code=404, detail="Data source not found")
        
        files = await get_files_by_datasource(datasource_id)
        file_list = [FileInfo(**file_data) for file_data in files]
        
        return FileListResponse(
            success=True,
            data=file_list,
            message=f"Retrieved {len(file_list)} files"
        )
    except HTTPException:
        raise
    except Exception as e:
        return FileListResponse(
            success=False,
            error=f"Failed to retrieve file list: {str(e)}",
            data=[]
        )

@router.delete("/datasources/{datasource_id}/files/{file_id}", response_model=BaseResponse, summary="Delete File from Data Source")
async def delete_file_from_datasource(datasource_id: int, file_id: int):
    """Delete a specific file and its associated data from a data source."""
    try:
        success = await delete_file_record_and_associated_data(file_id)
        if success:
            return BaseResponse(success=True, message=f"File ID {file_id} and its associated data deleted successfully.")
        else:
            raise HTTPException(status_code=404, detail=f"Failed to delete File ID {file_id}. File may not exist or operation was not completed.")
    except HTTPException:
        raise
    except Exception as e:
        return BaseResponse(success=False, error=f"An internal server error occurred while deleting File ID {file_id}: {str(e)}")

# ==================== Intelligent Q&A API ====================

@router.post("/query", response_model=Dict[str, Any], summary="Intelligent Q&A")
async def query_endpoint(request: QueryRequest):
    """
    Generic intelligent Q&A interface - query ERP data using natural language.
    
    Supported query types:
    - Sales data queries
    - Inventory status queries
    - Financial data queries (future)
    - Trend analysis, etc. (future)
    """
    try:
        intent = parse_query_intent(request.query)
        active_datasource_dict = await get_active_datasource()
        ds_id_for_response = active_datasource_dict['id'] if active_datasource_dict else 1 # Default to 1 if no active DS
        
        query_type_for_agent = intent['type']
        # Default routing logic based on intent and datasource type
        if active_datasource_dict and active_datasource_dict['type'] != DataSourceType.DEFAULT.value:
            # If custom data source is active, prioritize RAG or SQL Agent based on its type
            if active_datasource_dict['type'] == DataSourceType.SQL_TABLE_FROM_FILE.value:
                query_type_for_agent = "sql_agent"
            else: # KNOWLEDGE_BASE or other future non-default types
                query_type_for_agent = "rag"
        elif intent['type'] not in ["sales", "inventory", "report"]:
             # If default ERP and intent is unclear, fallback to general ERP / sales
            query_type_for_agent = "sales" # or a more generic ERP handler if available

        result = await get_answer_from_erp(request.query, query_type_for_agent, active_datasource=active_datasource_dict)
        
        return create_api_response(
            success=True,
            query=request.query,
            query_type=result.get("query_type", intent['type']), # Use query_type from agent if available
            intent=intent, # Keep original intent for context if needed
            answer=result.get("answer", "No answer could be generated."),
            data=result.get("data", {}),
            charts=result.get("chart_data"),
            suggestions=result.get("suggestions", []),
            datasource_id=ds_id_for_response,
            source_datasource_name=result.get("source_datasource_name", "Default ERP")
        )
        
    except Exception as e:
        # Log the full error for debugging
        # logger.error(f"Error processing query: {str(e)}", exc_info=True)
        return create_api_response(
            success=False,
            error=f"Query processing failed: {str(e)}",
            query=request.query,
            datasource_id=request.datasource_id # Pass original request DS ID if available
        )

# ==================== Inventory Management API ====================

@router.get("/inventory", summary="Get Inventory List")
async def get_inventory():
    """Get inventory information for all products"""
    try:
        products = await fetch_all_products()
        conn = get_db_connection()
        cursor = conn.cursor()
        inventory_list = []
        total_value = 0.0
        low_stock_count = 0
        out_of_stock_count = 0
        
        for product in products:
            cursor.execute("SELECT stock_level, last_updated FROM inventory WHERE product_id = ?", (product['product_id'],))
            inventory_info = cursor.fetchone()
            if inventory_info:
                stock_level = inventory_info['stock_level']
                unit_price = float(product['unit_price'])
                status = get_status_by_stock_level(stock_level)
                inventory_item = {
                    "id": product['product_id'], "name": product['product_name'], "category": product['category'],
                    "stock": stock_level, "unit_price": unit_price, "total_value": stock_level * unit_price,
                    "last_updated": inventory_info['last_updated'], "status": status,
                    "alert_level": get_alert_level_by_stock(stock_level)
                }
                inventory_list.append(inventory_item)
                total_value += inventory_item["total_value"]
                if status in ["low", "critical"]: low_stock_count += 1
                if status == "out_of_stock": out_of_stock_count += 1
        conn.close()
        return create_api_response(
            success=True, data=inventory_list,
            summary={
                "total_products": len(inventory_list), "total_value": total_value,
                "total_value_formatted": format_currency(total_value), "low_stock_count": low_stock_count,
                "out_of_stock_count": out_of_stock_count, "healthy_count": len(inventory_list) - low_stock_count
            }
        )
    except Exception as e:
        return create_api_response(success=False, error=f"Failed to retrieve inventory data: {str(e)}")

@router.get("/inventory/alerts", summary="Get Inventory Alerts")
async def get_inventory_alerts(threshold: int = Query(50, description="Inventory alert threshold")):
    """Get low stock alert information"""
    try:
        low_stock_items = await fetch_low_stock_products(threshold)
        alerts = []
        critical_count, urgent_count, warning_count = 0, 0, 0
        for item in low_stock_items:
            stock_level = item['stock_level']
            alert_level = get_alert_level_by_stock(stock_level)
            alert = {
                "product_id": item['product_id'], "product_name": item['product_name'],
                "current_stock": stock_level, "threshold": threshold, "alert_level": alert_level,
                "suggested_order_quantity": get_suggested_order_quantity(stock_level),
                "priority": 1 if alert_level == "critical" else 2 if alert_level == "urgent" else 3
            }
            alerts.append(alert)
            if alert_level == "critical": critical_count += 1
            elif alert_level == "urgent": urgent_count += 1
            else: warning_count += 1
        alerts.sort(key=lambda x: x['priority'])
        return create_api_response(
            success=True, data=alerts,
            summary={
                "total_alerts": len(alerts), "critical_count": critical_count,
                "urgent_count": urgent_count, "warning_count": warning_count
            }
        )
    except Exception as e:
        return create_api_response(success=False, error=f"Failed to retrieve inventory alerts: {str(e)}")

# ==================== Authentication API ====================

@router.post("/auth/login", summary="User Login (Placeholder)")
async def login(credentials: Dict[str, str]):
    """User login endpoint (placeholder)."""
    # In a real app, validate credentials, create a session/token
    if credentials.get("username") == "admin" and credentials.get("password") == "admin":
        return {"success": True, "message": "Login successful (placeholder)", "token": "fake-jwt-token"}
    raise HTTPException(status_code=401, detail="Invalid credentials (placeholder)")

@router.post("/auth/logout", summary="User Logout (Placeholder)")
async def logout():
    """User logout endpoint (placeholder)."""
    # In a real app, invalidate session/token
    return {"success": True, "message": "Logout successful (placeholder)"} 