import numpy as np
import json
import base64
import cv2
from keras_facenet import FaceNet

embedder = FaceNet()

# Convert base64 image to embedding
def generate_embedding_from_base64(base64_image):

    # Remove header part if present
    if "," in base64_image:
        base64_image = base64_image.split(",")[1]

    image_bytes = base64.b64decode(base64_image)
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    embedding = embedder.embeddings([img])[0]
    return embedding.tolist()


def compare_faces(stored_embedding, live_embedding, threshold=0.7):

    if isinstance(stored_embedding, str):
        stored_embedding = json.loads(stored_embedding)

    distance = np.linalg.norm(
        np.array(stored_embedding) - np.array(live_embedding)
    )

    return distance < threshold
