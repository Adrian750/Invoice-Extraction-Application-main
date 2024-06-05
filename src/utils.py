import os
import json
import traceback
import PyPDF2
from PIL import Image
from io import BytesIO

from langchain.document_loaders.image import UnstructuredImageLoader

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text

        except Exception as e:
            raise Exception("error reading the PDF File")
        
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    
    elif file.name.endswith(".jpeg"):
        image_list = [list(data.values())[0] for data in file]
        image_content = []
    
        for index, image_bytes in enumerate(image_list):
        
            image = Image.open(BytesIO(image_bytes))
            loader = UnstructuredImageLoader(image)
            data = loader.load()
            raw_text = data[index].page_content
                        
            image_content.append(raw_text)

        text = "\n".join(image_content)
        return text
    
    else:
        raise Exception("unsupported file format, only pdf and jpeg file supported")
    