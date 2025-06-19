from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import *
import logging
from datetime import datetime
import json
import re
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.utils import timezone
from .models import UserProfile, Citas, Areas  # Asegúrate de importar tus modelos



def inicio(request):
    return render(request, 'citas/index.html')
def panel(request):
    return render(request, 'enlace/table.html')

def consulta(request):
    if request.method == 'POST':
        folio = request.POST.get('folio')
        print(f"📥 Folio recibido por POST: {folio}")
        
        try:
            # Buscar la cita por el código de confirmación (folio)
            cita = get_object_or_404(Citas, id_cita=folio)
            print(f"✅ Cita encontrada: {cita.id_cita}")
            
            # Pasar todos los datos de la cita al template
            context = {
                'cita': cita,
                'folio': folio
            }
            
            return render(request, 'citas/reagendarcancelar.html', context)
            
        except Citas.DoesNotExist:
            # Si no se encuentra la cita
            print(f"❌ No se encontró cita con folio: {folio}")
            messages.error(request, 'No se encontró ninguna cita with ese folio.')
            return redirect('inicio')  # Asegúrate de que 'inicio' sea el nombre correcto de tu URL
            
        except Exception as e:
            # Manejo de otros errores
            print(f"❌ Error al buscar la cita: {str(e)}")
            messages.error(request, 'Ocurrió un error al buscar la cita.')
            return redirect('inicio')
    
    # Si no es POST, redirigir al inicio
    return redirect('inicio')


