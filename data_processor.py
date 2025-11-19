# data_processor.py - Final Implementation for Data Analysis Logic

# import requests
# import pandas as pd
# import io
# import re
# import os
# import fitz # PyMuPDF library for PDF handling
# import matplotlib.pyplot as plt
# import base64
# import numpy as np

# # -------------------------------------------------------------
# # Utility Functions
# # -------------------------------------------------------------

# def fetch_data(url: str) -> bytes:
#     """Fetches data from a given URL."""
#     print(f"[Data] Fetching data from: {url}")
#     # Using a 10-second timeout for external HTTP request
#     response = requests.get(url, timeout=10) 
#     response.raise_for_status()
#     return response.content

# def generate_base64_chart(data: pd.DataFrame, plan: dict) -> str:
#     """
#     Generates a simple bar chart based on calculated data, saves it as PNG, 
#     and returns the base64 string with the required prefix.
#     """
#     print(f"[Data] Generating chart for column: {plan['target_column']}")
    
#     column = plan['target_column']
#     if column == 'N/A':
#         raise ValueError("Cannot visualize without a target column.")

#     try:
#         # Find the best column for grouping (first non-numeric, excluding the target)
#         group_col = next((col for col in data.columns if data[col].dtype == 'object' and col != column), None)
        
#         if not group_col:
#             raise ValueError("No categorical column found for grouping/visualization.")

#         # Calculate data: Group by the categorical column and sum the target column
#         chart_data = data.groupby(group_col)[column].sum().sort_values(ascending=False).head(8)
        
#         fig, ax = plt.subplots(figsize=(8, 4))
#         chart_data.plot(kind='bar', ax=ax, color='teal')
        
#         ax.set_title(f"Top {len(chart_data)} {column} by {group_col}", fontsize=12)
#         ax.set_xlabel(group_col, fontsize=10)
#         ax.set_ylabel(plan['operation'], fontsize=10)
#         plt.xticks(rotation=45, ha='right')
#         plt.tight_layout()

#         # Save chart to an in-memory buffer
#         buffer = io.BytesIO()
#         plt.savefig(buffer, format='png')
#         plt.close(fig)
#         buffer.seek(0)
        
#         # Base64 encode and prepend prefix
#         base64_img = base64.b64encode(buffer.read()).decode('utf-8')
#         print("[Data] Chart generated and Base64 encoded successfully.")
#         return f"data:image/png;base64,{base64_img}"
    
#     except Exception as e:
#         raise ValueError(f"Visualization failed: {e}")


# # -------------------------------------------------------------
# # PDF Processing (Real Text Extraction)
# # -------------------------------------------------------------

# def extract_text_from_pdf_page(data_content: bytes, page_criteria: str) -> str:
#     """Uses PyMuPDF (fitz) to extract text from the specified page of the PDF."""
#     try:
#         page_num_match = re.search(r'(\d+)', page_criteria)
#         if not page_num_match:
#             raise ValueError("Could not find page number in criteria.")
        
#         target_page_index = int(page_num_match.group(0)) - 1
        
#         doc = fitz.open(stream=data_content, filetype="pdf")
        
#         if target_page_index < 0 or target_page_index >= len(doc):
#             raise IndexError(f"Page number {target_page_index + 1} is out of bounds.")
            
#         page = doc[target_page_index]
#         text = page.get_text()
#         doc.close()
        
#         return text

#     except Exception as e:
#         raise ValueError(f"PDF extraction failed: {e}")

# def process_pdf_data(data_content: bytes, plan: dict) -> float:
#     """
#     Reads a PDF, extracts data from the specified page, and performs the planned operation.
#     NOTE: Assumes the answer is the result of the operation on all numbers found on the target page.
#     """
#     print(f"[Data] PDF processing: Extracting data from page {plan['page_criteria']}")
    
#     page_text = extract_text_from_pdf_page(data_content, plan['page_criteria'])
    
#     # Simple regex to find numbers (floats or integers) on the page
#     values_raw = re.findall(r"[-+]?\d*\.\d+|\d+", page_text)
    
#     try:
#         values = [float(v) for v in values_raw]
#         if not values:
#             raise ValueError("No numeric values found in the extracted PDF text.")
            
#         operation = plan['operation']
        
#         if operation == 'SUM':
#             result = sum(values)
#         elif operation == 'AVG' or operation == 'MEAN':
#             result = np.mean(values)
#         elif operation == 'MAX':
#             result = max(values)
#         else:
#             raise ValueError(f"Unsupported PDF operation: {operation}")
            
#         print(f"[Data] Calculated PDF result: {result}")
#         return result
        
#     except ValueError as e:
#         raise ValueError(f"Error during PDF numeric processing: {e}")
#     except IndexError as e:
#         raise ValueError(f"Error during operation on PDF numbers: {e}")
#     return 0.0 # Fallback

