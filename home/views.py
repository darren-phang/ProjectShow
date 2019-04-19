import json
import os
import re
from json import dumps

from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from home.models import LinkGameRanking
from home.serializers import LinkGameRankingSerializer
from timetable.forms import AdaptationForm
from timetable.models import CoursesHtml, Donate, ColorTheme
from timetable.serializers import PostSerializer, PostSerializer2, DonateSerializer, \
    ColorThemeSerializer, ColorThemePostSerializer


def index(request):
    return render(request, 'home/index.html')


def adaptation_form(request):
    if request.method == "POST":
        adaptation_form = AdaptationForm(request.POST)
        if request.POST['school'] == "adaptedschool":
            adaptations = CoursesHtml.objects.all()
            all = request.POST['html'].split(", ")
            # resp = str(len(all)) + "\n"
            edit = 0
            for a in adaptations:
                if str(a.id) in all:
                    a.adapted = True
                    a.save()
                    edit += 1
                    # resp += str(a.id) + a.school + "\n"
            return HttpResponse("upload:" + str(len(all)) + " endied" + str(edit));
        elif adaptation_form.is_valid():
            adaptation_form.save()
            return HttpResponse("Succeed.")
        else:
            return HttpResponse("Sorry, something went wrong.")
    else:
        adaptation_form = AdaptationForm()
        return render(request, "adaptation_form.html",
                      {"form": adaptation_form})


def has_permission(ip):
    if ip != '66.42.35.209' and '157.61.153' not in ip \
            and '222.210.2' not in ip and ip != '101.206.1' and ip != '127.0.0.1':
        return False
    else:
        return True


def adaptlistapi(request):
    ip = request.META.get('REMOTE_ADDR')
    if has_permission(ip) is not True:
        return JsonResponse({"Error": "You are not allow to visit this page." + ip}, status=400)

    id = request.GET.get('id', "-1")
    if id != "-1":
        adaptations = CoursesHtml.objects.raw(
            'SELECT * FROM `timetable_courseshtml` WHERE id=' + id + ';')
    else:
        adaptations = CoursesHtml.objects.raw(
            'SELECT * FROM `timetable_courseshtml` WHERE deleted=0 AND valid=1 ORDER BY convert (school using GBK);')

    cnt = request.GET.get('cnt', '5')
    school = request.GET.get('school', "NULL")
    i = 0
    content = []
    for one in adaptations:
        if i >= int(cnt):
            break
        elif school != "NULL" and one.school != school:
            continue

        d = dict()
        d['id'] = one.id
        d['school'] = one.school
        d['contact'] = one.contact
        d['html'] = one.html
        d['eas'] = one.eas
        content.append(d)
        i += 1

    return HttpResponse(dumps(content, ensure_ascii=False),
                        content_type="application/json")


def adaptidlistapi(request):
    ip = request.META.get('REMOTE_ADDR')
    if has_permission(ip) is not True:
        return JsonResponse({"Error": "You are not allow to visit this page." + ip}, status=400)

    school = request.GET.get('school', "NULL")
    # adaptations = CoursesHtml.objects.raw(
    #     'SELECT * FROM `timetable_courseshtml` WHERE deleted=0 AND adapted=1 AND eas="正方";')
    adaptations = CoursesHtml.objects.filter(deleted=0, valid=1, eas="正方")
    # adaptations = CoursesHtml.objects.raw(
    #     'SELECT * FROM `timetable_courseshtml` WHERE deleted=0 AND valid=1 AND school=\"' + str(
    #         school) + '\";')
    id = ""
    for a in adaptations:
        id += str(a.id) + ","
    return HttpResponse(id)


def adaptation_list(request):
    ip = request.META.get('REMOTE_ADDR')
    # if has_permission(ip) is not True:
    if True:
        return JsonResponse({"Error": "You are not allow to visit this page." + ip}, status=400)

    # adaptations = CoursesHtml.objects.raw(
    #     'SELECT * FROM `timetable_courseshtml` WHERE deleted=0 ORDER BY `read`,`adapted`,`valid` desc,`type`;')

    total = 0
    total_valid = 0
    last = ''

    adaptations = CoursesHtml.objects.raw(
        'SELECT * FROM `timetable_courseshtml` WHERE deleted=0 AND `valid`=1 order by convert (school using GBK);')

    # adaptations = CoursesHtml.objects.raw(
    #     'SELECT * FROM `timetable_courseshtml` WHERE deleted=0 ORDER BY `read`,`adapted`,`valid` desc,convert (eas using GBK) desc,convert (school using GBK);')

    for a in adaptations:
        total += 1
        if a.valid and a.school != last and a.adapted == 0:
            total_valid += 1
        last = a.school

        # if "正方软件股份有限公司" in a.html or "正方教务管理系统" in a.html:
        #     a.eas = '正方'
        # elif '湖南强智科技发展有限公司' in a.html:
        #     a.eas = '强智'
        # else:
        #     a.eas = 'Unkown'
        # a.save()

    return render(request, "adaptation_list.html",
                  {"adaptations": adaptations, "total_valid": total_valid, "total": total})


