from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models

def sample_user(email = 'test@dinubilo.com', password = 'testpassword123'):
    """Create a smample user"""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_succussful(self):
        """Test creating a new user with an email is successful"""
        email = "test@dinubilo.com"
        password = "test123"
        user = get_user_model().objects.create_user(
            email = email,
            password = password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for new user is normalized"""
        email = "test@DINUBILO.COM"
        user = get_user_model().objects.create_user(email,'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating used with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def  test_creae_new_superuser(self):
        email = "test@dinubilo.com"
        password = "testingpassword"
        user = get_user_model().objects.create_superuser(
            email = email,
            password = password,
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation"""
        tag = models.Tag.objects.create(
            user = sample_user(),
            name = 'Meat'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the ingredient string respresentation"""
        ingredient = models.Ingredient.objects.create(
            user = sample_user(),
            name = 'Beef'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test the recipe string respresentation"""
        recipe = models.Recipe.objects.create(
            user = sample_user(),
            title = 'Steak and Eggs',
            time_minutes = 5,
            price = 5.00,
        )

        self.assertEqual(str(recipe), recipe.title)    