# # -------------------------------------------------------------
# # CSV/Pandas Processing (Fully Implemented for Aggregation)
# # -------------------------------------------------------------

# def process_tabular_data(data_content: bytes, plan: dict) -> pd.DataFrame:
#     """
#     Reads CSV/JSON, and returns the processed DataFrame.
#     """
#     print(f"[Data] Tabular processing: {plan['file_type']} for column {plan['target_column']}")
    
#     try:
#         # 1. Load data
#         if plan['file_type'] == 'CSV':
#             df = pd.read_csv(io.StringIO(data_content.decode('utf-8')))
#         elif plan['file_type'] == 'JSON':
#             df = pd.read_json(io.BytesIO(data_content))
#         else:
#             raise ValueError(f"Unsupported file type for tabular processing: {plan['file_type']}")
            
#         column = plan['target_column']
#         if column != 'N/A' and column not in df.columns:
#             raise ValueError(f"Column '{column}' not found in data frame.")

#         # 2. Prepare for analysis/filtering
#         # Convert the target column to numeric (errors become NaN)
#         if column != 'N/A':
#             df[column] = pd.to_numeric(df[column], errors='coerce')
#             df.dropna(subset=[column], inplace=True)
        
#         # 3. Apply filtering if criteria exists
#         criteria = plan.get('page_criteria', 'N/A')
#         if criteria != 'N/A' and '=' in criteria:
#             filter_col, filter_val = criteria.split('=', 1)
#             filter_col = filter_col.strip()
#             filter_val = filter_val.strip()
            
#             if filter_col in df.columns:
#                 # Basic categorical filter
#                 df = df[df[filter_col].astype(str).str.strip() == filter_val]
#                 print(f"[Data] Filter applied: {filter_col} = {filter_val}. Rows remaining: {len(df)}")
#             else:
#                 print(f"[Data] Warning: Filter column '{filter_col}' not found.")
                
#         return df
    
#     except Exception as e:
#         raise ValueError(f"Tabular processing failed: {e}")

# # -------------------------------------------------------------
# # execute_analysis_plan (Main dispatcher)
# # -------------------------------------------------------------

# def execute_analysis_plan(plan: dict) -> object:
#     """
#     Downloads data and executes the LLM-generated analysis plan.
#     Returns the final answer in the expected type.
#     """
#     data_content = fetch_data(plan['data_url'])
#     operation = plan['operation']
#     answer = None
    
#     # 1. Handle PDF
#     if plan['file_type'] == 'PDF':
#         answer = process_pdf_data(data_content, plan)
        
#     # 2. Handle Tabular Data (CSV/JSON)
#     elif plan['file_type'] in ('CSV', 'JSON'):
        
#         df = process_tabular_data(data_content, plan)
#         column = plan['target_column']

#         if operation == 'VISUALIZE':
#             answer = generate_base64_chart(df, plan)
            
#         elif column != 'N/A':
#             # Perform aggregation on the resulting DataFrame
#             if operation == 'SUM':
#                 result = df[column].sum()
#             elif operation in ('AVG', 'MEAN'):
#                 result = df[column].mean()
#             elif operation == 'MAX':
#                 result = df[column].max()
#             else:
#                 raise ValueError(f"Unsupported tabular operation: {operation}")
            
#             print(f"[Data] Final Tabular Result: {result}")
#             answer = result
        
#         else:
#             raise ValueError(f"Tabular operation '{operation}' requires a target column.")

#     # 3. Handle Other/Unsupported
#     else:
#         print(f"[Data] Operation {operation} on {plan['file_type']} not implemented.")
#         answer = "PlanNotImplemented"

#     # Final formatting based on LLM's expected answer type
#     if plan['answer_type'] == 'number':
#         # Return the number rounded to two decimal places
#         return round(float(answer), 2) if answer is not None else 0
    
#     return str(answer)

# import requests
# import pandas as pd
# import io
# import re
# import fitz # PyMuPDF
# import matplotlib.pyplot as plt
# import base64
# import numpy as np

# def fetch_data(url: str) -> bytes:
#     print(f"[Data] Fetching data from: {url}")
#     response = requests.get(url, timeout=10) 
#     response.raise_for_status()
#     return response.content

# def generate_base64_chart(data: pd.DataFrame, plan: dict) -> str:
#     column = plan.get('target_column', 'N/A')
    
#     # --- FIX: AUTO-SELECT LOGIC ---
#     if column == 'N/A':
#         numeric_cols = data.select_dtypes(include=[np.number]).columns
#         if len(numeric_cols) > 0:
#             column = numeric_cols[0]
#             print(f"[Data] Auto-selected target column: {column}")
#         else:
#             raise ValueError("Cannot visualize: No numeric columns found.")
    
