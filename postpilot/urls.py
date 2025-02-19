from django.urls import path

from .apps import PostpilotConfig
from .views import RecipientCreateView, RecipientListView, RecipientDeleteView, RecipientUpdateView, HomeView

app_name = PostpilotConfig.name

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # Главная страница приложения
    path('recipient_list/', RecipientListView.as_view(), name='recipient_list'),
    path('recipient_form/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipient_form/<int:pk>', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipient_confirm_delete/<int:pk>', RecipientDeleteView.as_view(), name='recipient_delete'),
]
