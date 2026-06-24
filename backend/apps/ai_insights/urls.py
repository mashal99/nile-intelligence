from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.GenerateInsightView.as_view(), name='ai-generate'),
    path('ask/', views.AskMarketQuestionView.as_view(), name='ai-ask'),
]
