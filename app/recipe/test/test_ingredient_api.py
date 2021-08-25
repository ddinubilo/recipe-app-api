from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')

def create_user(**params):
    return get_user_model().objects.create_user(**params)

class PublicIngredientsApiTests(TestCase):
    """Test the publicly available ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required accessing the ingredients endpoint"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    
class PrivateIngredientsApiTests(TestCase):
    """Test the authorized user ingredients API"""

    def setUp(self):
        data = {
            'email': 'test@dinubilo.com',
            'password': 'testpassword123',
            'name': 'Test Name'
        }
        self.user = create_user(**data)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_retrieve_ingredients_list(self):
        """ Test reteiving list of ingredients"""
        Ingredient.objects.create(user=self.user, name= "Beef")
        Ingredient.objects.create(user=self.user, name= "Salt")

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """ Test that only ingredients for the authenticated user are returned"""
        data2 = {
            'email': 'test2@dinubilo.com',
            'password': 'testpassword123',
            'name': 'Other Name'
        }
        user2 = create_user(**data2)

        Ingredient.objects.create(user=user2, name='Fruit')
        ingredient = Ingredient.objects.create(user = self.user, name = 'Cheese')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Test creating a new ingredient"""
        payload = {'name': 'Carrot'}

        self.client.post(INGREDIENTS_URL, payload)

        exists = Ingredient.objects.filter(
            user = self.user,
            name = payload['name'],
        ).exists()
        self.assertTrue(exists)
    
    def test_create_ingredient_invalid(self):
        """test creating a new ingredient with invalid payload"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        