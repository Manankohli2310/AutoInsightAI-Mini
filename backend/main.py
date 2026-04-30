from fastapi import FastAPI, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import io
import uvicorn

from backend.utils.data_cleaner import clean_data
from backend.engines.core_engine import CoreAnalyzer
from backend.engines.ai_engine import AIEngine
from backend.utils.visualizer import generate_plots

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...), engine: str = Query("v1")):
    try:
        contents = await file.read()
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        else:
            df = pd.read_excel(io.BytesIO(contents))

        # 1. Core Processing (Always needed for Math/Charts)
        df_cleaned, clean_report = clean_data(df)
        core = CoreAnalyzer(df_cleaned)
        v1_insights = core.generate_insights()
        basic_info = core.get_basic_info()
        plots = generate_plots(df_cleaned)

        final_insights = v1_insights
        ai_summary = ""

        # 2. AI Enhancement (Only if V2 selected)
        if engine == "v2":
            try:
                ai_worker = AIEngine(basic_info, v1_insights)
                ai_summary = ai_worker.get_smart_summary()
                # Get professional rewrite of insights
                enhanced = ai_worker.enhance_insights()
                final_insights = [line.strip() for line in enhanced.split('\n') if line.strip()]
            except Exception as ai_err:
                print(f"AI Engine Error: {ai_err}")
                ai_summary = "AI Engine is currently unavailable. Showing Core Engine results."

        return {
            "status": "success",
            "engine_used": engine,
            "ai_summary": ai_summary,
            "insights": final_insights,
            "visualizations": plots,
            "basic_info": basic_info,
            "cleaning_report": clean_report
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)