def adaptation_detail(request, id):
    if has_permission(request.META.get('REMOTE_ADDR')) is not True:
        return JsonResponse({"Error": "You are not allow to visit this page."}, status=400)

    adaptation = get_object_or_404(CoursesHtml, id=id)
    adaptation.read = True
    adaptation.save()
    return render(request, "adaptation_detail.html",
                  {"adaptation": adaptation})


def adapted(request, id):
    if has_permission(request.META.get('REMOTE_ADDR')) is not True:
        return JsonResponse({"Error": "You are not allow to visit this page."}, status=400)
    if request.GET['origin'] == "True":
        new = False
    else:
        new = True
    adaptation = get_object_or_404(CoursesHtml, id=id)
    adaptation.adapted = new
    adaptation.read = True
    adaptation.save()
    return HttpResponseRedirect("/adaptationList?pw=strivexjj123")
    # return HttpResponse("Succeed.")


def valid(request, id):
    if has_permission(request.META.get('REMOTE_ADDR')) is not True:
        return JsonResponse({"Error": "You are not allow to visit this page."}, status=400)
    if request.GET['origin'] == "True":
        new = False
    else:
        new = True
    adaptation = get_object_or_404(CoursesHtml, id=id)
    adaptation.valid = new
    adaptation.read = True
    adaptation.save()
    # return HttpResponseRedirect("/adaptationList?pw=strivexjj123")
    return HttpResponse("Succeed.")


def delete(request, id):
    if has_permission(request.META.get('REMOTE_ADDR')) is not True:
        return JsonResponse({"Error": "You are not allow to visit this page."}, status=400)
    adaptation = get_object_or_404(CoursesHtml, id=id)
    adaptation.deleted = True
    adaptation.save()
    return HttpResponseRedirect("/adaptationList?pw=strivexjj123")
    # return HttpResponseRedirect(reverse("home:adaptation_list", args={'pw': 'strivexjj123'}))


@csrf_exempt
def adaptationapi(request):
    if request.method == 'GET':
        adaptations = CoursesHtml.objects.raw(
            'SELECT id,school, COUNT(*) as schoolCount,'
            'COUNT(IF(valid=1,true,null)) as validCount,COUNT(IF(adapted=1,true,null)) as adaptedCount '
            'FROM timetable_courseshtml  WHERE deleted=0 GROUP by school;')

        contents = []
        for one in adaptations:
            content = dict()
            content['school'] = one.school
            content['schoolCount'] = one.schoolCount
            content['validCount'] = one.validCount
            content['adaptedCount'] = one.adaptedCount
            contents.append(content)

        # return JsonResponse(dumps(contents, ensure_ascii=False), safe=False)
        return HttpResponse(dumps(contents, ensure_ascii=False), content_type="application/json")
        # serializer = AdaptationApiSerializer(adaptation, many=True)
        # return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def list(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        return JsonResponse({"code": 400}, status=400)
        # snippets = CoursesHtml.objects.all()
        # serializer = PostSerializer(snippets, many=True)
        # return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = {}
        data['school'] = request.POST['school']
        data['type'] = request.POST['type']
        data['html'] = request.POST['html']
        data['url'] = request.POST['url']
        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"code": 201}, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def requestAdaptation(request):
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        return JsonResponse({"code": 400}, status=400)
        # snippets = CoursesHtml.objects.all()
        # serializer = PostSerializer(snippets, many=True)
        # return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = {}
        data['school'] = request.POST['school']
        data['type'] = request.POST['type']
        data['html'] = request.POST['html']
        data['url'] = request.POST['url']
        data['contact'] = request.POST['contact']
        serializer = PostSerializer2(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"code": 201}, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def donate(request):
    if request.method == 'GET':
        donates = Donate.objects.all()
        serializer = DonateSerializer(donates, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        if has_permission(request.META.get('REMOTE_ADDR')) is not True:
            return JsonResponse({"Error": "You are not allow to visit this page."}, status=400)

        data = dict()
        data['name'] = request.POST['name']
        data['money'] = request.POST['money']

        serializer = DonateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"code": 201}, status=201)
        return JsonResponse(serializer.errors, status=400)


@csrf_exempt
def color_theme(request):
    if request.method == 'GET':
        color_theme = ColorTheme.objects.all()
        serializer = ColorThemeSerializer(color_theme, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = dict()
        data['username'] = request.POST['username']
        data['description'] = request.POST['description']
        data['config'] = request.POST['config']
        serializer = ColorThemePostSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"code": 201}, status=201)
        return JsonResponse(serializer.errors, status=400)


