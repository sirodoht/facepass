import base64
from pathlib import Path

import cv2
import face_recognition
import numpy as np
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel


def load_faces():
    """
    Load known face images and extract encodings.
    """
    known_face_encodings = {}

    for file in Path("./data").iterdir():
        print(f"Loading {file}")
        person_name = file.name.split(".")[0].capitalize()
        image = face_recognition.load_image_file(file)
        encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings[person_name] = encoding

    return known_face_encodings


app = FastAPI()

templates = Jinja2Templates(directory="templates")
known_face_encodings = load_faces()


class Frame(BaseModel):
    image_base64: str


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/process")
async def process(payload: Frame):
    header, encoded = payload.image_base64.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    nparr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert to RGB for face_recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

    # Compare with known faces
    recognized_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(
            list(known_face_encodings.values()), face_encoding
        )
        if True in matches:
            idx = matches.index(True)
            name = list(known_face_encodings.keys())[idx]
            recognized_names.append(name)

    return JSONResponse(content={"recognized": recognized_names})
