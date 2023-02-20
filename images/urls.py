from django.urls import path
from .views import ImageCreateListView, BinaryImageCreateListView, BinaryImageLinkView

urlpatterns = [
    path('image/', ImageCreateListView.as_view(), name='image'),
    path('image/<image_id>/binary-image', BinaryImageCreateListView.as_view(), name='binary_image'),
    path('image/<binary_image_link>/', BinaryImageLinkView.as_view(), name='get_binary_link'),
]

app_name = "images"