#     group_col = next((col for col in data.columns if data[col].dtype == 'object' and col != column), 'Index')
#     if group_col == 'Index': data['Index'] = data.index

#     data[column] = pd.to_numeric(data[column], errors='coerce')
#     chart_data = data.groupby(group_col)[column].sum().sort_values(ascending=False).head(8)
    
#     fig, ax = plt.subplots(figsize=(8, 4))
#     chart_data.plot(kind='bar', ax=ax, color='teal')
#     plt.tight_layout()

#     buffer = io.BytesIO()
#     plt.savefig(buffer, format='png')
#     plt.close(fig)
#     buffer.seek(0)
    
#     base64_img = base64.b64encode(buffer.read()).decode('utf-8')
#     return f"data:image/png;base64,{base64_img}"

# def extract_text_from_pdf_page(data_content: bytes, page_criteria: str) -> str:
#     try:
#         page_num_match = re.search(r'(\d+)', str(page_criteria))
#         target_page_index = int(page_num_match.group(0)) - 1 if page_num_match else 0
        
#         doc = fitz.open(stream=data_content, filetype="pdf")
#         if target_page_index >= len(doc): 
#              full_text = "\n".join([page.get_text() for page in doc])
#              doc.close()
#              return full_text
        
#         text = doc[target_page_index].get_text()
#         doc.close()
#         return text
#     except Exception as e:
#         raise ValueError(f"PDF extraction failed: {e}")

# def process_pdf_data(data_content: bytes, plan: dict) -> object:
#     print(f"[Data] Processing PDF/Text data...")
#     text_content = ""
#     try:
#         if data_content.startswith(b'%PDF'):
#              text_content = extract_text_from_pdf_page(data_content, plan.get('page_criteria', 'N/A'))
#         else:
#              text_content = data_content.decode('utf-8', errors='ignore')
#     except:
#         text_content = str(data_content)

#     operation = plan['operation']
#     if operation == 'STRING_EXTRACT': return text_content.strip()
        
#     values = [float(v) for v in re.findall(r"[-+]?\d*\.\d+|\d+", text_content)]
#     if not values: return 0.0
    
#     if operation == 'SUM': return sum(values)
#     if operation in ['AVG', 'MEAN']: return np.mean(values)
#     if operation == 'MAX': return max(values)
#     return 0.0

# def process_tabular_data(data_content: bytes, plan: dict) -> object:
#     print(f"[Data] Processing {plan['file_type']}")
#     try:
#         if plan['file_type'] == 'CSV':
#             # CSV Header Fix
#             df = pd.read_csv(io.StringIO(data_content.decode('utf-8')))
#             if any(str(col).replace('.','').isdigit() for col in df.columns):
#                 print("[Data] Detected numeric header. Reloading with header=None.")
#                 df = pd.read_csv(io.StringIO(data_content.decode('utf-8')), header=None)
#                 df.columns = [f"col_{i}" for i in range(len(df.columns))]
#         else:
#             df = pd.read_json(io.BytesIO(data_content))
            
#         df.columns = df.columns.str.strip()

#         # AUTO COLUMN SELECTION
#         col = plan['target_column']
#         if col == 'N/A' or col not in df.columns:
#             numeric_cols = df.select_dtypes(include=[np.number]).columns
#             if len(numeric_cols) > 0:
#                 col = numeric_cols[0]
#                 print(f"[Data] Auto-picked column '{col}'")
#             else:
#                 col = df.columns[-1]

#         if plan['operation'] == 'VISUALIZE':
#              plan['target_column'] = col
#              return generate_base64_chart(df, plan)

#         if col in df.columns:
#             df[col] = pd.to_numeric(df[col], errors='coerce')
#             op = plan['operation']
#             if op == 'SUM': return df[col].sum()
#             if op in ['AVG', 'MEAN']: return df[col].mean()
#             if op == 'MAX': return df[col].max()
            
#         return 0
#     except Exception as e:
#         print(f"[Data] Error: {e}")
#         return 0

# def execute_analysis_plan(plan: dict) -> object:
#     data_content = fetch_data(plan['data_url'])
#     ft = plan['file_type']
    
#     if ft == 'PDF' or ft == 'N/A':
#         answer = process_pdf_data(data_content, plan)
#     elif ft in ('CSV', 'JSON'):
#         answer = process_tabular_data(data_content, plan)
#     else:
#         answer = process_pdf_data(data_content, plan)

#     if plan['answer_type'] == 'number':
#         try: return round(float(answer), 2)
#         except: return 0
#     return str(answer)

import requests
import pandas as pd
import io
import re
import fitz # PyMuPDF
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
import numpy as np

