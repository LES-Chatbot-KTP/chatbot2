from django.urls import path
from Backend.app.api.views.chat import ChatView

urlpatterns = [
    path("chat/", ChatView.as_view(), name="chat"),
]