@method_decorator(csrf_exempt, name='dispatch')
class BuscarTramitesView(View):
    def post(self, request):
        query = request.POST.get('query', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        # Buscar en trámites activos
        tramites = Tramites.objects.filter(
            Q(nombre_tramite__icontains=query) | 
            Q(descripcion__icontains=query) |
            Q(id_area__nombre_area__icontains=query),
            activo=1
        ).select_related('id_area')[:10]  # Limitar a 10 resultados
        
        # Formatear resultados
        results = []
        for tramite in tramites:
            results.append({
                'id_tramite': tramite.id_tramite,
                'nombre_tramite': tramite.nombre_tramite,
                'descripcion': tramite.descripcion[:200] + '...' if tramite.descripcion and len(tramite.descripcion) > 200 else tramite.descripcion,
                'area_nombre': tramite.id_area.nombre_area,
                'costo': float(tramite.costo) if tramite.costo else 0,
                'tiempo_estimado': tramite.tiempo_estimado
            })
        
        return JsonResponse({'results': results})


@csrf_protect
def login(request):
    """
    Vista de login que autentica al usuario y muestra sus citas
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                auth_login(request, user)
                
                try:
                    user_profile = UserProfile.objects.get(user=user)
                    
                    if user_profile.area:
                        area = user_profile.area
                        citas = Citas.objects.filter(id_area=area).order_by('-fecha', '-hora')
                        
                        # Renderizar directamente la plantilla con las citas
                        return render(request, 'enlace/table.html', {
                            'citas': citas,
                            'area': area
                        })
                        
                    else:
                        messages.warning(request, 'El usuario no tiene área asignada')
                        return redirect('login')
                        
                except UserProfile.DoesNotExist:
                    messages.warning(request, 'El usuario no tiene perfil configurado')
                    return redirect('login')
                
            else:
                messages.error(request, 'Error de autenticación')
        else:
            messages.error(request, 'Credenciales inválidas')
    
    # Si es GET o hay errores, mostrar el formulario
    form = AuthenticationForm()
    return render(request, 'enlace/login.html', {'form': form})

@require_POST
def reagendar_cita(request):
    try:
        data = json.loads(request.body)
        cita_id = data.get('cita_id')
        nueva_fecha = data.get('nueva_fecha')  # formato esperado: 'YYYY-MM-DD'
        nueva_hora = data.get('nueva_hora')    # formato esperado: 'HH:MM'

        print("========== DATOS RECIBIDOS ==========")
        print("ID de la cita:", cita_id)
        print("Nueva fecha:", nueva_fecha)
        print("Nueva hora:", nueva_hora)
        print("=====================================")

        # Obtener cita y actualizar
        cita = Citas.objects.get(pk=cita_id)
        cita.fecha = nueva_fecha
        cita.hora = nueva_hora
        cita.fecha_actualizacion = datetime.now()
        cita.save()

        return JsonResponse({
            'message': 'Cita reagendada correctamente',
            'status': 'ok'
        }, status=200)

    except Citas.DoesNotExist:
        return JsonResponse({'message': 'La cita no existe'}, status=404)

    except Exception as e:
        print("Error al procesar los datos:", str(e))
        return JsonResponse({'message': 'Error al procesar los datos'}, status=400)
    



@require_POST
def cancelar_cita(request):
    try:
        data = json.loads(request.body)
        cita_id = data.get('cita_id')

        print("========== CANCELAR CITA ==========")
        print("ID de la cita a cancelar:", cita_id)
        print("===================================")

        # Buscar y eliminar la cita
        cita = Citas.objects.get(pk=cita_id)
        cita.delete()

        return JsonResponse({
            'message': 'Cita cancelada correctamente',
            'status': 'ok'
        }, status=200)

    except Citas.DoesNotExist:
        return JsonResponse({'message': 'La cita no existe'}, status=404)

    except Exception as e:
        print("Error al cancelar la cita:", str(e))
        return JsonResponse({'message': 'Error al cancelar la cita'}, status=400)


class TramitesView(View):
    def post(self, request):
        id_area = request.POST.get('clave_secreta')

        print("\n=== DATOS RECIBIDOS POR POST ===")
        print(f"id_area: {id_area}")

        if not id_area:
            print("❌ ERROR: No se recibió 'id_area'")
            return HttpResponse(status=400)

        try:
            id_area = int(id_area)
        except ValueError:
            print("❌ ERROR: 'id_area' debe ser un número")
            return HttpResponse(status=400)

        tramites = Tramites.objects.filter(id_area=id_area, activo=1).select_related('id_area')

        print("\n📋 TRÁMITES ENCONTRADOS:")
        for tramite in tramites:
            print(f"\n🔹 ID: {tramite.id_tramite}")
            print(f"📌 Nombre: {tramite.nombre_tramite}")
            print(f"🏢 Área: {tramite.id_area.nombre_area}")
            print(f"📝 Descripción: {tramite.descripcion}")
            print(f"💰 Costo: {tramite.costo}")

        nombre_area = tramites[0].id_area.nombre_area if tramites else "Área desconocida"
        print(f"\n✅ Total trámites: {tramites.count()}")
        print(f"📌 Nombre del área: {nombre_area}")

        return render(request, 'citas/tramites.html', {
            'tramites': tramites,
            'nombre_area': nombre_area
        })
    



    
class TramitesCitaView(View):
    def post(self, request):
        id_tramite = request.POST.get('cookie')

        print("\n=== DATOS RECIBIDOS POR POST ===")
        print(f"id_tramite: {id_tramite}")

        if not id_tramite:
            print("❌ ERROR: No se recibió 'id_tramite'")
            return HttpResponse(status=400)

        try:
            id_tramite = int(id_tramite)
        except ValueError:
            print("❌ ERROR: 'id_tramite' debe ser un número")
            return HttpResponse(status=400)

        # Obtener el trámite
        tramite = get_object_or_404(Tramites, id_tramite=id_tramite, activo=1)

        print("\n✅ TRÁMITE ENCONTRADO:")
        print(f"🔹 ID: {tramite.id_tramite}")
        print(f"📌 Nombre: {tramite.nombre_tramite}")
        print(f"🏢 Área: {tramite.id_area.nombre_area}")
        print(f"📝 Descripción: {tramite.descripcion}")
        print(f"💰 Costo: {tramite.costo}")

        return render(request, 'citas/Agendarcita.html', {
            'tramite': tramite
        })


def extract_id_from_object_string(obj_str):
    """Extrae el ID de strings como 'Areas object (1)'"""
    try:
        return int(obj_str.split('(')[1].split(')')[0])
    except (IndexError, AttributeError, ValueError):
        raise ValueError(f"No se pudo extraer ID de: {obj_str}")
    


class ConsultaFecha(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            fecha = data.get('fecha')
            print(data.get('id_area'))
            id_area = extract_id_from_object_string(data.get('id_area'))

            print(f"Datos recibidos - Fecha: {fecha}, Área ID: {id_area}")

            # Horas disponibles predefinidas
            available_hours = ['09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00']

            # Consulta a la base de datos
            citas_existentes = Citas.objects.filter(
                id_area=id_area,
                fecha=fecha
            ).values_list('hora', flat=True)

            horas_ocupadas = [hora.strftime('%H:%M') for hora in citas_existentes if hora]
            horas_disponibles = [hora for hora in available_hours if hora not in horas_ocupadas]

            # Mostrar en consola
            print(f"Horas ocupadas: {horas_ocupadas}")
            print(f"Horas disponibles: {horas_disponibles}")

            return JsonResponse({
                'disponible': bool(horas_disponibles),
                'horas_disponibles': horas_disponibles,
                'debug': {
                    'id_area_recibido': data.get('id_area'),
                    'id_area_procesado': id_area,
                    'horas_ocupadas': horas_ocupadas
                }
            })

        except Exception as e:
            print(f"Error al procesar la solicitud: {e}")
            return JsonResponse({
                'disponible': False,
                'error': str(e),
                'received_data': str(data)
            }, status=400)




class GuardarCita(View):    
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            fecha = data.get('fecha')
            hora = data.get('hora')
            id_area = extract_id_from_object_string(data.get('id_area'))

            print(f"📅 Datos recibidos - Fecha: {fecha}, 🕒 Hora: {hora}, 🏢 Área ID: {id_area}")

            # Validar y obtener el área
            area = get_object_or_404(Areas, pk=id_area)

            # Crear la cita
            cita = Citas.objects.create(
                id_area=area,
                fecha=fecha,
                hora=hora,
                estado='PENDIENTE',  # Puedes cambiarlo según tu lógica
                fecha_creacion=timezone.now(),
                fecha_actualizacion=timezone.now(),
                codigo_confirmacion='CONF' + timezone.now().strftime('%Y%m%d%H%M%S')  # Ejemplo de código
            )

            print(f"✅ Cita guardada con ID: {cita.id_cita}")

            return JsonResponse({
                'disponible': True,
                'id_cita': cita.id_cita,
                'codigo_confirmacion': cita.codigo_confirmacion
            })

        except Exception as e:
            print(f"❌ Error al procesar la solicitud: {e}")
            return JsonResponse({
                'disponible': False,
                'error': str(e),
                'received_data': str(data)
            }, status=400)
        
@require_POST
@csrf_protect
def actualizar_estado_cita(request):
    """
    Vista para actualizar múltiples citas desde el formulario
    """
    try:
        # Obtener todos los datos del POST
        post_data = request.POST
        
        # Diccionarios para almacenar los cambios
        estados_cambios = {}
        comentarios_cambios = {}
        
        # Procesar todos los campos del formulario
        for key, value in post_data.items():
            if key.startswith('estado_'):
                # Extraer el ID de la cita
                cita_id = key.replace('estado_', '')
                estados_cambios[cita_id] = value
                
            elif key.startswith('comentarios_'):
                # Extraer el ID de la cita
                cita_id = key.replace('comentarios_', '')
                comentarios_cambios[cita_id] = value
        
        # Validar que tenemos datos para procesar
        if not estados_cambios and not comentarios_cambios:
            messages.warning(request, 'No se encontraron cambios para procesar.')
            # CAMBIO: Obtener el área del usuario para redireccionar correctamente
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                if user_profile.area:
                    area = user_profile.area
                    citas = Citas.objects.filter(id_area=area).order_by('-fecha', '-hora')
                    return render(request, 'enlace/citas.html', {
                        'citas': citas,
                        'area': area
                    })
            except UserProfile.DoesNotExist:
                pass
            return redirect('login')
        
        # Procesar los cambios con transacción
        cambios_realizados = 0
        errores = []
        
        with transaction.atomic():
            # Obtener todas las citas que van a ser modificadas
            citas_ids = set(estados_cambios.keys()) | set(comentarios_cambios.keys())
            citas = Citas.objects.filter(id_cita__in=citas_ids)
            
            for cita in citas:
                cita_id_str = str(cita.id_cita)
                cambios_en_cita = False
                
                try:
                    # Actualizar estado si cambió
                    if cita_id_str in estados_cambios:
                        nuevo_estado = estados_cambios[cita_id_str]
                        if nuevo_estado != cita.estado:
                            # Validar estado
                            estados_validos = ['pendiente', 'asistida', 'completada', 'cancelada']
                            if nuevo_estado in estados_validos:
                                cita.estado = nuevo_estado
                                cambios_en_cita = True
                            else:
                                errores.append(f'Estado inválido para cita {cita.id_cita}: {nuevo_estado}')
                                continue
                    
                    # Actualizar comentarios si cambió
                    if cita_id_str in comentarios_cambios:
                        nuevos_comentarios = comentarios_cambios[cita_id_str].strip()
                        if nuevos_comentarios != (cita.comentarios or ''):
                            cita.comentarios = nuevos_comentarios if nuevos_comentarios else None
                            cambios_en_cita = True
                    
                    # Guardar si hubo cambios
                    if cambios_en_cita:
                        cita.save()
                        cambios_realizados += 1
                        
                except ValidationError as ve:
                    errores.append(f'Error de validación en cita {cita.id_cita}: {str(ve)}')
                except Exception as e:
                    errores.append(f'Error al actualizar cita {cita.id_cita}: {str(e)}')
        
        # Preparar mensajes de respuesta
        if cambios_realizados > 0:
            messages.success(
                request, 
                f'✅ Se actualizaron {cambios_realizados} cita{"s" if cambios_realizados != 1 else ""} correctamente.'
            )
        
        if errores:
            for error in errores:
                messages.error(request, f'❌ {error}')
        
        if cambios_realizados == 0 and not errores:
            messages.info(request, 'ℹ️ No se detectaron cambios para actualizar.')
        
        # CAMBIO: En lugar de usar HTTP_REFERER, obtener el área y renderizar la plantilla
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.area:
                area = user_profile.area
                # Volver a consultar las citas actualizadas
                citas = Citas.objects.filter(id_area=area).order_by('-fecha', '-hora')
                return render(request, 'enlace/citas.html', {
                    'citas': citas,
                    'area': area
                })
            else:
                messages.warning(request, 'El usuario no tiene área asignada')
                return redirect('login')
        except UserProfile.DoesNotExist:
            messages.warning(request, 'El usuario no tiene perfil configurado')
            return redirect('login')
        
    except Exception as e:
        messages.error(request, f'❌ Error inesperado: {str(e)}')
        # CAMBIO: También aquí, intentar volver a la pantalla de citas
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.area:
                area = user_profile.area
                citas = Citas.objects.filter(id_area=area).order_by('-fecha', '-hora')
                return render(request, 'enlace/table.html', {
                    'citas': citas,
                    'area': area
                })
        except:
            pass
        return redirect('login')