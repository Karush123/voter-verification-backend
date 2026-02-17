import numpy as np
import base64
import io
from PIL import Image
from keras_facenet import FaceNet

embedder = FaceNet()

def get_face_embedding(base64_image):
    image_data = base64.b64decode(base64_image)
    image = Image.open(io.BytesIO(image_data))
    image = np.array(image)

    embeddings = embedder.embeddings([image])
    return embeddings[0].tolist()


def compare_faces(stored_embedding, new_embedding, threshold=0.6):
    stored = np.array(stored_embedding)
    new = np.array(new_embedding)

    distance = np.linalg.norm(stored - new)
    return distance < threshold
