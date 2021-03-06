from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404,\
    HttpResponse, HttpResponseRedirect, render_to_response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.functional import SimpleLazyObject
from memory_profiler import profile
import json
import os

import project.client as client
from project.models import Inception, FaceVector
# Create your views here.
from .models import ProjectPost
import project.facenet.tools as tools
import scipy.misc as misc
import numpy as np


def index(request):
    project_list = ProjectPost.objects.exclude(type="Other")
    paginator = Paginator(project_list, 6)
    page = request.GET.get('page')
    if page is None:
        page = 1
    try:
        project_page = paginator.page(page)
        project = project_page.object_list
    except PageNotAnInteger:
        project_page = paginator.page(1)
        project = project_page.object_list
    except EmptyPage:
        project_page = paginator.page(paginator.num_pages)
        project = project_page.object_list
    return render(request, "project/project.html",
                  {"projects": project, "page": project_page,
                   "total_pages": get_range(page)
                   })


@csrf_exempt
def project_show_page(request, id, type):
    if id == 5:
        return HttpResponseRedirect('http://a.vmall.com/uowap/index.html#/detailApp/C100279569')
    elif id == 4:
        return HttpResponseRedirect('http://v.qq.com/x/page/b0657jz3rjl.html')

    if type == 'classification':
        return render(request, 'project/project_classification.html')

    if type == 'detection':
        return render(request, 'project/project_detection.html')

    if type == 'APP':
        pass


@csrf_exempt
def get_response_classification(request, id):
    if request.method != "POST":
        return
    project = get_object_or_404(ProjectPost, id=id)
    dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    new_img = Inception(
        img=request.FILES.get('img'),
        name=request.FILES.get('img').name,
    )
    new_img.save()
    img_id = new_img.id
    obj = Inception.objects.get(id=img_id)
    img_dir = obj.img
    abs_image_dir = client.change_image_path(os.path.join(dir_path, 'media', 'image'),
                                             str(img_dir).split('/')[-1], str(id))
    api = client.ClientAPI(host=project.address, port=project.port)
    result = api.send_request(
        abs_image_dir, project.model_name,
        project.signature_name, project.input_tensor_name, _id=str(id))
    label_and_percentage = api.classification_result(result)
    label_and_percentage_str = json.dumps(label_and_percentage)
    obj.predict = label_and_percentage_str
    obj.save()
    content = {
        'img_dir': str(result['abs_img_dir']),
        'predict': json.loads(label_and_percentage_str)
    }
    print("\n--classification--" + os.path.join(dir_path, 'media', content['img_dir']) + "\n")
    return JsonResponse(label_and_percentage)


@csrf_exempt
def get_response_detection(request, id):
    if request.method != "POST":
        return
    project = get_object_or_404(ProjectPost, id=id)
    dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    new_img = Inception(
        img=request.FILES.get('img'),
        name=request.FILES.get('img').name,
    )
    new_img.save()
    img_id = new_img.id
    obj = Inception.objects.get(id=img_id)
    img_dir = obj.img
    abs_image_dir = client.change_image_path(os.path.join(dir_path, 'media', 'image'),
                                             str(img_dir).split('/')[-1], str(id))
    api = client.ClientAPI(host=project.address, port=project.port)

    result = api.send_request(
        abs_image_dir, project.model_name,
        project.signature_name, project.input_tensor_name, _id=str(id))
    if project.model_name == 'face':
        # api.detection_result_face(result)
        detection_response = api.detection_result_face(result)
        face_match = get_response_facenet(result['abs_img_dir'],
                                          detection_response["bboxes"], request.user)
        detection_response['face_match'] = face_match
    elif project.model_name == 'ssd':
        detection_response = api.detection_result_ssd(result)
    return JsonResponse(detection_response)


def get_response_facenet(abs_img_dir, bboxes, user_id):
    dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    face_image_dir = os.path.join(dir_path, 'media', 'image', 'face')
    client.check_dir(face_image_dir)
    image_name = abs_img_dir.split("/")[-1].split(".")[0]
    img_dir = os.path.join(dir_path, 'media', abs_img_dir)

    project = get_object_or_404(ProjectPost, id=6)
    api = client.ClientAPI(host=project.address, port=project.port)
    img = misc.imread(os.path.expanduser(img_dir), mode='RGB')
    img_size = np.asarray(img.shape)[0:2]
    embedding_list = []
    img_face_list = []
    match_face_dict = {}
    for i, bboxe in enumerate(bboxes):
        img_face = tools.clip_image(img, bboxe, img_size)
        embedding = tools.get_face_embedding(img_face, project, api)
        match_face, store = tools.get_face_vector(embedding, i)
        if len(match_face) != 0 and match_face[0].face_name != '':
            match_face_dict[i] = match_face[0].to_string()
        if store:
            embedding_list.append(embedding)
            img_face_list.append(img_face)
        else:
            embedding_list.append(False)
            img_face_list.append(False)
    for i in range(len(img_face_list)):
        image_url = "%s_noOne_%s.jpg" % (image_name, i)
        if img_face_list[i] is not False:
            misc.imsave(os.path.join(face_image_dir, image_url), img_face_list[i])
            if i in list(match_face_dict.keys()):
                name = match_face_dict[i]['face_name']
            else:
                name = None
            tools.save_vector(embedding_list[i], user_id, os.path.join('face', image_url), face_name=name)
    for i in list(match_face_dict.keys()):
        print("%s_noOne_%s.jpg" % (image_name, i), end=' ')
        print(match_face_dict[i]['face_name'])
    return match_face_dict


def face(request):
    face_list = FaceVector.objects.filter()
    paginator = Paginator(face_list, 6)
    page = request.GET.get('page')
    if page is None:
        page = 1
    try:
        project_page = paginator.page(page)
        project = project_page.object_list
    except PageNotAnInteger:
        project_page = paginator.page(1)
        project = project_page.object_list
    except EmptyPage:
        project_page = paginator.page(paginator.num_pages)
        project = project_page.object_list

    return render(request, 'project/face.html',
                  {"faces": project, "page": project_page,
                   "total_pages": get_range(page)}
                  )


@csrf_exempt
def change_name(request):
    if request.method == "POST":
        face_name = request.POST['face_name']
        image_name = request.POST['image_name']
        face = FaceVector.objects.get(image_url=image_name)
        face.face_name = face_name
        face.save()
        return HttpResponse("succeed")
    else:
        return HttpResponse("loss")


@csrf_exempt
def delete_face(request):
    if request.method == "POST":
        image_name = request.POST['image_name']
        FaceVector.objects.filter(image_url=image_name).delete()
        return HttpResponse("succeed")
    else:
        return HttpResponse("loss")


def get_range(page):
    # start = int(page)
    start = max(int(page) - 2, 1)
    end = min(int(FaceVector.objects.count() / 6 + 1), start + 6)
    if end - start != 6:
        start = max(0, end - 6)
    return list(range(start, end))
