from .models import Image, BinaryImage
from rest_framework.serializers import ValidationError, ModelSerializer, SerializerMethodField
from sorl.thumbnail import get_thumbnail
from collections import OrderedDict


class ImageCreateSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = ['image']

    def validate_image(self, value):
        ext = value.name.split(".")[1]
        correct_ext = ['jpeg', 'png', 'jpg']

        if ext.lower() not in correct_ext:
            raise ValidationError("Wrong file extension.")

        return value


class ImageListSerializer(ModelSerializer):
    thumbnails = SerializerMethodField()
    binary_image = SerializerMethodField()

    class Meta:
        model = Image
        fields = ["id",'image', 'thumbnails', 'binary_image']

    def get_fields(self, *args, **kwargs):
        fields = super().get_fields(*args, **kwargs)
        user = self.context.get('request').user

        if not user.plan.image_link:
            fields.pop('image', None)

        if not user.plan.download_binary_image_link:
            fields.pop('binary_image', None)

        return fields

    def get_thumbnails(self, obj):
        request = self.context.get('request', None)
        thumbnail_urls = []

        for thumbnail_size in obj.user.plan.thumbnail_size.all().values_list('size', flat=True):
            url = get_thumbnail(obj.image, str(thumbnail_size), crop='center', quality=95).url
            thumbnail_urls.append({thumbnail_size: request.build_absolute_uri(url)})

        return thumbnail_urls

    def get_binary_image(self, obj):
        request = self.context.get('request', None)

        if obj.binary_image is not None:
            if not obj.binary_image.is_expired():
                return request.build_absolute_uri(obj.binary_image.binary_image_link)

    def to_representation(self, instance):
        result = super(ImageListSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key]])


class BinaryImageCreateSerializer(ModelSerializer):
    class Meta:
        model = BinaryImage
        fields = ['expiration_time']


class BinaryImageLinkSerializer(ModelSerializer):
    class Meta:
        model = BinaryImage
        fields = ['binary_image']
