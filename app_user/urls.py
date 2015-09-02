__author__ = 'moon'
from django.conf.urls import patterns, include, url

urlpatterns = patterns('app_user.views',
    #signnup
    url(r'signup/$', 'signup', name='v2_signup'),
    url(r'signup/confirm/(?P<key>[\w.@+-]+)/$', 'signup_confirm', name="v2_email_confirm"),
    url(r'send_confirm/$', 'send_confirm', name='v2_send_confirm'),
    url(r'signup/host/$', 'host_signup', name='v2_host_signup'),


    url(r'reset_password/$', 'pw_reset_request', name="v2_reset_request"),
    url(r'reset_process/(?P<key>[\w.@+-]+)/$', 'pw_reset_process', name='pw_reset_process_get'),
    url(r'reset_process/$', 'pw_reset_process', name='pw_reset_process_post'),


    url(r'login/$', 'login', name='v2_login'),
    url(r'logout/$','logout', {'next_page':'/'},name='v2_logout'),

    url(r'edit_prof/(?P<user_num>[0-9]+)/$', 'T2W_edit_prof', name='v2_edit_prof'),
    url(r'profile/(?P<user_num>[0-9]+)/$', 'T2W_public_prof', name='v2_public_prof'),

    #test
    url(r'^test_lg/$', 'testlogin', name='testlogin'),
    url(r'^ajax/test_sg/$', 'ajax_signup_view', name='ajaxsignup'),
    url(r'^ajax/line_state/$', 'lineup_test', name='lineup_test'),
    url(r'^pay_test/$', 'pay_test', name='pay_test')
    )