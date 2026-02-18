import numpy as np
from keras_facenet import FaceNet

embedder = FaceNet()

def get_face_embedding(image_array):
    embedding = embedder.embeddings([image_array])[0]
    return embedding.tolist()

def compare_faces(embedding1, embedding2, threshold=0.7):
    distance = np.linalg.norm(
        np.array(embedding1) - np.array(embedding2)
    )
    return distance < threshold
