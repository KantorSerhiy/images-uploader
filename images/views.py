from rest_framework.generics import ListCreateAPIView, CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from django.urls import reverse

from .serializers import ImageListSerializer, ImageCreateSerializer, BinaryImageCreateSerializer, \
    BinaryImageLinkSerializer
from .models import Image, BinaryImage
from .ulils import create_exist_image
from .permissions import PlanIsSet, BinaryImageCreate


class ImageCreateListView(ListCreateAPIView):
    permission_classes = (IsAuthenticated, PlanIsSet)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ImageCreateSerializer
        return ImageListSerializer

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user).prefetch_related("user__plan")

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


class BinaryImageCreateListView(CreateAPIView):
    permission_classes = (IsAuthenticated, PlanIsSet, BinaryImageCreate)
    serializer_class = BinaryImageCreateSerializer

    def create(self, request, *args, **kwargs):
        try:
            image = Image.objects.get(id=self.kwargs.get('image_id'))
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid():
                if image.binary_image is not None:
                    image.binary_image.delete()

                binary_image = serializer.save(
                    binary_image=create_exist_image(image.image, '1', ext=image.get_extension()),
                    user=self.request.user)

                image.binary_image = binary_image
                image.save()

                url_binary_link = reverse("images:get_binary_link", args=[binary_image.binary_image_link])

                return Response({"binary_image": self.request.build_absolute_uri(url_binary_link)})

            return Response(status=status.HTTP_400_BAD_REQUEST)

        except Image.DoesNotExist:
            return Response({"message": "Image does not exist."}, status=status.HTTP_400_BAD_REQUEST)


class BinaryImageLinkView(ListAPIView):
    permission_classes = (IsAuthenticated, PlanIsSet, BinaryImageCreate)
    serializer_class = BinaryImageLinkSerializer

    def list(self, request, *args, **kwargs):
        try:
            binary_image = BinaryImage.objects.get(binary_image_link=self.kwargs.get('binary_image_link'))

            if binary_image.user == request.user:

                if not binary_image.is_expired():
                    serializer = self.get_serializer(binary_image)
                    return Response(serializer.data)

                return Response({"message": "Link has expired."}, status=status.HTTP_400_BAD_REQUEST)

            return Response(status=status.HTTP_403_FORBIDDEN)

        except BinaryImage.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
