#coding:utf-8
from django.shortcuts import render
from django.template import \
    Context,\
    RequestContext
from django.contrib.auth.models import \
    User
from django.contrib.auth.decorators import \
    login_required
from django.http import \
    HttpResponseRedirect, \
    HttpResponse
from django.shortcuts import \
    loader,\
    render,\
    render_to_response
from django.core.context_processors import \
    csrf
from django.contrib.auth import \
    login as auth_login
from django.contrib.auth.views import \
    logout as django_logout
import os
from django.core.files.images import \
    ImageFile

from DIY_tool import \
    template_match as TEMP
from DIY_tool.settings import \
    LOCAL as SET_LOCAL
from utils import \
    tasks,\
    utils
from app_user.form import \
    UserForm,\
    PwReset_RequestForm, \
    PwReset_ProcessForm,\
    Send_ConfirmForm, \
    Host_Signup, \
    LoginForm
from app_user.models import \
    UserProfile, \
    SignupConfirmKey, \
    PWResetKeys, \
    HostProfile
from DIY_tool import settings

# Create your views here.

def signup(request):
    ctx = Context({
        'error':None
    })
    next=""

    if request.method == "GET":
        userForm = UserForm()
        next=request.GET.get("next", "/")
    else:
        userForm = UserForm(request.POST)

        if userForm.is_valid():
            next=request.POST.get("next","/")

            user_data={
                'username': request.POST.get("username", "null"),
                'email':request.POST.get("username", "null"),
                'first_name': request.POST.get('first_name', "null"),
                'last_name': request.POST.get('last_name', "null"),
                'password': request.POST.get('password', "null"),
            }
            if not "null" in user_data.values():
                _user = User.objects.create_user(**user_data)
                image_file = open(os.path.join(settings.BASE_DIR,
                                               'resource/image/default_prof.png'),'r')
                content = ImageFile(image_file)

                _userprofile = UserProfile(djgouser=_user, propic=content)
                _userprofile.save()

                #send email
                key = utils.generate_key(32,SignupConfirmKey, _userprofile.djgouser)

                host =request.META['HTTP_HOST']
                title = u"안녕하세요! 토마킷입니다. 정식 사용을 승인해주세요."
                sender = "makerecipe@gmail.com"

                if SET_LOCAL:
                   utils.send_key_email(request, title, sender,
                        _user.email, TEMP.V2_CONFIRM_MAIL, key)

                else:
                    tasks.send_key_email.delay(host, title, sender,
                    _user.email, TEMP.V2_CONFIRM_MAIL, key)

                return HttpResponseRedirect("/v2/user/login/?next="+next)
    HTTP_HOST = request.META["HTTP_HOST"]
    return render(request, TEMP.V2_SIGNUP_TEM,{
        'accountform':userForm,
        'next':next,
        'HTTP_HOST':HTTP_HOST,
        })

@login_required
def host_signup(request):
    ctx = Context({
        'error':None
    })

    _hostprofile = HostProfile.objects.filter(djgouser=request.user)

    #if(_hostprofile.exists()):
    #    tpl = loader.get_template(TEMP.V2_HOST_SIGNUP_REJECT)
    #    return HttpResponse(tpl.render(ctx))

    if request.method == "GET":
        hostform = Host_Signup()
        next=request.GET.get("next", "/")


    elif request.method=="POST":
        next=request.POST.get("next","/")
        hostform = Host_Signup(request.POST)
        print request.POST["hosttype"]
        print hostform.data

        if hostform.is_valid():
            _hostprofile = HostProfile(djgouser=request.user, mobile=hostform.cleaned_data['mobile'],
                                       hosttype=hostform.cleaned_data['hosttype'])
            _hostprofile.save()

        return HttpResponseRedirect(next)
    HTTP_HOST = request.META["HTTP_HOST"]
    return render(request, TEMP.V2_HOST_SIGNUP,{
        'hostform':hostform,
        'HTTP_HOST':HTTP_HOST,

    })


def signup_confirm(request, *args, **kwargs):

    HTTP_HOST = request.META["HTTP_HOST"]
    ctx = Context({
        'error':None,
        'HTTP_HOST':HTTP_HOST,

    })
    ctx["host"] = request.META['HTTP_HOST']

    _conkey = SignupConfirmKey.find(kwargs['key'])

    if(_conkey):
        _conkey[0].user.email_confirm= True
        _conkey[0].user.save()
        ctx["message"] = "이메일 인증이 완료 되었습니다. 서비스를 이용해주세요!"
        ctx["error"] = True

        tpl = loader.get_template(TEMP.V2_CONFIRM_RESULT)
        ctx.update(csrf(request))
        return HttpResponse(tpl.render(ctx))


    ctx["message"] = "이메일 인증이 실패 하였습니다. 인증 메일을 다시 보내주세요!"
    ctx["error"] = False
    tpl = loader.get_template(TEMP.V2_CONFIRM_RESULT)
    ctx.update(csrf(request))
    return HttpResponse(tpl.render(ctx))

