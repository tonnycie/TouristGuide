from django.utils.html import strip_tags
from rest_framework import serializers


def clean_text(value):
    """Маха всички HTML тагове от потребителски текст."""
    return strip_tags(value).strip()


def clean_required(value):
    """Същото, но текстът не може да остане празен след почистването."""
    cleaned = clean_text(value)
    if not cleaned:
        raise serializers.ValidationError("Полето не може да е празно.")
    return cleaned