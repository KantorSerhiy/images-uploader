from datetime import timedelta

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.files.storage import default_storage

import hashlib

from django.utils import timezone


class ThumbnailSize(models.Model):
    size = models.IntegerField(validators=[MinValueValidator(16), MaxValueValidator(4320)])

    def __str__(self):
        return f"size: {self.size}x{self.size}"


class Plan(models.Model):
    name = models.CharField(max_length=32)
    image_link = models.BooleanField(default=False)
    download_binary_image_link = models.BooleanField(default=False)
    thumbnail_size = models.ManyToManyField(ThumbnailSize, blank=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, default=None, null=True)


class BinaryImage(models.Model):
    binary_image = models.ImageField(upload_to="image/binary", blank=False)
    binary_image_link = models.CharField(blank=False, max_length=32, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    expiration_time = models.IntegerField(validators=[MinValueValidator(300), MaxValueValidator(30000)])
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        if self.binary_image is not None:
            path = self.binary_image.name
            if path:
                default_storage.delete(path)

        super(BinaryImage, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        seed = (str(self.created) + self.binary_image.name)
        self.binary_image_link = hashlib.md5(seed.encode('utf-8')).hexdigest()[:16]

        super(BinaryImage, self).save(*args, **kwargs)

    def is_expired(self):
        return (self.created + timedelta(seconds=self.expiration_time)) < timezone.now()

    def __str__(self):
        return f"Image binary: {self.pk}"


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='image', blank=False)
    binary_image = models.OneToOneField(BinaryImage, on_delete=models.CASCADE,
                                        default=None, null=True, blank=True, related_name='image')

    def get_extension(self):
        return self.image.name.split(".")[1]

    def __str__(self):
        return f"Image {self.pk}"
