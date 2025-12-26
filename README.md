# BROKEN TUNES

Pequeño proyecto para reproducir canciones desde una base de datos y servir una interfaz web. He intentado mantener todo lo más simple y directo posible para facilitar pruebas y despliegues locales.

Requisitos:
- MariaDB (ej. XAMPP)
- Python 3.x
- Paquetes: Flask, mysql-connector-python

Pasos para ejecutar:
1. Importar la base de datos:
   - Abrir phpMyAdmin o tu herramienta MySQL preferida.
   - Importar `backup_db.sql`.
2. Instalar dependencias:
   - pip install flask mysql-connector-python
3. Arrancar el servidor:
   - python app.py
4. Abrir en el navegador:
   - http://localhost:5000

Credenciales por defecto (para demo local):
- Usuario: `admin`
- Contraseña: `1234`

Descripción general:
- `backup_db.sql` crea la base de datos `broken_tunes`, usuarios y canciones. La columna `mp3_data` contiene datos binarios del audio.
- `app.py` es el servidor Flask que expone:
  - `/` : frontend
  - `/api/songs` : lista de canciones
  - `/play/<id>` : devuelve el MP3 de la canción
  - `/login` : endpoint de login básico
- `index.html` es una interfaz sencilla con reproductor de audio y control de velocidad.

Consideraciones de diseño:
- He priorizado simplicidad y facilidad de ejecución en entornos locales.
- Algunas decisiones se tomaron para facilitar pruebas y despliegues sin infraestructura adicional.