def fetch_data(url: str) -> bytes:
    print(f"[Data] Fetching data from: {url}")
    response = requests.get(url, timeout=10) 
    response.raise_for_status()
    return response.content

def generate_base64_chart(data: pd.DataFrame, plan: dict) -> str:
    column = plan.get('target_column', 'N/A')
    
    if column == 'N/A':
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            column = numeric_cols[0]
            print(f"[Data] Auto-selected target column: {column}")
        else:
            raise ValueError("Cannot visualize: No numeric columns found.")
    
    group_col = next((col for col in data.columns if data[col].dtype == 'object' and col != column), 'Index')
    if group_col == 'Index':
        data['Index'] = data.index

    data[column] = pd.to_numeric(data[column], errors='coerce')
    chart_data = data.groupby(group_col)[column].sum().sort_values(ascending=False).head(8)
    
    fig, ax = plt.subplots(figsize=(8, 4))
    chart_data.plot(kind='bar', ax=ax, color='teal')
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    
    base64_img = base64.b64encode(buffer.read()).decode('utf-8')
    return f"data:image/png;base64,{base64_img}"

def extract_text_from_pdf_page(data_content: bytes, page_criteria: str) -> str:
    try:
        page_num_match = re.search(r'(\d+)', str(page_criteria))
        target_page_index = int(page_num_match.group(0)) - 1 if page_num_match else 0
        
        doc = fitz.open(stream=data_content, filetype="pdf")
        if target_page_index >= len(doc): 
             full_text = "\n".join([page.get_text() for page in doc])
             doc.close()
             return full_text
        
        text = doc[target_page_index].get_text()
        doc.close()
        return text
    except Exception as e:
        raise ValueError(f"PDF extraction failed: {e}")

def process_pdf_data(data_content: bytes, plan: dict) -> object:
    print(f"[Data] Processing PDF/Text data...")
    text_content = ""
    try:
        if data_content.startswith(b'%PDF'):
             text_content = extract_text_from_pdf_page(data_content, plan.get('page_criteria', 'N/A'))
        else:
             text_content = data_content.decode('utf-8', errors='ignore')
    except:
        text_content = str(data_content)

    operation = plan['operation']
    if operation == 'STRING_EXTRACT': return text_content.strip()
        
    values = [float(v) for v in re.findall(r"[-+]?\d*\.\d+|\d+", text_content)]
    if not values: return 0.0
    
    if operation == 'SUM': return sum(values)
    if operation in ['AVG', 'MEAN']: return np.mean(values)
    if operation == 'MAX': return max(values)
    return 0.0

def process_tabular_data(data_content: bytes, plan: dict) -> object:
    print(f"[Data] Processing {plan['file_type']}")
    try:
        if plan['file_type'] == 'CSV':
            df = pd.read_csv(io.StringIO(data_content.decode('utf-8')))
            if any(str(col).replace('.','').isdigit() for col in df.columns):
                print("[Data] Detected numeric header. Reloading with header=None.")
                df = pd.read_csv(io.StringIO(data_content.decode('utf-8')), header=None)
                df.columns = [f"col_{i}" for i in range(len(df.columns))]
        else:
            df = pd.read_json(io.BytesIO(data_content))
            
        df.columns = df.columns.str.strip()

        # --- CRITICAL FIX: Handle Bad Column Names ---
        col = plan['target_column']
        if col not in df.columns and col != 'N/A':
            print(f"[Data] Warning: Column '{col}' not found. Switching to Auto-Selection.")
            col = 'N/A'
            
        # Auto-Selection Logic
        if col == 'N/A':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                col = numeric_cols[-1] # Use LAST numeric column (likely 'Value')
                print(f"[Data] Auto-picked column: '{col}'")
            else:
                col = df.columns[-1]

        if plan['operation'] == 'VISUALIZE':
             plan['target_column'] = col
             return generate_base64_chart(df, plan)

        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            op = plan['operation']
            if op == 'SUM': return df[col].sum()
            if op in ['AVG', 'MEAN']: return df[col].mean()
            if op == 'MAX': return df[col].max()
            
        return 0
    except Exception as e:
        print(f"[Data] Tabular error: {e}")
        return data_content.decode('utf-8', errors='ignore').strip()

def execute_analysis_plan(plan: dict) -> object:
    data_content = fetch_data(plan['data_url'])
    ft = plan['file_type']
    
    if ft == 'PDF' or ft == 'N/A':
        answer = process_pdf_data(data_content, plan)
    elif ft in ('CSV', 'JSON'):
        answer = process_tabular_data(data_content, plan)
    else:
        answer = process_pdf_data(data_content, plan)

    if plan['answer_type'] == 'number':
        try: return round(float(answer), 2)
        except: return 0
    return str(answer) 