from django.contrib import admin
from django.urls import path
from storm_companies import views

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('login/', views.ratelimited_login, name='login'),
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('companies/create/', views.company_create, name='company_create'),
    path('companies/<int:pk>/update/', views.company_update, name='company_update'),
    path('companies/<int:pk>/delete/', views.company_delete, name='company_delete'),
    path('stormevents/', views.stormevent_list, name='stormevent_list'),
    path('stormevents/create/', views.stormevent_create, name='stormevent_create'),
    path('stormevents/<int:pk>/update/', views.stormevent_update, name='stormevent_update'),
    path('stormevents/<int:pk>/delete/', views.stormevent_delete, name='stormevent_delete'),
    path('deployments/', views.deployment_list, name='deployment_list'),
    path('deployments/create/', views.deployment_create, name='deployment_create'),
    path('deployments/<int:pk>/update/', views.deployment_update, name='deployment_update'),
    path('deployments/<int:pk>/delete/', views.deployment_delete, name='deployment_delete'),
]
