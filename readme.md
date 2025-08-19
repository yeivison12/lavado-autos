
  

# Sistema de Administración de Lavado de Autos

  

  

Aplicación web desarrollada en **Django** para administrar reservas, tarifas, horarios y trabajadores de un servicio de lavado de autos.

  

Incluye un **panel de control moderno** con Bootstrap, envío de correos de confirmación y generación de PDFs con **Html2pdf** y envios automatizados de correos electronicos.

  

  

---

  

  

## Características principales

  

-  **Gestión de reservas** con validación de envío de correo antes de guardar.

  

-  **CRUD personalizado** para modelos: `Reserva`, `Tarifa`, `HorarioDisponible`, `Worker` y `Recibo`.

  

-  **Panel de trabajadores** estilizado con tarjetas, badges y nav-pills de Bootstrap.

  

-  **Generación de PDFs** (facturas y recibos) con xhtml2pdf.

  

-  **Sistema de autenticación** para restringir el acceso a áreas privadas, uso del sistema interno de django(un poco modificado)

  

-  **Envío de correos automáticos** para confirmaciones y cancelaciones.

  

  

---

  

  

## Requisitos previos

  

- Python 3.10+

  

- Django 5.x

  

- Base de datos: PostgreSQL, MySQL o SQLite (por defecto)

  

- pip 

  

- Git 

- Tener una cuenta de google para acceder al smtp de gmail

  

  

---

  

  

## Instalación

  

  

```bash

  

# Clonar el repositorio

  

git  clone  https://github.com/yeivison12/lavado-autos.git

  

cd  lavado-autos

  

  

# Crear entorno virtual

  

python  -m  venv  venv

  

source  venv/bin/activate  # Linux/Mac

  

venv\Scripts\activate  # Windows

  

  

# Instalar dependencias

  

pip  install  -r  requirements.txt

  

  

# Migrar base de datos

  
python manage.py makemigrations

python  manage.py  migrate


# Crear superusuario
python  manage.py  createsuperuser

  
  

# Ejecutar el servidor

  

python  manage.py  runserver

  


```
# Luego debes acceder al panel de administración

debes  crear  un  grupo  llamado  Trabajadores(Con  la  mayúscula) ese  grupo  es  importante  para  el

funcionamiento,  cuando  crees  usuarios,  debes  ponerlos  en  el  grupo

trabajadores  para  que  puedan  acceder  y  limitar  sus  funciones  solo  a  la  de  trabajadores

# Diagrama de flujo
```mermaid
flowchart  TD

subgraph  Reserva

A[Usuario  genera  pedido] --> B{¿Horario  disponible?}

B  --  No  --> Z1[Fin: Sin  horarios]

B  --  Sí --> C[Enviar  correo  cliente]

  

C  --  Falla  --> Z2[Fin: Error  correo  cliente]

C  -- Éxito  --> D[Admin  revisa  pedido]

  

D  --> E{¿Confirma  admin?}

E  --  No  --> Z3[Fin: Pedido  pendiente]

E  --  Sí --> F[Enviar  correo  confirmación]

F  --  Falla  --> Z4[Fin: No  guardar  ni  asignar]

F  -- Éxito  --> G[Trabajo  disponible]

end

  

subgraph  Asignación

G  --> H{¿Trabajador  acepta?}

H  --  No  --> Z5[Fin: No  tomado]

H  --  Sí --> I[Correo  confirmación  trabajador]

  

I  --  Falla  --> Z6[Fin: No  asignado]

I  -- Éxito  --> J[Trabajador  realiza  trabajo]

end

  

subgraph  Finalización

J  --> K{¿Correo  finalización  enviado?}

K  --  No  --> Z7[Fin: No  completado]

K  --  Sí --> L[Trabajo  completado]

  

L  --> M[Generar  recibo  dashboard]

M  --> N[Modificar  precio/comentario]

N  --> O[Ver  PDF  recibo]

O  --> P[Enviar  recibo  por  correo]

  

P  --  Falla  --> Z8[Fin: Recibo  no  enviado]

P  -- Éxito  --> Z9[Fin: Proceso  terminado]

end
```