def color_theme_function(request):
    id = int(request.GET.get('id', '-1'))
    if id == -1:
        return JsonResponse({"code": 400}, status=400)
    color = get_object_or_404(ColorTheme, id=id)

    like = int(request.GET.get('like', '0'))

    if like != -1:
        if color.like + 1 >= color.download:
            return JsonResponse({"code": 201}, status=201)
        color.like = color.like + 1
        color.save()
        return JsonResponse({"code": 201}, status=201)
    else:
        color.download = color.download + 1
        color.save()
        return HttpResponse(color.config)


def getColor(request):
    color_theme = ColorTheme.objects.all()
    un=[]
    re=''
    for one in color_theme:
        s=one.username+one.config
        if s in un:
            re+=one.username+"<br>"
            one.delete()
        else:
            un.append(s)
            one.precolor = json.loads(one.config)['courseColor'];
            one.save()
        # one.update(precolor=json.loads(one.config)['courseColor'])
        # s += json.loads(one.config)['courseColor']+'\n'
    return JsonResponse({"code": re+" success~!"}, status=201)


def validateEmail(email):
    if len(email) > 7:
        if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",
                    email) != None:
            return 1
    return 0


def sendEmail(request):
    ip = request.META.get('REMOTE_ADDR')
    if has_permission(ip) is not True:
        return JsonResponse({"Error": "You are not allow to visit this page."}, status=400)

    school = CoursesHtml.objects.filter(adapted=True, notified=False)

    email = []
    person = []
    for a in school:
        if a.contact is not None and validateEmail(a.contact):
            email.append(a.contact)
            person.append(a)
    if len(email) == 0:
        return HttpResponse("Null")

    res = ""
    for a in person:
        res += a.contact + "<br>"
    # send_mail(
    #     subject=u"课程表适配成功", message=u"课程表已成功适配你们学校，目前只上传了应用宝，"
    #                                 u"下载地址 https://sj.qq.com/myapp/detail.htm?apkName=com.strivexj.timetable\n如果导课有问题请尽快联系我。没问题的话可以推荐给同学哦，多谢支持～\n\n"
    #                                 u"注意事项：先在导课列表找自己学校，如果没有且是正方/强智系统再选正方/强智。 教务处登录界面下方写了“正方软件股份有限公司”或“湖南强智科技发展有限公司”就是正方/强智系统。",
    #     from_email='strivexj@gmail.com', recipient_list=email,
    #     fail_silently=False
    # )
    # for a in person:
    #     a.notified = True
    #     a.save()

    return HttpResponse(res)


def v2ray(request):
    code = request.GET['op']
    if code is None:
        return JsonResponse({"code": 400}, status=400)
    if code == 'restart':
        s = os.popen("v2ray restart").readlines()
        return JsonResponse({"code": s}, status=201)
    if code == 'start':
        s = os.popen("v2ray start").readlines()
        # sss = ''
        # for ss in s:
        #     sss += ss.decode("gbk").encode("utf-8")
        # return HttpResponse(sss)
        return JsonResponse({"code": s}, status=201)
    if code == 'status':
        s = os.popen("v2ray status").readlines()
        return JsonResponse({"code": s}, status=201)


