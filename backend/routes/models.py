from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Route(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="routes"
    )
    title = models.CharField(max_length=200)
    destination = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    tips = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Waypoint(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="waypoints")
    name = models.CharField(max_length=200)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    order_index = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order_index"]

    def __str__(self):
        return f"{self.name} ({self.latitude}, {self.longitude})"


class Photo(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="route_photos/")


class Review(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="reviews")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    text = models.TextField()
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["route", "author"], name="one_review_per_user")
        ]