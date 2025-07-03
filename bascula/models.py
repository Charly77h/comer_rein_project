from django.db import models

# Molde para los Proveedores
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=1)

    # Esto es para que en el panel de admin veamos el nombre y no "Proveedor object (1)"
    def __str__(self):
        return self.nombre

# Molde para los Materiales
class Material(models.Model):
    nombre = models.CharField(max_length=100, unique=True) # unique=True evita materiales duplicados
    es_merma = models.BooleanField(default=False) # Por defecto, un material no es merma

    def __str__(self):
        return self.nombre
    
    #------------------------------------------------------------
#           AÑADE ESTE CÓDIGO NUEVO
#------------------------------------------------------------

# Molde para el encabezado de la Nota de Entrada
class NotaDeEntrada(models.Model):
    folio = models.AutoField(primary_key=True) # Un número automático que es la clave
    fecha = models.DateTimeField(auto_now_add=True) # Guarda la fecha y hora al crearse
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT) # El "hilo" que lo conecta a un Proveedor
    placas_camion = models.CharField(max_length=50, blank=True) # blank=True significa que puede estar vacío
    
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('FINALIZADA', 'Finalizada'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='PENDIENTE')

    def __str__(self):
        return f"Nota #{self.folio} - {self.proveedor.nombre}"

# Molde para CADA LÍNEA dentro de una nota (EL CORAZÓN DE LA APP)
class LineaDeNota(models.Model):
    nota = models.ForeignKey(NotaDeEntrada, related_name='lineas', on_delete=models.CASCADE) # Hilo a la Nota a la que pertenece
    material = models.ForeignKey(Material, on_delete=models.PROTECT) # Hilo al Material de esta línea
    kilos = models.IntegerField() # Kilos de esta línea
    
    # ¡LA MAGIA! El hilo que apunta a OTRA línea de la que se rebajó
    linea_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='rebajes')

    def __str__(self):
        if self.linea_padre:
            return f"  └─ Rebaje de {self.material.nombre} ({self.kilos} kg) de la línea #{self.linea_padre.id}"
        else:
            return f"Material Original: {self.material.nombre} ({self.kilos} kg)"