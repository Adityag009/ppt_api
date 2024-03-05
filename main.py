import pathlib
import tempfile
from fastapi import FastAPI, File, UploadFile
from code import convert_ppt_to_images_and_analyze
from pathlib import Path
app = FastAPI()

TEMP_DIR = pathlib.Path(tempfile.mkdtemp())

@app.post("/analyze_ppt/")
async def analyze_ppt(file: UploadFile = File(...)):
    temp_ppt_path = TEMP_DIR / file.filename

    with temp_ppt_path.open("wb") as temp_ppt:
        temp_ppt.write(await file.read())

    try:
        output_folder = Path.home() / "aditya/ppt/ppt_api/data"
        ppt_images = convert_ppt_to_images_and_analyze(temp_ppt_path, output_folder)
        response_data = {"status": "success", "message": "Analysis completed successfully", "results": ppt_images}
    except Exception as e:
        response_data = {"status": "error", "message": f"An error occurred: {str(e)}"}

    return response_data
