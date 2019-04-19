from django.urls import path, include

urlpatterns = [
    path('', include(('home.urls', 'home'), namespace='home')),
]
