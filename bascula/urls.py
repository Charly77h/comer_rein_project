from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_notas, name='lista_notas'),
    
    # Revisa esta línea con mucho cuidado
    path('nota/<int:folio>/', views.detalle_nota, name='detalle_nota'), 
    path('nota/nueva/', views.crear_nota, name='crear_nota'), 
    path('inventario/', views.reporte_inventario, name='reporte_inventario'),
]




    
   





   


