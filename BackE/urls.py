"""
URL configuration for BB project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from Match.views import join_game_queue
from Match.views import out_card
from Match.views import query_outcard_right

urlpatterns = [
    path('admin/', admin.site.urls),
    # 收到加入游戏的请求, 一旦join_game,就要建立ws连接
    path('join_game/', join_game_queue, name='join_game'),


    # 申请出牌
    path('outc_ard/', out_card, name='out_card'),
    # 访问牌权
    path('query_outcard_right', query_outcard_right, name='query_outcard_right')

]
