import asyncio
from pathlib import Path
import pandas as pd
import re # For sanitizing column names
import uuid # For unique table name suffix
from .db import update_file_processing_status, get_datasource, set_datasource_table_name, get_db_connection # Assuming get_db_connection might be needed for other ops
from .models import ProcessingStatus, DataSourceType, FileType # Ensure enums are available
import logging

logger = logging.getLogger(__name__)

def sanitize_column_name(col_name: str) -> str:
    """Converts a column name to a safe SQL column name."""
    # Remove or replace illegal characters, e.g., spaces, special symbols.
    # Convert to lowercase, replace spaces with underscores.
    col_name = str(col_name).lower()
    col_name = re.sub(r'\s+', '_', col_name) # Replace spaces with underscores
    col_name = re.sub(r'[^a-z0-9_]', '', col_name) # Remove non-alphanumeric (excluding underscore)
    if not col_name: # If empty after processing (e.g., original name was all special chars)
        col_name = "column_" + uuid.uuid4().hex[:6]
    elif col_name[0].isdigit(): # If starts with a digit, add a prefix
        col_name = "col_" + col_name
    return col_name

async def _create_table_from_df(conn, table_name: str, df: pd.DataFrame):
    """Dynamically creates an SQLite table based on DataFrame columns."""
    sanitized_columns = {col: sanitize_column_name(col) for col in df.columns}
    df_renamed = df.rename(columns=sanitized_columns)
    
    # Simplified SQLite type inference: TEXT for all, or basic inference.
    # For more robust type inference, one might inspect df.dtypes.
    # A more advanced version could map pandas dtypes to SQLite types.
    cols_with_types = ", ".join([f'"{col_name}" TEXT' for col_name in df_renamed.columns])
    
    create_table_sql = f"CREATE TABLE IF NOT EXISTS \"{table_name}\" ({cols_with_types})"
    logger.info(f"Executing SQL to create table: {create_table_sql}")
    
    cursor = conn.cursor()
    cursor.execute(create_table_sql)
    conn.commit()
    return df_renamed # Return dataframe with sanitized column names

async def _insert_df_to_table(conn, table_name: str, df_renamed: pd.DataFrame):
    """Inserts DataFrame data into the specified SQLite table."""
    logger.info(f"Inserting {len(df_renamed)} rows into table '{table_name}'")
    
    cols = df_renamed.columns
    placeholders = ", ".join(["?" for _ in cols])
    formatted_column_names = [f'"{c}"' for c in cols]
    columns_sql_string = ", ".join(formatted_column_names)
    insert_sql = f"INSERT INTO \"{table_name}\" ({columns_sql_string}) VALUES ({placeholders})"
    
    cursor = conn.cursor()
    try:
        data_to_insert = [tuple(row) for row in df_renamed.itertuples(index=False, name=None)]
        cursor.executemany(insert_sql, data_to_insert)
        conn.commit()
        logger.info(f"Successfully inserted {len(data_to_insert)} rows into '{table_name}'.")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting data into '{table_name}': {e}", exc_info=True)
        raise

async def process_uploaded_file(
    file_id: int, 
    datasource_id: int, 
    file_path: Path, 
    original_filename: str, 
    file_type: str 
):
    """
    Background task to process uploaded files.
    - If data source type is SQL_TABLE_FROM_FILE and file is CSV/XLSX, parse and store in a new table.
    - Other cases (e.g., knowledge base files) currently simulate processing and update status.
    """
    logger.info(f"[FileProcessor] Starting processing for file ID: {file_id}, DS_ID: {datasource_id}, Name: {original_filename}")

    datasource_details = await get_datasource(datasource_id)
    if not datasource_details:
        logger.error(f"[FileProcessor] Datasource {datasource_id} not found. Cannot process file {file_id}.")
        await update_file_processing_status(file_id, status=ProcessingStatus.FAILED.value, error_message="Associated datasource not found.")
        return

    ds_type = datasource_details.get('type')
    conn = None

    try:
        await update_file_processing_status(file_id, status=ProcessingStatus.PROCESSING.value)
        logger.info(f"[FileProcessor] File ID: {file_id} - Status set to PROCESSING. Datasource type: {ds_type}")

        if ds_type == DataSourceType.SQL_TABLE_FROM_FILE.value and file_type.lower() in [FileType.CSV.value, FileType.XLSX.value]:
            logger.info(f"[FileProcessor] Processing '{file_type}' file '{original_filename}' for SQL table ingestion.")
            
            if not file_path.exists():
                logger.error(f"[FileProcessor] File not found at path: {file_path}. Cannot ingest.")
                raise FileNotFoundError(f"Source file {original_filename} not found at {file_path}")

            df = None
            if file_type.lower() == FileType.CSV.value:
                df = pd.read_csv(file_path, on_bad_lines='skip')
            elif file_type.lower() == FileType.XLSX.value:
                xls = pd.ExcelFile(file_path)
                if xls.sheet_names:
                    df = xls.parse(xls.sheet_names[0])
                else:
                    raise ValueError("Excel file contains no sheets.")
            
            if df is None or df.empty:
                logger.warning(f"[FileProcessor] DataFrame is empty for file {original_filename}. No data to ingest.")
                await update_file_processing_status(file_id, status=ProcessingStatus.COMPLETED.value, chunks=0, error_message="File was empty or unreadable as table.")
                return

            base_name = Path(original_filename).stem
            unique_suffix = uuid.uuid4().hex[:8]
            sane_base_name = re.sub(r'\W|\s', '_', base_name)
            table_name = f"dstable_{datasource_id}_{sane_base_name}_{unique_suffix}" 
            table_name = table_name[:60]
            logger.info(f"[FileProcessor] Generated table name: {table_name}")

            conn = get_db_connection()
            df_renamed = await _create_table_from_df(conn, table_name, df)
            await _insert_df_to_table(conn, table_name, df_renamed)
            
            await set_datasource_table_name(datasource_id, table_name)
            logger.info(f"[FileProcessor] Successfully linked table '{table_name}' to datasource {datasource_id}")
            
            await update_file_processing_status(file_id, status=ProcessingStatus.COMPLETED.value, chunks=len(df))
            logger.info(f"[FileProcessor] File ID: {file_id} - SQL table ingestion COMPLETED. Rows: {len(df)}")

        else:
            logger.info(f"[FileProcessor] File ID: {file_id} - Not a CSV/XLSX for SQL table or wrong DS type. Using placeholder processing.")
            await asyncio.sleep(5) # Simulate processing for other file types
            processed_chunks_count = 50 # Placeholder
            await update_file_processing_status(file_id, status=ProcessingStatus.COMPLETED.value, chunks=processed_chunks_count)
            logger.info(f"[FileProcessor] File ID: {file_id} - Placeholder processing COMPLETED.")

    except Exception as e:
        logger.error(f"[FileProcessor] Error processing file ID: {file_id}, Name: {original_filename}. Error: {str(e)}", exc_info=True)
        await update_file_processing_status(file_id, status=ProcessingStatus.FAILED.value, error_message=str(e))
    finally:
        if conn:
            conn.close()
        logger.info(f"[FileProcessor] Finished processing attempt for file ID: {file_id}, Name: {original_filename}")

# More file processing helper functions can be added here, for example:
# async def parse_pdf(file_path: Path) -> str: ...
# async def parse_docx(file_path: Path) -> str: ...
# async def chunk_text(text: str) -> List[str]: ...
# async def generate_embeddings(chunks: List[str]) -> List[List[float]]: ...
# async def store_vector_chunks(file_id: int, chunks: List[str], embeddings: List[List[float]]): ... 