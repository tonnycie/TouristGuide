from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from .models import Review, Route, Waypoint


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

class ReviewApiTests(APITestCase):
    def setUp(self):
        self.ivan = User.objects.create_user("ivan", password="Tur1st!Pass2026")
        self.maria = User.objects.create_user("maria", password="Tur1st!Pass2026")
        self.petar = User.objects.create_user("petar", password="Tur1st!Pass2026")
        self.route = Route.objects.create(author=self.ivan, title="Рила", destination="Рила")
        Waypoint.objects.create(route=self.route, name="Паничище", latitude=42.2686, longitude=23.317)
        self.url = f"/api/routes/{self.route.id}/reviews/"

    def test_review_requires_login(self):
        r = self.client.post(self.url, {"text": "Супер", "rating": 5}, format="json")
        self.assertEqual(r.status_code, 401)

    def test_create_review(self):
        self.client.force_authenticate(self.maria)
        r = self.client.post(self.url, {"text": "Супер", "rating": 5}, format="json")
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["author"], "maria")
        self.assertEqual(Review.objects.count(), 1)

    def test_rating_out_of_range_rejected(self):
        self.client.force_authenticate(self.maria)
        for bad in (0, 6):
            r = self.client.post(self.url, {"text": "Ок", "rating": bad}, format="json")
            self.assertEqual(r.status_code, 400)
        self.assertEqual(Review.objects.count(), 0)

    def test_duplicate_review_rejected(self):
        self.client.force_authenticate(self.maria)
        self.client.post(self.url, {"text": "Супер", "rating": 5}, format="json")
        r = self.client.post(self.url, {"text": "Пак", "rating": 4}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Review.objects.count(), 1)

    def test_cannot_review_own_route(self):
        self.client.force_authenticate(self.ivan)
        r = self.client.post(self.url, {"text": "Моят", "rating": 5}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Review.objects.count(), 0)

    def test_list_reviews_is_public(self):
        Review.objects.create(route=self.route, author=self.maria, text="Супер", rating=5)
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data), 1)

    def test_average_rating(self):
        Review.objects.create(route=self.route, author=self.maria, text="Добро", rating=4)
        Review.objects.create(route=self.route, author=self.petar, text="Супер", rating=5)
        r = self.client.get(f"/api/routes/{self.route.id}/")
        self.assertEqual(r.data["average_rating"], 4.5)
        self.assertEqual(r.data["reviews_count"], 2)

    def test_no_reviews_means_no_average(self):
        r = self.client.get(f"/api/routes/{self.route.id}/")
        self.assertIsNone(r.data["average_rating"])
        self.assertEqual(r.data["reviews_count"], 0)

    def test_xss_in_review_is_stripped(self):
        self.client.force_authenticate(self.maria)
        r = self.client.post(
            self.url,
            {"text": "<script>alert(1)</script>Страхотно", "rating": 5},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertNotIn("<script>", r.data["text"])
        self.assertNotIn("<", Review.objects.get().text)

    def test_review_empty_after_strip_rejected(self):
        self.client.force_authenticate(self.maria)
        r = self.client.post(self.url, {"text": "<script></script>", "rating": 5}, format="json")
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Review.objects.count(), 0)

    def test_xss_in_route_fields_is_stripped(self):
        self.client.force_authenticate(self.maria)
        payload = {
            "title": "<b>Хак</b><script>alert(1)</script>",
            "destination": "<img src=x onerror=alert(1)>Варна",
            "description": "<script>alert(2)</script>Описание",
            "tips": "<i>съвет</i>",
            "waypoints": [{"name": "<script>x</script>Точка", "latitude": 43.2, "longitude": 27.9}],
        }
        r = self.client.post("/api/routes/", payload, format="json")
        self.assertEqual(r.status_code, 201)
        for field in ("title", "destination", "description", "tips"):
            self.assertNotIn("<", r.data[field])
        self.assertNotIn("<", r.data["waypoints"][0]["name"])           