# -*- coding: utf-8 -*-

# =========================
# Librarys
# =========================
import os
from os.path import join, dirname
from flask import request, url_for
from flask_api import FlaskAPI, status, exceptions

# =========================
# Extensions initialization
# =========================
app = FlaskAPI(__name__)

# =========================
# Extensions initialization
# =========================



# =========================
# Routes
# =========================

#[id_conductor,puntos actuales,puntos perdidos,puntos ganados]
notes = {
    0: ['30245467K',11,1,0],
    1: ['28453456J',9,3,0],
    2: ['32323443N',12,2,2],
    3: ['28437658C',8,0,0],
    4: ['32466658X',14,0,0],
    5: ['28564768L',8,5,1],
}

def note_repr(key):
    return {
        'url': request.host_url.rstrip('/') + url_for('notes_detail', key=key),
        'id_conductor': notes[key][0],
        'puntos_actuales': notes[key][1],
        'puntos_perdidos':notes[key][2],
        'puntos_recuperados':notes[key][3]
    }


@app.route("/puntos", methods=['GET', 'POST'])
def notes_list():
    """
    List or create notes.
    """
    if request.method == 'POST':
        note = str(request.data.get('text', ''))
        idx = max(notes.keys()) + 1
        notes[idx] = note
        return note_repr(idx), status.HTTP_201_CREATED

    # request.method == 'GET'
    return [note_repr(idx) for idx in sorted(notes.keys())]


@app.route("/puntos/<int:key>/", methods=['GET', 'PUT', 'DELETE'])
def notes_detail(key):
    """
    Retrieve, update or delete note instances.
    """
    if request.method == 'PUT':
        note = str(request.data.get('text', ''))
        notes[key] = note
        return note_repr(key)

    elif request.method == 'DELETE':
        notes.pop(key, None)
        return '', status.HTTP_204_NO_CONTENT

    # request.method == 'GET'
    if key not in notes:
        raise exceptions.NotFound()
    return note_repr(key)


if __name__ == "__main__":
    app.run(debug=True)