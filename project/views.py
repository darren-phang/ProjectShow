from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, HttpResponse, HttpResponseRedirect
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

    project = get_object_or_404(ProjectPost, id=id)
    dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if request.method == 'POST':
        new_img = Inception(
            img=request.FILES.get('img'),
            name=request.FILES.get('img').name,
        )

        new_img.save()
        img_id = new_img.id
        obj = Inception.objects.get(id=img_id)
        img_dir = obj.img
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
            return HttpResponse(get_change(render(request, 'project/project_classification.html', content).content))
        else:
            content = {
                'img_dir': 'image/default_image_for_inception.jpeg',
                'predict': {}
            }
        print("\n--classification--" + os.path.join(dir_path, 'media', content['img_dir']) + "\n")
        return render(request, 'project/project_classification.html', content)

    if type == 'detection':
        if request.method == 'POST':
            other_k = {}
            if project.model_name == 'face':
                other_k['min_face_size_input:float'] = 18
            result = api.send_request(
                os.path.join(dir_path, 'media', str(img_dir)), project.model_name,
                project.signature_name, project.input_tensor_name, other_k=other_k)
            if project.model_name == 'face':
                api.detection_result_face(result)
            elif project.model_name == 'ssd':
                api.detection_result_ssd(result)
            content = {
                'img_dir': str(result['abs_img_dir']),
                'infos': result['colors']
            }
            return HttpResponse(get_change(render(request, 'project/project_detection.html', content).content))
        else:
            content = {
                'img_dir': 'image/default_image_for_inception.jpeg',
                'infos': {}
            }
        print("\n--detection--" + os.path.join(dir_path, 'media', content['img_dir']) + "\n")
        # os.chmod(os.path.join(dir_path, 'media', content['img_dir']), stat.S_IRWXU|stat.S_IRGRP|stat.S_IROTH)
        #os.popen("chmod 666 " + os.path.join(dir_path, 'media', content['img_dir'])).readlines()
        return render(request, 'project/project_detection.html', content)

    if type == 'APP':
        pass


def get_change(html):
    html = html.decode()
    html_return = html[html.find("<section"):html.find("section>") + 8]
    return html_return
