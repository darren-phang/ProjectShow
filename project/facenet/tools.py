import numpy as np
from project.models import Inception, FaceVector
from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect
from project.models import ProjectPost
import project.client as client
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
import scipy.misc as misc


def get_dist(embeddings_one, embeddings_two):
    dist = np.sqrt(np.sum(np.square(np.subtract(embeddings_one, embeddings_two)), axis=1))
    return dist


def clip_image(img, det, img_size, margin=44):
    bb = np.zeros(4, dtype=np.int32)
    bb[0] = np.maximum(det[0] - margin / 2, 0)
    bb[1] = np.maximum(det[1] - margin / 2, 0)
    bb[2] = np.minimum(det[2] + margin / 2, img_size[1])
    bb[3] = np.minimum(det[3] + margin / 2, img_size[0])
    cropped = img[bb[1]:bb[3], bb[0]:bb[2], :]
    return cropped


def get_face_embedding(img, project, api):
    s = BytesIO()
    misc.imsave(s, img, format='JPEG')
    value = s.getvalue()
    s.close()
    result = api.send_request_by_image(
        value, project.model_name,
        project.signature_name, project.input_tensor_name)
    result = result['result']
    embedding = np.array(result.outputs['embeddings'].float_val)
    return embedding


def save_vector(embedding, user_id, image_url, face_name=None):
    vector = FaceVector(
        vector=embedding,
        face_name='' if face_name is None else face_name,
        user_id=user_id,
        image_url=image_url
    )
    vector.save()


def get_all_vector():
    vectors_array = []
    vectors = FaceVector.objects.filter()
    for vector in vectors:
        vectors_array.append(vector.get_embedding())
    return np.array(vectors_array)


def get_all_dist(embedding):
    vectors_array = get_all_vector()
    if len(vectors_array) > 0:
        dist = get_dist(vectors_array, embedding)
        sort_dist = np.argsort(dist)
        return dist, sort_dist
    return np.array([]), np.array([])


def get_face_vector(embedding, face_ind, top_k=1):
    dist, sort_dist = get_all_dist(embedding)
    if len(np.shape(dist)) == 0:
        dist = np.expand_dims(dist, axis=0)
    if len(np.shape(sort_dist)) == 0:
        sort_dist = np.expand_dims(sort_dist, axis=0)
    match_face = []
    print(dist[sort_dist[0]])
    if sort_dist.size == 0 or dist[sort_dist[0]] > 0.7:
        return [], True
    for i, face in enumerate(FaceVector.objects.filter()):
        for j in sort_dist[:top_k]:
            if i == j:
                match_face.append(face)
                # print(face_ind, face.face_name, face.image_url)
    if dist[sort_dist[0]] <= 0.1:
        return match_face, False
    return match_face, True