def send_confirm(request):

    if request.method == "GET":
        send_confirm_form = Send_ConfirmForm()
    elif request.method == "POST":
        print "POST"
        send_confirm_form = Send_ConfirmForm(request.POST)

        if send_confirm_form.is_valid():
            _user = User.objects.filter(username=send_confirm_form.cleaned_data['email'])
            print _user

            if(_user.exists()):
                key = utils.generate_key(32,SignupConfirmKey,_user[0])

                host =request.META['HTTP_HOST']
                title = u"안녕하세요! 토마킷입니다. 정식 사용을 승인해주세요."
                sender = "makerecipe@gmail.com"

                if SET_LOCAL:
                    utils.send_key_email(request, title, sender,
                        _user[0].email, TEMP.V2_CONFIRM_MAIL, key)
                else:
                    tasks.send_key_email.delay(host, title, sender,
                        _user[0].email, TEMP.V2_CONFIRM_MAIL, key)

    HTTP_HOST = request.META["HTTP_HOST"]
    return render(request, TEMP.V2_SEND_CONFIRM, {
        "send_conf_for":send_confirm_form,
        'HTTP_HOST':HTTP_HOST,

    })

def pw_reset_request(request):

    if request.method =="GET":
        pwresetform = PwReset_RequestForm()
    elif request.method =="POST":
        pwresetform = PwReset_RequestForm(request.POST)

        if pwresetform.is_valid():
            _user = User.objects.filter(username=pwresetform.cleaned_data['email'])

            if(_user.exists() and _user[0].has_usable_password()):
                key = utils.generate_key(32,PWResetKeys,_user[0])

                host =request.META['HTTP_HOST']
                title = u"안녕하세요. 토마킷 패스워드 변경 이메일을 보내드려요.."
                sender = "makerecipe@gmail.com"

                if SET_LOCAL:
                    utils.send_key_email(request, title, sender,
                        _user[0].email, TEMP.V2_PW_RESET_EMAIL, key)
                else:
                    tasks.send_key_email.delay(host, title, sender,
                        _user[0].email, TEMP.V2_PW_RESET_EMAIL, key)

    HTTP_HOST = request.META["HTTP_HOST"]
    return render(request, TEMP.V2_PW_RESET, {
        'pwrsetform':pwresetform,
        'HTTP_HOST':HTTP_HOST,

    })

def pw_reset_process(request, key):

    ctx =Context({
        'error':None
    })

    _reset_obj = PWResetKeys.find(key)

    if(_reset_obj == None):
        tpl = loader.get_template(TEMP.V2_PW_RESET_FAIL)
        ctx.update(csrf(request))
        return HttpResponse(tpl.render(ctx))

    if (request.method=="GET"):
        pwresetform = PwReset_ProcessForm()
        return render(request, TEMP.V2_PW_RESET_PROCESS, {
            'pwresetform':pwresetform})

    if (request.method=="POST"):
        pwresetform = PwReset_ProcessForm(request.POST)

        if(not pwresetform.is_valid()):
            HTTP_HOST = request.META["HTTP_HOST"]

            return render(request, TEMP.V2_PW_RESET_PROCESS, {
                'pwresetform':pwresetform,
                'HTTP_HOST':HTTP_HOST,
                })

        _user = _reset_obj.user
        _user.set_password(pwresetform.cleaned_data['password'])
        _user.save()
        return HttpResponseRedirect('/v2/user/login')

    pwreset_process_form = PwReset_ProcessForm()
    HTTP_HOST = request.META["HTTP_HOST"]
    return render(request, TEMP.V2_PW_RESET_PROCESS, {
        'pwrset_process_form':pwreset_process_form,
        'HTTP_HOST':HTTP_HOST,
    })

