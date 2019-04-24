from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os

import project.client as client
from project.models import Inception
# Create your views here.
from .models import ProjectPost


def index(request):
    project_list = ProjectPost.objects.filter()
    paginator = Paginator(project_list, 6)
    page = request.GET.get('page')
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
                   "total_pages": list(range(1, int(ProjectPost.objects.count() / 6 + 2))),
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
    other_k = {}
    if project.model_name == 'face':
        other_k['min_face_size_input:float'] = 18
    result = api.send_request(
        abs_image_dir, project.model_name,
        project.signature_name, project.input_tensor_name,
        other_k=other_k, _id=str(id))
    if project.model_name == 'face':
        # api.detection_result_face(result)
        detection_response = api.detection_result_face(result)
    elif project.model_name == 'ssd':
        detection_response = api.detection_result_ssd(result)
    return JsonResponse(detection_response)
