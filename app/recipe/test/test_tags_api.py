from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer

TAGS_URL = reverse('recipe:tag-list')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicTagsApitTests(TestCase):
    """Test the publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)   
    
class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        data = {
            'email': 'test@dinubilo.com',
            'password': 'testpassword123',
            'name': 'Test Name'
        }
        self.user = create_user(**data)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_tags(self):
        """ Test reteiving tags"""
        Tag.objects.create(user=self.user, name= "Meat")
        Tag.objects.create(user=self.user, name= "Vegetable")

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test that tgas returned are for the authenticated user"""
        data2 = {
            'email': 'test2@dinubilo.com',
            'password': 'testpassword123',
            'name': 'Other Name'
        }
        user2 = create_user(**data2)

        Tag.objects.create(user=user2, name='Fruit')
        tag = Tag.objects.create(user = self.user, name = 'Cheese')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {'name': 'Test Tag'}

        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user = self.user,
            name = payload['name']
        ).exists()
        self.assertTrue(exists)
    
    def test_create_tag_invalid(self):
        """test creating a new tag with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
