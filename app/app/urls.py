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
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin', admin.site.urls),
    path('', views.IndexView.as_view(), name='index'),
    path('seminar', views.SeminarListView.as_view(), name='seminar_list'),
    path('lecture/<uuid:seminar_id>', views.LectureListView.as_view(), name='lecture_list'),
    path('doc/<uuid:seminar_id>', views.DocumentView.as_view(), name='document'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('print-list', views.PrintListView.as_view(), name='print_seminar_list'),
    path('print/<uuid:seminar_id>', views.PrintView.as_view(), name='print'),
    # path('print/<uuid:seminar_id>/<int:lecture_id>/', views.PrintView.as_view(), name='print_print'),
    # Include markdownx URLs
    path('markdownx/', include('markdownx.urls')),
    path('file/<uuid:uuid>', views.ProtectFileView.as_view(), name='file_view'),
    path('manager', views.ManagerListView.as_view(), name='manager_list'),
    path('manager/<uuid:seminar_id>', views.ManagerView.as_view(), name='manager_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)