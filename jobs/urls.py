from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('job/<int:pk>/', views.job_detail, name='job_detail'),
    path('job/<int:pk>/apply/', views.apply_job, name='apply_job'),
    path('job/<int:pk>/applicants/', views.job_applicants, name='job_applicants'),
    path('post-job/', views.post_job, name='post_job'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-applications/', views.my_applications, name='my_applications'),
]