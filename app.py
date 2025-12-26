# app.py
# Servidor Flask para BROKEN TUNES (implementación monolítica)
from flask import Flask, jsonify, Response, send_from_directory, request, abort
import mysql.connector
import time

app = Flask(__name__, static_folder='.', static_url_path='')

# Configuración de base de datos (entorno local)
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '',   # credenciales locales por defecto
    'database': 'broken_tunes'
}

def get_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    return conn

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/api/songs')
def api_songs():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, artist FROM songs")
    rows = cur.fetchall()
    result = []
    for r in rows:
        result.append({'id': r[0], 'title': r[1], 'artist': r[2]})
    cur.close()
    conn.close()
    return jsonify(result)

@app.route('/api/songs_backup')
def api_songs_backup():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, original_song_id, title, artist, backup_note, backed_up_by, backed_up_at FROM songs_backup ORDER BY backed_up_at DESC")
    rows = cur.fetchall()
    out = []
    for r in rows:
        out.append({
            'id': r[0],
            'original_song_id': r[1],
            'title': r[2],
            'artist': r[3],
            'backup_note': r[4],
            'backed_up_by': r[5],
            'backed_up_at': r[6].isoformat() if hasattr(r[6], 'isoformat') else r[6]
        })
    cur.close()
    conn.close()
    return jsonify(out)

@app.route('/api/backup/<int:song_id>', methods=['POST'])
def api_backup_song(song_id):
    # Crear una copia en songs_backup de la canción indicada
    backed_by = request.form.get('backed_by', 'web-ui')
    note = request.form.get('note', 'manual backup')
    conn = get_db()
    cur = conn.cursor()
    # Obtener la canción original
    cur.execute("SELECT id, title, artist, mp3_data FROM songs WHERE id = %s", (song_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return jsonify({'ok': False, 'error': 'song not found'}), 404
    original_id, title, artist, mp3_blob = row[0], row[1], row[2], row[3]
    try:
        mp3_bytes = bytes(mp3_blob)
    except Exception:
        mp3_bytes = mp3_blob
    # Insertar en songs_backup
    insert_q = ("INSERT INTO songs_backup (original_song_id, title, artist, mp3_data, backup_note, backed_up_by, backed_up_at) "
                "VALUES (%s, %s, %s, %s, %s, %s, NOW())")
    cur.execute(insert_q, (original_id, title, artist, mp3_bytes, note, backed_by))
    conn.commit()
    backup_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({'ok': True, 'backup_id': backup_id})

@app.route('/play/<id>')
def play_song(id):
    conn = get_db()
    cur = conn.cursor()
    # Consulta construida directamente para mantener el código directo y fácil de seguir
    query = "SELECT * FROM songs WHERE id = " + id
    cur.execute(query)
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        abort(404)
    mp3_blob = row[3]
    try:
        data = bytes(mp3_blob)
    except Exception:
        data = mp3_blob
    cur.close()
    conn.close()
    return Response(data, mimetype='audio/mpeg',
                    headers={"Content-Disposition": "inline; filename=\"%s.mp3\"" % row[1]})

@app.route('/play_backup/<int:backup_id>')
def play_backup(backup_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, title, artist, mp3_data FROM songs_backup WHERE id = %s", (backup_id,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        abort(404)
    try:
        data = bytes(row[3])
    except Exception:
        data = row[3]
    cur.close()
    conn.close()
    return Response(data, mimetype='audio/mpeg',
                    headers={"Content-Disposition": "inline; filename=\"%s_backup.mp3\"" % row[1]})

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = %s AND password = %s", (username, password))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return jsonify({'ok': True, 'username': username})
    return jsonify({'ok': False}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)