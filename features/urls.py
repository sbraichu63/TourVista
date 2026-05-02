from django.urls import path
from . import views

app_name = 'features'

urlpatterns = [
    path('weather/', views.weather_api, name='weather'),
    path('chatbot/', views.chatbot_api, name='chatbot'),
    path('budget/', views.budget_calculator, name='budget'),
    path('destinations/', views.destinations_map, name='destinations_map'),
    path('quiz/', views.quiz_page, name='quiz'),
    path('api/quiz/', views.quiz_api, name='quiz_api'),
]
