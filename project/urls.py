"""ProjectShow URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
import project.views as view

urlpatterns = [
    path('', view.index, name='project_home'),
    path('project_show/<int:id>/<str:type>/', view.project_show_page,
         name='project_show'),
    path('classification/<int:id>/', view.get_response_classification,
         name='classification'),
    path('detection/<int:id>/', view.get_response_detection,
         name='detection'),
    path('face/', view.face,
         name='face'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
