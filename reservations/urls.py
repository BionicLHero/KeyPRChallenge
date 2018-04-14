from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.ReservationModelViewSet)


urlpatterns = [
    url(r'^(?P<reservation_id>[0-9]*)/status-change$', views.StatusChangeView.as_view(), name='statuschange'),
    url(r'', include(router.urls)),
]
