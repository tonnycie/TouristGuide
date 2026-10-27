from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class AuthTests(APITestCase):
    def test_register_and_login(self):
        r = self.client.post(
            "/api/auth/register/",
            {"username": "ivan", "email": "ivan@example.com", "password": "Tur1st!Pass2026"},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertTrue(User.objects.filter(username="ivan").exists())
        self.assertNotIn("password", r.data)

        r = self.client.post(
            "/api/auth/login/",
            {"username": "ivan", "password": "Tur1st!Pass2026"},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)

    def test_register_weak_password_rejected(self):
        r = self.client.post(
            "/api/auth/register/",
            {"username": "pesho", "email": "p@example.com", "password": "123"},
            format="json",
        )
        self.assertEqual(r.status_code, 400)
        self.assertFalse(User.objects.filter(username="pesho").exists())

    def test_wrong_password_login_fails(self):
        User.objects.create_user("maria", password="Tur1st!Pass2026")
        r = self.client.post(
            "/api/auth/login/",
            {"username": "maria", "password": "greshna"},
            format="json",
        )
        self.assertEqual(r.status_code, 401)