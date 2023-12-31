import sys
import requests
import cv2
import os
import subprocess
from keras_facenet import FaceNet

import numpy as np

embedder = FaceNet()

# Connection to SurrealDB
session = requests.Session()
session.auth = ('ann', 'ann')
headers={
    "NS": 'ann',
    "DB": 'ann',
    "Accept": "application/json",
}
session.headers.update(headers)

def index_photos():
    surreal_ql(f"REMOVE TABLE photos;")
    for filename in os.listdir('photos'):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            filepath = os.path.join('photos', filename)
            embedding = extract_features(filepath)
            if embedding is not None:
                print(f"Index {filename}")
                surreal_ql(f"CREATE photos SET r={embedding.tolist()}, path=\"{filename}\";")
            else:
                print(f"Ignore {filename}")


def find_largest_face(detections):
    if not detections:
        return None
    largest_area = 0
    largest_detection = None
    for detection in detections:
        box = detection['box']
        area = box[2] * box[3]  # width * height
        if area > largest_area:
            largest_area = area
            largest_detection = detection
    return largest_detection

def extract_features(filepath):
    image = cv2.imread(filepath)
    detections = embedder.extract(image, threshold=0.95)
    largest = find_largest_face(detections)
    if largest:
        return largest['embedding']

def surreal_ql(q):
    # print(q)
    r = session.post('http://127.0.0.1:8000/sql', q)
    if r.status_code != 200:
        raise RuntimeError(f"{r.text}")
    return r.json()   

def search_photo(filepath):
    subprocess.run(['open', filepath])
    embedding = extract_features(filepath)
    if embedding is None:
        print("No face found")
        return
    res = surreal_ql(f"SELECT path FROM photos WHERE r <1,EUCLIDEAN> {embedding.tolist()};")
    for item in res[0]['result']:
        filename = os.path.join('photos', item['path'])
        subprocess.run(['open', filename])

if __name__ == "__main__":
    n = len(sys.argv)
    if n > 2:
        print("Usage: python knn_demo.py path/to/image.jpg")
        sys.exit(1)
    elif n == 1:
        index_photos()
    elif n == 2:
        search_photo(sys.argv[1])
    
