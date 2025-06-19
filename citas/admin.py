from django.contrib import admin
from .models import *  # Asegúrate de importar tus modelos

# Register your models here.
admin.site.register(Areas)
admin.site.register(UserProfile)

admin.site.register(AuthGroup)
admin.site.register(AuthGroupPermissions)
admin.site.register(AuthPermission)
admin.site.register(AuthUser)
admin.site.register(AuthUserGroups)
admin.site.register(AuthUserUserPermissions)
admin.site.register(Citas)
admin.site.register(Configuracion)
admin.site.register(DiasNoLaborables)
admin.site.register(DjangoAdminLog)
admin.site.register(DjangoContentType)
admin.site.register(DjangoMigrations)

admin.site.register(DjangoSession)
admin.site.register(DocumentosCitas)
admin.site.register(Empleados)
admin.site.register(HorariosLaborales)
admin.site.register(LogsAcceso)

admin.site.register(Tramites)
admin.site.register(Usuarios)

