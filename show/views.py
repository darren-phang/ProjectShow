from django.shortcuts import render
from show.models import Inception
import show.client as client
import os
import json
# Create your views here.


def index(request):
    return render(request, 'show/show.html')


def inception_v4_in_image_net(request):
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
        api = client.RockApi()
        label_and_percentage, adj_img_dir = api.send_request(
            os.path.join(dir_path, 'media', str(img_dir)))
        print(label_and_percentage)
        label_and_percentage_str = json.dumps(label_and_percentage)
        obj.predict = label_and_percentage_str
        obj.save()
        content = {
            # 'img_dir': str(img_dir),
            'img_dir': str(adj_img_dir),
            'predict': json.loads(label_and_percentage_str)
        }
        return render(request, 'show/image_net_inception_v4.html', content)
    content = {
        'img_dir': 'image/default_image_for_inception.jpeg',
        'predict': {}
    }
    return render(request, 'show/image_net_inception_v4.html', content)