def login(request, *args, **kwargs):

    next=""

    if request.method=="GET":
        login_form = LoginForm()
        next=request.GET.get("next","/")

    elif request.method=="POST":
        login_form = LoginForm(request.POST)
        next=request.POST.get("next", "/")
        print next
        if login_form.is_valid():
            user = login_form.authenticate(request)
            if user:
                auth_login(request, user)
                return HttpResponseRedirect(next)

    HTTP_HOST = request.META["HTTP_HOST"]
    return render(request, TEMP.V2_LOGIN,
                  {'login_form':login_form,
                   'next':next,
                    'HTTP_HOST':HTTP_HOST,
                   })

def logout(request, *args, **kwargs):
    res = django_logout(request, *args, **kwargs)
    return res

@login_required
def T2W_edit_prof(request, user_num):

    if request.method=="GET":
        _req_user = request.user
        _page_user = User.objects.get(id=user_num)
        HTTP_HOST = request.META["HTTP_HOST"]
        if _req_user == _page_user :
            context={
                "djgouser":_page_user,
                'HTTP_HOST':HTTP_HOST,
            }
            context.update(csrf(request))

            return render_to_response(TEMP.V2_RPO_EDIT,context,
                                      context_instance=RequestContext(request))

    elif request.method=="POST":

        _profile = UserProfile.objects.get(djgouser=request.user)

        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        inter_oneline= request.POST.get('inter_oneline')
        inter_start=request.POST.get('inter_start')
        inter_url=request.POST.get('inter_url', _profile.inter_url)
        pro_pic = request.FILES.get('pro_pic', _profile.propic)
        inter_pic=request.FILES.get('inter_pic', _profile.inter_pic)

        if "=" in inter_url:
            shr_codes= inter_url.split("=")

        else:
            shr_codes=inter_url.split("/")
        shr_code=shr_codes[-1]

        _profile.first_name = first_name
        _profile.last_name = last_name
        _profile.inter_oneline= inter_oneline
        _profile.inter_start=inter_start
        _profile.inter_url=shr_code
        _profile.propic = pro_pic
        _profile.inter_pic=inter_pic
        _profile.save()

        return HttpResponseRedirect("/v2/user/profile/{0}".format(_profile.id))

def T2W_public_prof(request, user_num):

    if request.method=="GET":
        _page_uesr=User.objects.get(id=user_num)
        _req_user = request.user
        _profile = UserProfile.objects.get(djgouser=_page_uesr)

        HTTP_HOST = request.META["HTTP_HOST"]

    return render(request, TEMP.V2_PROF_PUBLIC, {
        'page_user':_page_uesr,
        'req_user':_req_user,
        'profile':_profile,

        'HTTP_HOST':HTTP_HOST,
    })
from app_user.form import TestUserForm as TESTFORM

def testlogin(request):
    if request.method == 'GET':
        form = TESTFORM(request.POST)
        print form.is_valid()
        if form.is_valid():
            return HttpResponseRedirect('/')
    else:
        form = LoginForm()

    return render_to_response('v2_dev_moon/ajax_test.html',
                            {'form':form},
                            context_instance=RequestContext(request))

import json
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def ajax_signup_view(request):
    if request.method == 'GET':
        return render_to_response('v2_dev_moon/ajax_test.html',{},
                            context_instance=RequestContext(request))

    elif request.method =='POST':
        data={}
        print "POST"
        print request.POST
        state = request.POST.get('L_state', 'error')

        if state == 'inline':
            print "inline"
            data['state']="success"
            data['L_state']="unline"
            return HttpResponse(json.dumps(data), 'application/json')

        elif state == 'unline':
            print "unline"
            data['state']="success"
            data['L_state']="inline"
            return HttpResponse(json.dumps(data), 'application/json')

        else:
            data['state']='error'
            data['L_state']="error"
            return HttpResponse(json.dumps(data), 'application/json')

@csrf_exempt
def lineup_test(request):
    if request.method == 'GET':
        return render_to_response('v2_dev_moon/lineup_test.html',{},
                            context_instance=RequestContext(request))
    elif request.method =='POST':
        data={}
        print "POST"
        print request.POST
        state = request.POST.get('L_state', 'error')

        if state == 'inline':
            print "inline"
            data['state']="success"
            data['L_state']="unline"
            return HttpResponse(json.dumps(data), 'application/json')

        elif state == 'unline':
            print "unline"
            data['state']="success"
            data['L_state']="inline"
            return HttpResponse(json.dumps(data), 'application/json')

        else:
            data['state']='error'
            data['L_state']="error"
            return HttpResponse(json.dumps(data), 'application/json')

def pay_test(request):
    if request.method == "GET":
        return render(request, 'v2_dev_moon/payment_test.html', {})