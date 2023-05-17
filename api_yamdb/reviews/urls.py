from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReviewsViewSet


router = DefaultRouter()
router.register(r'titles/(?P<post_id>\d+)/reviews',
                ReviewsViewSet, basename='post')


urlpatterns = [
    path('', include(router.urls)),
]
