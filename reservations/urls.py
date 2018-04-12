from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.ReservationModelViewSet, base_name='reservationset')

urlpatterns = [
    url(r'', include(router.urls))
    # url(r'^$', views.index, name='index'),
    # url(r'^create$', views.create, name='create'),
    # url(r'^(?P<reservation_id>[0-9]*)$', views.retrieve, name='retrieve'),
    # url(r'^(?P<reservation_id>[0-9]*)/status$', views.retrieve_status, name='retrieve_status'),
    # url(r'^(?P<reservation_id>[0-9]*)/change$', views.modify, name='modify'),
    # url(r'^(?P<reservation_id>[0-9]*)/delete$', views.delete, name='delete'),
    # url(r'^(?P<reservation_id>[0-9]*)/state/(?P<state>[0-5])$', views.state_change, name='statechange')
]
