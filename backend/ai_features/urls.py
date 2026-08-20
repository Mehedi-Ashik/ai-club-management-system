from django.urls import path
from . import views

app_name = "ai_features"

urlpatterns = [
    path("ask/", views.ask_chatbot, name="ask_chatbot"),
]