@csrf_exempt
def linkGameRanking(request):
    max = 9
    """
    List all code snippets, or create a new snippet.
    """
    if request.method == 'GET':
        rankings = LinkGameRanking.objects.all()
        serializer = LinkGameRankingSerializer(rankings, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':

        data = dict()
        data['username'] = request.POST['username']
        data['type'] = request.POST['type']
        data['record'] = request.POST['record']
        data['date'] = request.POST['date']

        rankings = LinkGameRanking.objects.filter(type=data['type'])
        if len(rankings) > max and int(data['record']) >= rankings[len(rankings) - 1].record:
            return JsonResponse({"code": 201}, status=201)

        if len(rankings) > max:
            rankings[len(rankings) - 1].delete()

        try:
            aRecord = LinkGameRanking.objects.get(username=data['username'], type=data['type'])
        except:
            aRecord = None

        serializer = LinkGameRankingSerializer(data=data)
        if serializer.is_valid():
            if aRecord is not None:
                if aRecord.record > int(data['record']):
                    aRecord.delete()
                else:
                    return JsonResponse({"code": 201}, status=201)
            serializer.save()
            return JsonResponse({"code": 201}, status=201)
        return JsonResponse(serializer.errors, status=400)


def timetable(request):
    content = {}
    content["appname"] = 'Timetable'
    content["version"] = 23335
    content["title"] = '新版本V2.33.35'
    content["force"] = 139
    content["type"] = 0
    content["alipay"] = """563049812"""
    content["positiveButtonText"] = "下载"
    content["updateurl"] = 'https://sj.qq.com/myapp/detail.htm?apkName=com.strivexj.timetable'
    content[
        "upgradeinfo"] = """        优化分享功能。
        适配使用正方/强智系统的两百多所大学以及四川大学，山东大学，青岛农业大学，安徽财经大学，哈尔滨工程大学等大学（详情请看应用内适配列表）。
        修复插件空白。
        新增颜色主题，可以下载上传自己的配色，也能下载别人上传的。"""

    return HttpResponse(dumps(content, ensure_ascii=False), content_type="application/json")


def list_path(path):
    file_list = []
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            list_path(file_path)
        else:
            file_list.append(file_path)
    return file_list


def tv_series_list(request):
    base = "/home/wwwroot/www.strivexj.com/myfiles/tvseries"
    mlist = []

    tv = {
        "id": 1,
        "tvName": "friends",
        "en": "Friends",
        'zh': "老友记",
        'src': "https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2187822907.webp",
        'resource': os.path.join(base, "friends.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 2,
        "tvName": "agentsofshield",
        "en": "Agents of S.H.I.E.L.D.",
        'zh': "神盾局特工",
        'src': "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2505133194.webp",
        'resource': os.path.join(base, "agentsofshield.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 3,
        "tvName": "thebigbangtheory",
        "en": "The Big Bang Theory",
        'zh': "生活大爆炸",
        'src': "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2499638425.webp",
        'resource': os.path.join(base, "thebigbangtheory.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 4,
        "tvName": "sherlock",
        "en": "Sherlock",
        'zh': "神探夏洛克",
        "src": "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2412027382.webp",
        'resource': os.path.join(base, "sherlock.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 5,
        "tvName": "brokegirls",
        "en": "Broke Girls",
        'zh': "破产姐妹",
        "src": "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2426595773.webp",
        'resource': os.path.join(base, "brokegirls.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 6,
        "tvName": "desperatehousewives",
        "en": "Desperate Housewives",
        'zh': "绝望主妇",
        "src": "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p1208078100.webp",
        'resource': os.path.join(base, "desperatehousewives.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 7,
        "tvName": "gameofthrones",
        "en": "Game of Thrones",
        'zh': "权力的游戏",
        "src": "https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2462245619.webp",
        'resource': os.path.join(base, "gameofthrones.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 8,
        "tvName": "siliconvalley",
        "en": "Silicon Valley",
        'zh': "硅谷",
        "src": "https://img3.doubanio.com/view/photo/s_ratio_poster/public/p2172371194.webp",
        'resource': os.path.join(base, "siliconvalley.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 9,
        "tvName": "modernfamily",
        "en": "Modern Family",
        'zh': "摩登家庭",
        "src": "https://img1.doubanio.com/view/photo/s_ratio_poster/public/p2376089099.webp",
        'resource': os.path.join(base, "modernfamily.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 999,
        "tvName": "all",
        "en": "All",
        'zh': "全部词汇",
        "src": "https://strivexj.com/myfiles/all_glossarys.jpg",
        'resource': os.path.join(base, "modernfamily.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 10,
        "tvName": "wordfrequencylist",
        "en": "Word Frequency List",
        'zh': "Word Frequency List",
        "src": "https://strivexj.com/myfiles/p.jpg",
        'resource': os.path.join(base, "modernfamily.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 11,
        "tvName": "dict",
        "en": "Dict",
        'zh': "Dict",
        "src": "https://strivexj.com/myfiles/p.jpg",
        'resource': os.path.join(base, "modernfamily.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 12,
        "tvName": "ieltslistening",
        "en": "IELTS Listening",
        'zh': "雅思听力",
        "src": "https://strivexj.com/myfiles/p.jpg",
        'resource': os.path.join(base, "ieltslistening.json"),
        "description": ""
    }
    mlist.append(tv)
    tv = {
        "id": 13,
        "tvName": "weixiaolv",
        "en": "Merriam Webster's Vocabulary Builder",
        'zh': "韦小绿",
        "src": "https://img3.doubanio.com/view/subject/r/public/s4339900.jpg",
        'resource': os.path.join(base, "weixiaolv.json"),
        "description": ""
    }
    mlist.append(tv)

    tv = {
        "id": 14,
        "tvName": "wordpowermadeeasy",
        "en": "Word Power Made Easy",
        'zh': "Word Power Made Easy",
        "src": "https://img3.doubanio.com/view/subject/r/public/s6525336.jpg",
        'resource': os.path.join(base, "wordpowermadeeasy.json"),
        "description": ""
    }
    mlist.append(tv)

    return HttpResponse(dumps(mlist, ensure_ascii=False),

                        content_type="application/json")
