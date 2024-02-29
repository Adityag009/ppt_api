import pathlib
import tempfile
from fastapi import FastAPI, File, UploadFile
from code import convert_ppt_to_images_and_analyze

app = FastAPI()

TEMP_DIR = pathlib.Path(tempfile.mkdtemp())

@app.post("/analyze_ppt/")
async def analyze_ppt(file: UploadFile = File(...)):
    temp_ppt_path = TEMP_DIR / file.filename

    with temp_ppt_path.open("wb") as temp_ppt:
        temp_ppt.write(await file.read())

    try:
        ppt_images = convert_ppt_to_images_and_analyze(temp_ppt_path)
        response_data = {"status": "success", "message": "Analysis completed successfully", "results": ppt_images}
    except Exception as e:
        response_data = {"status": "error", "message": f"An error occurred: {str(e)}"}
    finally:
        temp_ppt_path.unlink()  # Delete the temporary PPT file
        if 'ppt_images' in locals():
            for img_path in ppt_images:
                img_path.unlink()  # Delete each temporary image file

    return response_data
