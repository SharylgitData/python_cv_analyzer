from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import shutil
from service.ResumeEvaluator import ResumeEvaluator
import io
app = FastAPI()



@app.post("/uploadPdf")
async def upload_pdf(
    file: UploadFile = File(...),
    personality: str = Form(...),
    emailId: str = Form(...),
    job_id: str = Form(...),
    job_description: str = Form(...)
    
):
    # Validate that the uploaded file is a PDF
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Invalid file type, only PDFs are allowed")
    
    try:
        evaluator = ResumeEvaluator()
        print("evaluator", evaluator)
        contents = await file.read()
        file_stream = io.BytesIO(contents)

        print("📄 Resume uploaded: ", file.filename)
        print("🧠 Job Description: ", job_description)

        # result = evaluator.evaluate_resume(file_stream, job_description, personality, prompt_type="rank" )
        result = evaluator.extract_resume_info(file_stream, job_description, personality, prompt_type="rank")
        return {"response": result}

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")



if __name__ == '__main__':
    app.run(debug=True)