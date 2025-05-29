from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home_view, name='home'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('finance-assistant/', views.finance_assistant_view, name='finance_assistant'),
    path('AIAssistant/', views.AIAssistant, name='AIAssistant'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('budget_tracker/', views.budget_tracker, name='budget_tracker'),
    path('create-account-steps/', views.steps_to_create_account, name='create_account_steps'),
    path('financeeducation/', views.financeeducation, name='financeeducation'),
    
]
