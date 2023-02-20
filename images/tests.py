from rest_framework.test import APITestCase
from django.urls import reverse
import io
from PIL import Image as PilImage
from rest_framework import status
from .models import Image, User, Plan, ThumbnailSize, BinaryImage
from django.core.files.images import ImageFile


class ImageTests(APITestCase):
    def setUp(self):
        self.list_create_url = reverse('images:image')

        self.tier_basic = Plan.objects.create(name='Basic', image_link=False, download_binary_image_link=False)
        self.tier_basic.thumbnail_size.add(ThumbnailSize.objects.create(size=200),
                                           ThumbnailSize.objects.create(size=400))

        self.tier_premium = Plan.objects.create(name='Premium', image_link=True, download_binary_image_link=False)
        self.tier_premium.thumbnail_size.add(ThumbnailSize.objects.create(size=200),
                                             ThumbnailSize.objects.create(size=400))

        self.tier_enterprise = Plan.objects.create(name='Enterprise', image_link=True, download_binary_image_link=True)
        self.tier_enterprise.thumbnail_size.add(ThumbnailSize.objects.create(size=200),
                                                ThumbnailSize.objects.create(size=400))

        self.user = User.objects.create_user(username='user_basic', password='Pas$w0rd', plan=self.tier_basic)
        self.user_premium = User.objects.create_user(username='user_premium', password='Pas$w0rd',
                                                     plan=self.tier_premium)
        self.user_enterprise = User.objects.create_user(username='user_enterprise', password='Pas$w0rd',
                                                        plan=self.tier_enterprise)

    # Static functions
    def create_image(self, size=(100, 100), color=(255, 255, 255), ext='png'):
        file = io.BytesIO()
        image = PilImage.new('RGB', size=size, color=color)
        image.save(file, ext)
        file.name = f'test.{ext}'
        file.seek(0)
        return file

    def create_binary_image_url(self, obj):
        return reverse('images:binary_image', kwargs={'image_id': obj.id})

    def get_binary_image_link(self, obj):
        return reverse('images:get_binary_link', kwargs={'binary_image_link': obj.binary_image_link})

    def create_image_object(self, user=False, filename='file.png'):
        if not user:
            return Image.objects.create(user=self.user,
                                        image=ImageFile(self.create_image(ext='png'), filename))

        return Image.objects.create(user=user,
                                    image=ImageFile(self.create_image(ext='png'), 'file.png'))

    def binary_image_link_tier_request(self, user):
        self.client.force_authenticate(user=user)

        binary_image = BinaryImage.objects.create(binary_image=ImageFile(self.create_image(), 'file.png'),
                                                  user=user, expiration_time=350)
        return self.client.get(self.get_binary_image_link(binary_image))

    # Create Image

    def test_create_image_unauthorized(self):
        response = self.client.post(self.list_create_url, data={'image': self.create_image()})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_image_authorized(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.list_create_url, data={'image': self.create_image()})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_image_empty(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.list_create_url, data={'image': ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_image_authenticate(self):
        response = self.client.post(self.list_create_url, data={'image': self.create_image()})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_image_ext(self):
        self.client.force_authenticate(user=self.user)

        correct_ext = ['jpeg', 'png']
        incorrect_ext = ['gif', 'bmp']

        for ext in correct_ext:
            response = self.client.post(self.list_create_url, data={'image': self.create_image(ext=ext)})
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        for ext in incorrect_ext:
            response = self.client.post(self.list_create_url, data={'image': self.create_image(ext=ext)})
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Create Image - Tiers

    def test_create_image_without_tier(self):
        user = User.objects.create_user(username='username42', password='Pas$w0rd2')
        self.client.force_authenticate(user=user)
        response = self.client.post(self.list_create_url, data={'image': self.create_image()})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Create Binary-Image
    def test_create_binary_image(self):
        self.client.force_authenticate(user=self.user_enterprise)

        image_object = self.create_image_object()

        response = self.client.post(self.create_binary_image_url(image_object), data={'expiration_time': 345})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_binary_image_unauthorized(self):
        image_object = self.create_image_object()

        response = self.client.post(self.create_binary_image_url(image_object), data={'expiration_time': 345})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_binary_image_expiration_limit(self):
        self.client.force_authenticate(user=self.user_enterprise)

        image_object = self.create_image_object()

        response = self.client.post(self.create_binary_image_url(image_object), data={'expiration_time': 32})
        response2 = self.client.post(self.create_binary_image_url(image_object), data={'expiration_time': 34543})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_binary_image_wrong_value(self):
        self.client.force_authenticate(user=self.user_enterprise)

        image_object = self.create_image_object()

        response = self.client.post(self.create_binary_image_url(image_object), data={'expiration_time': 'error'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Create Binary-Image - Tiers

    def test_create_binary_tier_no_access(self):
        image_object = self.create_image_object()

        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.create_binary_image_url(image_object), data={'expiration_time': 355})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user_premium)

        response = self.client.post(self.create_binary_image_url(image_object), data={'expiration_time': 3765})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Create Binary-Image-Link
    def test_get_binary_image_link_unauthorized(self):
        binary_image = BinaryImage.objects.create(binary_image=ImageFile(self.create_image(), 'file.png'),
                                                  user=self.user, expiration_time=350)
        response = self.client.get(self.get_binary_image_link(binary_image))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_binary_image_link_basic(self):
        response = self.binary_image_link_tier_request(self.user)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_binary_image_link_premium(self):
        response = self.binary_image_link_tier_request(self.user_premium)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_binary_image_link_enterpise(self):
        response = self.binary_image_link_tier_request(self.user_enterprise)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_binary_image_link_enterpise_is_owner(self):
        user_enterprise2 = User.objects.create_user(username='user_enterprise2', password='Pas$w0rd',
                                                    plan=self.tier_enterprise)

        self.client.force_authenticate(user=user_enterprise2)
        binary_image = BinaryImage.objects.create(binary_image=ImageFile(self.create_image(), 'file.png'),
                                                  user=self.user_enterprise, expiration_time=350)
        response = self.client.get(self.get_binary_image_link(binary_image))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # List of Images + Tiers

    def test_list_image_unauthorized(self):
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_image_without_tier(self):
        user = User.objects.create_user(username='user_no_tier', password='Pas$w0rd')
        self.client.force_authenticate(user=user)
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_image_authorized(self):

        self.client.force_authenticate(user=self.user)
        create_response = self.client.post(self.list_create_url, data={'image': self.create_image()})

        user2 = User.objects.create_user(username='username2', password='Pas$w0rd2', plan=self.tier_basic)
        self.client.force_authenticate(user=user2)

        create_response2 = self.client.post(self.list_create_url, data={'image': self.create_image()})
        list_response = self.client.get(self.list_create_url)

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(Image.objects.all().count(), 2)


