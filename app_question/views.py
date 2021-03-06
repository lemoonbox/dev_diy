#coding: utf-8
from django.shortcuts import render

from django.shortcuts import \
    loader,\
    render
from django.contrib.auth.decorators import \
    login_required, \
    permission_required
from django.contrib.auth.models import \
    User
from django.http import \
    HttpResponseRedirect,\
    HttpResponse, \
    Http404

from app_question.form import \
    CreateQItem, \
    CreateQSkill
from app_comminfo.models import Category, State
from app_question.models import QItem, QPic, QSkill
from app_board.models import Questionbox


from DIY_tool import template_match as TEMP
import logging
logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def create_q_item(request):

    error = False

    if request.method == "GET":
        create_qform = CreateQItem()

    elif request.method == "POST":
        user = User.objects.get(username=request.user)
        create_qform = CreateQItem(request.POST)
        category= request.POST['category']
        state = request.POST['state']
        photos = request.FILES.getlist("Qphoto", "")


        if len(photos) == 0 :
            create_qform.add_error('qpic', u'최소 한장의 사진이 필요합니다.')
            error = True
        for photo in photos:
            allow_type=('image/jpeg', 'image/png')
            if photo.content_type not in allow_type :
                error = True

        if create_qform.is_valid() and not error:
            _qitempost = create_qform.save(commit=False)
            _qitempost.djgouser=request.user
            _qitempost.save()
            _category=Category.objects.get_or_create(category=category)
            _state = State.objects.get_or_create(state=state)

            _qitempost.category.add(_category[0])
            _qitempost.state.add(_state[0])
            _qitempost.save()

            for photo in photos:
                _qpic = QPic(user=user,qitem=_qitempost,pic=photo)
                _qpic.save()
                _qpic.category.add(_category[0])
                _qpic.save()
            picpic=_qitempost.qpic_set.first().pic
            _qbox = Questionbox(djgouser=user, title =_qitempost.title,
                                mylocal=_qitempost.mylocal, qtype="I",
                                qitempost = _qitempost, weekday=_qitempost.weekday,
                                item_pic=picpic)
            _qbox.save()
            _qbox.category.add(_category[0])
            _qbox.state.add(_state[0])
            _qbox.save()

            HTTP_HOST = request.META['HTTP_HOST']

            return HttpResponseRedirect("/v2/question/next_guid")

    HTTP_HOST = request.META["HTTP_HOST"]
    return render(request, TEMP.V2_CREATE_QITEM,{
        'create_qform':create_qform,
        'HTTP_HOST':HTTP_HOST,

    })


def qitem_detail(request, qitem_num):

    if request.method == "GET":
        try:
            _qitempost = QItem.objects.get(pk=qitem_num)
        except _qitempost.DoesNotExist:
            raise Http404("post does not exist")

    HTTP_HOST = request.META["HTTP_HOST"]
    next = "/v2/question/item/{0}".format(_qitempost.id)
    return render(request, TEMP.V2_DETAIL_QITEM,
        {
            'qitem_post':_qitempost,
            'HTTP_HOST':HTTP_HOST,
            'next':next,
        })


@login_required
def create_q_skill(request):

    error = False

    if request.method == "GET":
        create_qform = CreateQSkill()

    elif request.method == "POST":
        user = User.objects.get(username=request.user)
        create_qform = CreateQSkill(request.POST)
        category= request.POST['category']
        state = request.POST['state']

        print create_qform.is_valid()
        if create_qform.is_valid():
            _qskillpost = create_qform.save(commit=False)
            _qskillpost.djgouser=request.user
            _qskillpost.save()
            _category=Category.objects.get_or_create(category=category)
            _state = State.objects.get_or_create(state=state)
            _qskillpost.category.add(_category[0])
            _qskillpost.state.add(_state[0])
            _qskillpost.save()

            _qbox = Questionbox(djgouser=user, title =_qskillpost.title,
                                mylocal=_qskillpost.mylocal, qtype="S",weekday=_qskillpost.weekday,
                                qskillpost = _qskillpost,skill_class=_qskillpost.wantclass,
                                skill_goal=_qskillpost.wantgoal, skill_edu=_qskillpost.wantedu)
            _qbox.save()
            _qbox.category.add(_category[0])
            _qbox.state.add(_state[0])
            _qbox.save()


            return HttpResponseRedirect("/v2/question/next_guid")

    HTTP_HOST = request.META['HTTP_HOST']
    return render(request, TEMP.V2_CREATE_QSKILL,{
        'create_qform':create_qform,
        'HTTP_HOST':HTTP_HOST,

    })

def qskill_detail(request, qskill_num):

    if request.method == "GET":
        try:
            _qskillpost = QSkill.objects.get(pk=qskill_num)
        except _qskillpost.DoesNotExist:
            raise Http404("post does not exist")

    HTTP_HOST = request.META["HTTP_HOST"]
    next = "/v2/question/skill/{0}".format(_qskillpost.id)
    return render(request, TEMP.V2_DETAIL_QSKILL,
        {
            'qskill_post':_qskillpost,
            'HTTP_HOST':HTTP_HOST,
            'next':next,

        })
def next_guid(request):

    HTTP_HOST = request.META['HTTP_HOST']
    return render(request, TEMP.V2_NEXT_GUIDE,{
        'HTTP_HOST':HTTP_HOST,
        'next':'/',
    })

def T2W_que_bridge(request):
    HTTP_HOST = request.META['HTTP_HOST']
    next ="/v2/question/que_bridge/"
    return render(request, TEMP.V2_QUE_BRIDGE,{
        'HTTP_HOST':HTTP_HOST,
        'next':next,
    })