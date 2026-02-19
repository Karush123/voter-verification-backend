import numpy as np
from keras_facenet import FaceNet
import json

embedder = FaceNet()

def get_face_embedding(image_array):
    embedding = embedder.embeddings([image_array])[0]
    return embedding.tolist()

def compare_faces(embedding1, embedding2, threshold=0.7):
    if isinstance(embedding1, str):
        embedding1 = json.loads(embedding1)

    if isinstance(embedding2, str):
        embedding2 = json.loads(embedding2)

    distance = np.linalg.norm(
        np.array(embedding1) - np.array(embedding2)
    )
    return distance < threshold
