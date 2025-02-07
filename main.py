from pathlib import Path

import cv2
import face_recognition
import numpy as np

# Load faces and extract encodings
known_face_encodings = {}
for file in Path("./data").iterdir():
    print(f"Loading {file}")
    person_name = file.name.split(".")[0].capitalize()
    image = face_recognition.load_image_file(file)
    encoding = face_recognition.face_encodings(image)[0]
    # Store in a dictionary
    known_face_encodings[person_name] = encoding

# Initialize video capture
video_capture = cv2.VideoCapture(0)

while True:
    ret, frame = video_capture.read()
    if not ret:
        # Continue if video capture does not return any frame data
        continue

    # Convert the image from BGR color (which OpenCV uses) to RGB color
    rgb_frame = np.ascontiguousarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    # Find all the faces and face encodings in the frame
    face_locations = face_recognition.face_locations(rgb_frame)
    face_encoding_list = face_recognition.face_encodings(rgb_frame, face_locations)

    for face_encoding in face_encoding_list:
        # Compare with known faces
        matches = face_recognition.compare_faces(
            list(known_face_encodings.values()), face_encoding
        )
        if True in matches:
            index = matches.index(True)
            name = list(known_face_encodings.keys())[index]
            print(f"Access granted for {name}")
        else:
            print(f"No person recognized among {len(known_face_encodings)} photos")

    # Display the resulting frame
    cv2.imshow("Video", frame)

    # Break loop on key press
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

video_capture.release()
cv2.destroyAllWindows()
