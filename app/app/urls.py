"""
URL configuration for app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from seminar_base2 import views
from seminar_base2 import api
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    path('seminar', views.SeminarListView.as_view(), name='seminar_list'),
    path(
        'lecture/<uuid:seminar_id>',
        views.LectureListView.as_view(),
        name='lecture_list'
    ),
    path(
        'doc/<uuid:seminar_id>',
        views.DocumentView.as_view(),
        name='document'
    ),
    path('accounts/', include('django.contrib.auth.urls')),
    path(
        'print-list',
        views.PrintListView.as_view(),
        name='print_seminar_list'
    ),
    path(
        'print/<uuid:seminar_id>',
        views.PrintView.as_view(),
        name='print'
    ),
    # Include markdownx URLs
    path('markdownx/', include('markdownx.urls')),
    path(
        'file/<uuid:uuid>',
        views.ProtectFileView.as_view(),
        name='file_view'
    ),
    path('manager', views.ManagerListView.as_view(), name='manager_list'),
    path(
        'manager/<uuid:seminar_id>',
        views.ManagerView.as_view(),
        name='manager_view'
    ),
    path(
        'manager/progress/<uuid:seminar_id>',
        views.ManagerProgressView.as_view(),
        name='manager_progress'
    ),
    path(
        'manager/request/<uuid:seminar_id>',
        views.ManagerRequestView.as_view(),
        name='manager_request'
    ),
    path(
        'api/manager/request_hash/<uuid:seminar_id>',
        api.RequestHashView.as_view(),
        name='api_request_hash'
    ),
    path(
        'api/request/<uuid:seminar_id>',
        api.RequestView.as_view(),
        name='api_request'
    ),
    path(
        'manager/request/reset/<uuid:seminar_id>/<str:username>',
        views.ManagerRequestResetView.as_view(),
        name='api_reset_request'
    ),
    path(
        'manager/request/realtime/<uuid:seminar_id>',
        views.ManagerRequestRealtimeView.as_view(),
        name='manager_request_realtime'
    ),
    path(
            'setting',
            views.SettingView.as_view(),
            name='setting'
        ),
    path(
            'setting/complete',
            views.CompleteView.as_view(),
            name='setting_complete'
        ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    # noqa: E501
