from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404

# Create your views here.
from .models import ProjectPost
from project.models import Inception
import project.client as client
import os
import json


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
                   "total_pages": list(range(1, int(ProjectPost.objects.count() / 6 + 2)))})


def project_show_page(request, id, type):
    project = get_object_or_404(ProjectPost, id=id)
    if request.method == 'POST':
        new_img = Inception(
            img=request.FILES.get('img'),
            name=request.FILES.get('img').name,
        )
        new_img.save()
        img_id = new_img.id
        obj = Inception.objects.get(id=img_id)
        img_dir = obj.img
        dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        api = client.ClientAPI(host=project.address, port=project.port)

    if type == 'classification':
        if request.method == 'POST':
            result = api.send_request(
                os.path.join(dir_path, 'media', str(img_dir)), project.model_name,
                project.signature_name, project.input_tensor_name)
            label_and_percentage = api.classification_result(result)
            label_and_percentage_str = json.dumps(label_and_percentage)
            obj.predict = label_and_percentage_str
            obj.save()
            content = {
                'img_dir': str(result['abs_img_dir']),
                'predict': json.loads(label_and_percentage_str)
            }
        else:
            content = {
                'img_dir': 'image/default_image_for_inception.jpeg',
                'predict': {}
            }
        return render(request, 'project/project_classification.html', content)

    if type == 'detection':
        if request.method == 'POST':
            other_k = {}
            if project.model_name == 'face':
                other_k['min_face_size_input:float'] = 18
            result = api.send_request(
                os.path.join(dir_path, 'media', str(img_dir)), project.model_name,
                project.signature_name, project.input_tensor_name, other_k=other_k,
                restore=False)
            api.detection_result_face(result)
            content = {
                'img_dir': str(result['abs_img_dir']),
            }
        else:
            content = {
                'img_dir': 'image/default_image_for_inception.jpeg',
            }
        return render(request, 'project/project_detection.html', content)

    if type == 'APP':
        pass
