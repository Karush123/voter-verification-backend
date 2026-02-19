import numpy as np
import json
from keras_facenet import FaceNet

embedder = FaceNet()

def get_face_embedding(image_array):
    embedding = embedder.embeddings([image_array])[0]
    return embedding.tolist()

def compare_faces(stored_embedding, live_embedding, threshold=0.7):

    # Convert JSON string back to list if needed
    if isinstance(stored_embedding, str):
        stored_embedding = json.loads(stored_embedding)

    if isinstance(live_embedding, str):
        live_embedding = json.loads(live_embedding)

    distance = np.linalg.norm(
        np.array(stored_embedding) - np.array(live_embedding)
    )

    return distance < threshold
