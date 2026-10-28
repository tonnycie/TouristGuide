from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import Route, Waypoint


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
class RouteApiTests(APITestCase):
    def setUp(self):
        self.ivan = User.objects.create_user("ivan", password="Tur1st!Pass2026")
        self.maria = User.objects.create_user("maria", password="Tur1st!Pass2026")
        self.payload = {
            "title": "Пловдив - София",
            "destination": "София",
            "description": "Приятно пътуване",
            "tips": "Тръгнете рано",
            "waypoints": [
                {"name": "Пловдив", "latitude": 42.1354, "longitude": 24.7453},
                {"name": "София", "latitude": 42.6977, "longitude": 23.3219},
            ],
        }

    def make_route(self):
        route = Route.objects.create(author=self.ivan, title="Стар", destination="Варна")
        Waypoint.objects.create(route=route, name="Варна", latitude=43.2141, longitude=27.9147)
        return route

    def test_list_is_public(self):
        self.make_route()
        r = self.client.get("/api/routes/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)

    def test_create_requires_login(self):
        r = self.client.post("/api/routes/", self.payload, format="json")
        self.assertEqual(r.status_code, 401)

    def test_create_route_with_waypoints(self):
        self.client.force_authenticate(self.ivan)
        r = self.client.post("/api/routes/", self.payload, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["author"], "ivan")
        self.assertEqual([w["name"] for w in r.data["waypoints"]], ["Пловдив", "София"])
        self.assertEqual([w["order_index"] for w in r.data["waypoints"]], [0, 1])
        self.assertEqual(Waypoint.objects.count(), 2)

    def test_create_without_waypoints_rejected(self):
        self.client.force_authenticate(self.ivan)
        self.payload["waypoints"] = []
        r = self.client.post("/api/routes/", self.payload, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Route.objects.count(), 0)

    def test_invalid_latitude_rejected(self):
        self.client.force_authenticate(self.ivan)
        self.payload["waypoints"][0]["latitude"] = 100
        r = self.client.post("/api/routes/", self.payload, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Route.objects.count(), 0)

    def test_other_user_cannot_edit(self):
        route = self.make_route()
        self.client.force_authenticate(self.maria)
        r = self.client.patch(f"/api/routes/{route.id}/", {"title": "Хакнат"}, format="json")
        self.assertEqual(r.status_code, 403)
        route.refresh_from_db()
        self.assertEqual(route.title, "Стар")

    def test_author_can_edit_and_replace_waypoints(self):
        route = self.make_route()
        self.client.force_authenticate(self.ivan)
        new_points = [
            {"name": "А", "latitude": 42.0, "longitude": 24.0},
            {"name": "Б", "latitude": 43.0, "longitude": 25.0},
            {"name": "В", "latitude": 44.0, "longitude": 26.0},
        ]
        r = self.client.patch(
            f"/api/routes/{route.id}/",
            {"title": "Нов", "waypoints": new_points},
            format="json",
        )
        self.assertEqual(r.status_code, 200)
        route.refresh_from_db()
        self.assertEqual(route.title, "Нов")
        self.assertEqual(route.waypoints.count(), 3)

    def test_other_user_cannot_delete(self):
        route = self.make_route()
        self.client.force_authenticate(self.maria)
        r = self.client.delete(f"/api/routes/{route.id}/")
        self.assertEqual(r.status_code, 403)
        self.assertEqual(Route.objects.count(), 1)

    def test_author_can_delete(self):
        route = self.make_route()
        self.client.force_authenticate(self.ivan)
        r = self.client.delete(f"/api/routes/{route.id}/")
        self.assertEqual(r.status_code, 204)
        self.assertEqual(Route.objects.count(), 0)        