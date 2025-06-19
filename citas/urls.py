from django.urls import path
from . import views    # Importa las vistas de la app Tienda
from .views import *


urlpatterns = [
    path('', views.inicio, name='inicio'),  # Esta es la URL que buscas como 'inicio'
    path('tramites', views.TramitesView.as_view(), name='Tramites'),  # Esta es la URL que buscas como 'inicio'
    path('tramites/cita', views.TramitesCitaView.as_view(), name='TramitesCita'),  # Esta es la URL que buscas como 'inicio'
    path('ConsultaFecha', views.ConsultaFecha.as_view(), name='FechaDisponible'),  # Esta es la URL que buscas como 'inicio'
    path('GuardarCita', views.GuardarCita.as_view(), name='GuardarCita'),  # Esta es la URL que buscas como 'inicio'
    # En tu urls.py
    path('buscar-tramites/', views.BuscarTramitesView.as_view(), name='buscar-tramites'),
    path('Secure-login', views.login, name='Securelogin'),  # Esta es la URL que buscas como 'inicio'
    path('Panel-admin', views.panel, name='Panel'),
    path('actualizar-citas/', views.actualizar_estado_cita, name='actualizar_estado_cita'),


    path('consultar-cita', views.consulta, name='consultar-cita'),
    path('reagendar-cita', views.reagendar_cita, name='reagendar-cita'),
    path('cancelar-cita', views.cancelar_cita, name='cancelar-cita'),


]