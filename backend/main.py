from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import uvicorn
import uuid

# Import custom utilities and engines
from backend.utils.data_cleaner import clean_data
from backend.engines.core_engine import CoreAnalyzer
from backend.engines.ai_engine import AIEngine
from backend.utils.visualizer import generate_plots

app = FastAPI(title="AutoInsight AI Professional")

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store for cleaned datasets (Temporary cache)
CLEANED_DATA_STORE = {}

@app.get("/")
def health_check():
    return {"status": "online", "message": "AutoInsight AI API is running."}

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...), engine: str = Query("v2")):
    try:
        # 1. READ UPLOADED FILE BYTES
        contents = await file.read()
        filename = file.filename
        extension = filename.split('.')[-1].lower() if '.' in filename else 'csv'

        # 2. RESILIENT FILE PARSING
        if extension == 'csv':
            try:
                # Try modern standard encoding
                df = pd.read_csv(io.BytesIO(contents), encoding='utf-8')
            except UnicodeDecodeError:
                # Fallback for Excel-style CSVs (Fixes the 0x96 error)
                df = pd.read_csv(io.BytesIO(contents), encoding='latin1')
        elif extension in ['xls', 'xlsx']:
            # Requires: pip install openpyxl
            df = pd.read_excel(io.BytesIO(contents))
        else:
            return {"status": "error", "message": "Unsupported format. Use CSV or Excel."}

        if df.empty:
            return {"status": "error", "message": "The uploaded file is empty."}

        # 3. SCIENTIFIC CLEANING PIPELINE
        df_cleaned, clean_report = clean_data(df)
        
        # 4. CACHE CLEANED DATA FOR DOWNLOAD (Format-Aware)
        file_id = str(uuid.uuid4())
        CLEANED_DATA_STORE[file_id] = {
            "df": df_cleaned,
            "original_name": filename,
            "extension": extension
        }

        # 5. CORE STATISTICAL ANALYSIS (V1)
        core = CoreAnalyzer(df_cleaned)
        v1_insights = core.generate_insights()
        basic_info = core.get_basic_info()
        
        # 6. INTELLIGENT VISUALIZATION (Ranked Selection)
        plots = generate_plots(df_cleaned, core.schema, core.ranked_numeric)

        final_insights = v1_insights
        ai_summary = ""

        # 7. GROUNDED AI ENHANCEMENT (V2)
        if engine == "v2":
            try:
                # Pass statistical snapshot to prevent AI hallucinations
                ai_worker = AIEngine(
                    basic_info=basic_info, 
                    stats_snapshot=core.stats_snapshot, 
                    v1_insights=v1_insights
                )
                ai_summary = ai_worker.get_smart_summary()
                enhanced = ai_worker.enhance_insights()
                # Split into a clean list of insights
                final_insights = [line.strip() for line in enhanced.split('\n') if len(line.strip()) > 10]
            except Exception as ai_err:
                print(f"AI Engine Fallback: {ai_err}")
                ai_summary = "AI interpretation is unavailable. Displaying Core mathematical results."

        return {
            "status": "success",
            "file_id": file_id,
            "insights": final_insights,
            "visualizations": plots,
            "basic_info": basic_info,
            "cleaning_report": clean_report,
            "ai_summary": ai_summary
        }

    except Exception as e:
        print(f"CRITICAL SERVER ERROR: {str(e)}")
        return {"status": "error", "message": f"Analysis failed: {str(e)}"}

@app.get("/download/{file_id}")
async def download_file(file_id: str):
    """
    Format-aware download route. 
    Handles true binary Excel exports and Excel-compatible CSVs.
    """
    if file_id not in CLEANED_DATA_STORE:
        raise HTTPException(status_code=404, detail="File expired or not found. Please re-analyze.")
    
    file_info = CLEANED_DATA_STORE[file_id]
    df = file_info["df"]
    ext = file_info["extension"]
    original_name = file_info["original_name"]
    
    stream = io.BytesIO()
    
    # --- BINARY EXCEL EXPORT ---
    if ext in ['xlsx', 'xls']:
        with pd.ExcelWriter(stream, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        download_name = f"cleaned_{original_name}"
        if not download_name.endswith('.xlsx'):
            download_name = download_name.rsplit('.', 1)[0] + '.xlsx'
            
    # --- COMPATIBLE CSV EXPORT ---
    else:
        # utf-8-sig ensures Excel opens symbols and dashes correctly
        df.to_csv(stream, index=False, encoding='utf-8-sig')
        media_type = "text/csv"
        download_name = f"cleaned_{original_name}"
        if not download_name.endswith('.csv'):
            download_name = download_name.rsplit('.', 1)[0] + '.csv'

    stream.seek(0)
    
    return StreamingResponse(
        stream, 
        media_type=media_type, 
        headers={
            "Content-Disposition": f"attachment; filename={download_name}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)