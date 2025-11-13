"""
URL configuration for omoide_teikibin_project project.

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
from omoide_teikibin_project.views import IndexView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('', IndexView.as_view() , name='index'),
    # accounts.urlsへのURLパターン
    path('api/accounts/', include('accounts.urls')),
    # post.urlsへのURLパターン
    path('api/post/', include('post.urls')),
    # friend.urlsへのURLパターン
    path("api/friend/", include("friend.urls")),
    path("api/post/", include("post.urls")),
    #開発時のみ、メディアURL用
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
