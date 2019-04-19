from json import dumps

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from timetable.models import CoursesHtml
from timetable.serializers import PostSerializer








