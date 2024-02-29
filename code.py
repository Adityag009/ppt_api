import subprocess
import pathlib
import tempfile
from PIL import Image
import google.generativeai as genai

model = genai.GenerativeModel('gemini-pro-vision')
def convert_ppt_to_images_and_analyze(pptx_file, output_path):
    if not str(output_path).endswith("Images"):
        img_path = output_path / "Images"
    else:
        img_path = output_path
    img_path.mkdir(parents=True, exist_ok=True)

    slide_analysis_results = []

    with tempfile.TemporaryDirectory() as temp_pdf_folder:
        subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", temp_pdf_folder, pptx_file], check=True)
        pdf_files = list(pathlib.Path(temp_pdf_folder).glob("*.pdf"))

        if not pdf_files:
            print("No PDF files were created from the PPTX.")
            return slide_analysis_results

        for pdf_file in pdf_files:
            base_name = pdf_file.stem.replace(' ', '_')
            pdf_to_png_output_path = img_path / base_name
            pdf_to_png_output_path.mkdir(parents=True, exist_ok=True)

            subprocess.run(["gs", "-sDEVICE=pngalpha", "-o", f"{pdf_to_png_output_path}/{base_name}_slide_%02d.png", "-r144", pdf_file], check=True)
            generated_images = list(pdf_to_png_output_path.glob(f"{base_name}_slide_*.png"))

        for img_path in generated_images:
            with Image.open(img_path) as img:
                # Extract slide name from the image path (filename without extension)
                slide_name = img_path.stem
                slide_analysis = analyze_slide_image(img, slide_name)  # Pass slide name here
                slide_analysis_results.append(slide_analysis)

    return slide_analysis_results

# Placeholder function for slide image analysis
def analyze_slide_image(img,slide_name):
    response = model.generate_content(['''Carefully examine the provided PowerPoint slide image to identify and describe specific elements. For each element that is visibly present in the image, detail the content it contains, following the structure provided below. Only mention the elements found in the image; if an element is not present, omit it entirely from your response. This approach ensures that your output only reflects the content actually visible on the slide.

For the elements you identify, provide concise yet informative descriptions within the categories listed. Do not include counts or descriptions of elements that are absent from the slide.

- Title: Only if a title is present.
- Subtitle: If there's a subtitle.
- Paragraph: Mention the presence of paragraphs and write the text it content.
- Bullet Points: Mention the bullet points, write the text it content.
- Image: For images, give a general category.
- Table: If a table is detected, summarize the type of data it displays, noting rows and columns only if relevant.
- Quotes: Mention the presence of Quotes
- List: Describe lists, including the general subject, only if present.
- Cycle Infographic, Process Infographic, Timeline Infographic, Funnel Infographic, Pyramid Infographic: Note these only if they are present.
- Equation: If equations are found.
- Graph: Describe any graphs, mentioning their type (e.g., bar, line, pie) and the data they represent, only if applicable.

Your output should directly reflect the content of the slide, focusing exclusively on the elements that are present. Avoid mentioning any element not explicitly found in the slide image."
..''', img], stream=True)
    response.resolve()

    # Prepare the analysis of the current slide for sending to the API
    slide_analysis_json = json.dumps({slide_name: response.text}, indent=4)
    return slide_analysis_json