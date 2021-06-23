from django.urls import path
from .import views


urlpatterns = [
   path('',views.summary,name="summary"),
   path('about/',views.about,name='about'),
   path('login',views.login_page,name='login_page'),
   path('register',views.register_page,name='register_page'),
   path('logout',views.logout_page,name='logout_page'),
   path('save_summary',views.save_summary,name="save_summary"),

]