from django.urls import path

from .apps import PostpilotConfig
from .views import RecipientCreateView, RecipientListView, RecipientDeleteView, RecipientUpdateView

app_name = PostpilotConfig.name

urlpatterns = [
    path('', RecipientListView.as_view(), name='recipient_list'),  # Главная страница приложения
    path('recipient_list/', RecipientListView.as_view(), name='recipient_list'),
    path('recipient_form/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipient_form/<int:pk>', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipient_confirm_delete/<int:pk>', RecipientDeleteView.as_view(), name='recipient_delete'),
]
