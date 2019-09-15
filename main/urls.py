"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin


app_name ='main'
urlpatterns = [
    path("",views.homepage,name='homepage'),
    path("register/",views.register,name='register'),
    path("logout/",views.logout_request,name='logout'),
    path("login/",views.login_request,name='login'),
    path("select/",views.select,name="select"),
    path("fit/",views.fit_data,name="fit"),
    path("visualise/",views.visualise,name="visualise"),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
