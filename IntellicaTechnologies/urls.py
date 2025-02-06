"""
URL configuration for IntellicaTechnologies project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from Landing.views import landing
from login.views import *
from executive.views import *
from Api.login     import *
from Api.kyc       import *
from Api.idr       import *


urlpatterns = [
    #path('admin/', admin.site.urls),
    path('',landing),
    path('login',LoginUser),
    path('home',Home),
    path('login_api',login),
    path('pan',pan_kyc),
    path('cface',compareFace),
    path('getImage',downloadImage),
    path('getResult',downloadResult),
    path('analysis',faceAnalysis),
    path('nameMatch',name_match),
    path('distanceMap',getDistanceResult)
]
