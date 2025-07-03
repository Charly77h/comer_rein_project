from django.shortcuts import render, get_object_or_404, redirect
# ASEGÚRATE DE QUE 'Material' ESTÉ EN ESTA LÍNEA DE IMPORTACIÓN
from .models import NotaDeEntrada, LineaDeNota, Proveedor, Material  

# Vista para la página principal: la lista de todas las notas de entrada
def lista_notas(request):
    # 1. Pedimos a la base de datos TODAS las notas de entrada
    #    y las ordenamos de más nueva a más vieja.
    notas = NotaDeEntrada.objects.all().order_by('-folio')

    # 2. Pasamos la lista de notas a la plantilla para que las muestre.
    #    'contexto' es como un diccionario que lleva la información.
    contexto = {'notas_list': notas}
    return render(request, 'bascula/lista_notas.html', contexto)

# Reemplaza la anterior 'detalle_nota' por esta versión FINAL
def detalle_nota(request, folio):
    nota = get_object_or_404(NotaDeEntrada, pk=folio)

    # --- Lógica para procesar el envío de formularios ---
    if request.method == 'POST':
        accion = request.POST.get('accion')
         

        if accion == 'anadir_material':
            material_id = request.POST.get('material')
            kilos = request.POST.get('kilos')
            material_obj = get_object_or_404(Material, pk=material_id)
            LineaDeNota.objects.create(nota=nota, material=material_obj, kilos=kilos)

        elif accion == 'anadir_rebaje':
            linea_padre_id = request.POST.get('linea_padre')
            material_id = request.POST.get('material')
            kilos = request.POST.get('kilos')
            linea_padre_obj = get_object_or_404(LineaDeNota, pk=linea_padre_id)
            material_obj = get_object_or_404(Material, pk=material_id)
            LineaDeNota.objects.create(nota=nota, material=material_obj, kilos=kilos, linea_padre=linea_padre_obj)
        
        elif accion == 'finalizar_nota':
         nota.estado = 'FINALIZADA'
         nota.save() # Guarda el cambio en la base de


        return redirect('detalle_nota', folio=nota.folio) # Redirige para refrescar la página

    # --- Lógica para mostrar la página (código que ya teníamos pero mejorado) ---
    todos_los_materiales = Material.objects.all()
    
    # --- Cálculo de pesos netos (Lógica compleja) ---
    pesos_netos = {}
    lineas_origen = nota.lineas.all() # Tomamos todas las líneas

    for linea in lineas_origen:
        # Sumamos al material de la línea actual
        pesos_netos[linea.material.nombre] = pesos_netos.get(linea.material.nombre, 0) + int(linea.kilos)
        # Si la línea tiene un padre, restamos del material del padre
        if linea.linea_padre:
            pesos_netos[linea.linea_padre.material.nombre] = pesos_netos.get(linea.linea_padre.material.nombre, 0) - int(linea.kilos)

    contexto = {
        'nota': nota,
        'materiales': todos_los_materiales,
        'pesos_netos': pesos_netos.items(),
    }
    
    return render(request, 'bascula/detalle_nota.html', contexto)


# Vista para crear una NUEVA nota de entrada (maneja el formulario)
def crear_nota(request):
    # Preguntamos: ¿El usuario está enviando datos (POST) o solo pidiendo ver la página (GET)?
    if request.method == 'POST':
        # Si está enviando datos...
        # 1. Recogemos la información del formulario que nos llegó.
        proveedor_id = request.POST.get('proveedor')
        placas = request.POST.get('placas_camion')

        # 2. Buscamos el objeto Proveedor completo usando el ID que recibimos.
        proveedor_obj = get_object_or_404(Proveedor, pk=proveedor_id)

        # 3. Creamos el nuevo registro de NotaDeEntrada en la base de datos.
        nueva_nota = NotaDeEntrada.objects.create(
            proveedor=proveedor_obj,
            placas_camion=placas
            # El estado por defecto es 'PENDIENTE', como definimos en el modelo.
        )

        # 4. Redirigimos al usuario a la página de detalle de la nota que acabamos de crear.
        return redirect('detalle_nota', folio=nueva_nota.folio)

    else:
        # Si solo está pidiendo ver la página...
        # 1. Obtenemos la lista de todos los proveedores para rellenar el menú desplegable.
        todos_los_proveedores = Proveedor.objects.all()
        
        # 2. Se la pasamos a la plantilla del formulario.
        contexto = {'proveedores': todos_los_proveedores}
        return render(request, 'bascula/crear_nota.html', contexto)
    
    # Añade esta nueva función al final de views.py
def reporte_inventario(request):
    # Usaremos el mismo cálculo de pesos netos, pero aplicado a TODAS las notas
    
    inventario = {}
    todas_las_lineas = LineaDeNota.objects.all()

    for linea in todas_las_lineas:
        nota = linea.nota
        if nota.estado == 'FINALIZADA': # Solo contamos notas finalizadas
            # Sumamos al material de la línea actual
            inventario[linea.material.nombre] = inventario.get(linea.material.nombre, 0) + int(linea.kilos)
            # Si es un rebaje, restamos del material del padre
            if linea.linea_padre:
                inventario[linea.linea_padre.material.nombre] = inventario.get(linea.linea_padre.material.nombre, 0) - int(linea.kilos)

    # Filtramos para no mostrar materiales con stock 0 o negativo (como basura, etc.)
    inventario_positivo = {k: v for k, v in inventario.items() if v > 0}
    
    contexto = {'inventario': inventario_positivo.items()}
    return render(request, 'bascula/reporte_inventario.html', contexto)
