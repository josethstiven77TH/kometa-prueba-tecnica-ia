// Estado en memoria del curso actual (mientras el usuario está en el flujo)
let cursoActual = null;

const overlay = document.getElementById('loadingOverlay');
const loadingText = document.getElementById('loadingText');

function mostrarCarga(texto) {
    loadingText.textContent = texto;
    overlay.classList.add('loading-overlay--visible');
}

function ocultarCarga() {
    overlay.classList.remove('loading-overlay--visible');
}

function irAPaso(numero) {
    document.querySelectorAll('.panel').forEach(p => p.classList.remove('panel--active'));
    document.getElementById(`panel-${numero}`).classList.add('panel--active');

    document.querySelectorAll('.step').forEach(s => s.classList.remove('step--active'));
    document.querySelector(`.step[data-step="${numero}"]`).classList.add('step--active');
}

// ---------- PASO 1: Generar ----------

document.querySelectorAll('.chip').forEach(chip => {
    chip.addEventListener('click', () => {
        document.getElementById('inputInstruccion').value = chip.dataset.example;
    });
});

document.getElementById('formInstruccion').addEventListener('submit', async (e) => {
    e.preventDefault();
    const instruccion = document.getElementById('inputInstruccion').value.trim();
    if (!instruccion) return;

    mostrarCarga('Diseñando la estructura del curso y redactando el contenido…');

    try {
        const res = await fetch('/api/curso/generar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ instruccion }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Error generando el curso');
        }

        cursoActual = await res.json();
        renderizarPreview(cursoActual);
        irAPaso(2);

    } catch (err) {
        alert('Ocurrió un error generando el curso: ' + err.message);
    } finally {
        ocultarCarga();
    }
});

// ---------- PASO 2: Preview ----------

function renderizarPreview(curso) {
    document.getElementById('previewNombreCurso').textContent = curso.nombre_curso;
    document.getElementById('previewDescripcion').textContent = curso.descripcion_corta;

    const contenedor = document.getElementById('modulesContainer');
    contenedor.innerHTML = '';

    curso.modulos.forEach((modulo, idx) => {
        const card = document.createElement('div');
        card.className = 'module-card';
        card.innerHTML = `
            <div class="module-card__header">
                <span class="module-card__number">0${idx + 1}</span>
                <input class="module-card__title" data-idx="${idx}" data-field="titulo" value="${escaparHtml(modulo.titulo)}">
            </div>
            <textarea class="module-card__content" data-idx="${idx}" data-field="contenido_texto">${escaparHtml(modulo.contenido_texto)}</textarea>
            <div class="module-card__tags">
                <span class="tag">Texto</span>
                <span class="tag">PDF</span>
                <span class="tag">Imagen</span>
                <span class="tag">Podcast</span>
            </div>
        `;
        contenedor.appendChild(card);
    });

    // Permitir edición: actualiza cursoActual cuando el usuario cambia algo
    contenedor.querySelectorAll('[data-field]').forEach(el => {
        el.addEventListener('input', (e) => {
            const idx = parseInt(e.target.dataset.idx);
            const field = e.target.dataset.field;
            cursoActual.modulos[idx][field] = e.target.value;
        });
    });
}

function escaparHtml(texto) {
    const div = document.createElement('div');
    div.textContent = texto;
    return div.innerHTML;
}

document.getElementById('btnVolver').addEventListener('click', () => irAPaso(1));

document.getElementById('btnPublicar').addEventListener('click', async () => {
    mostrarCarga('Generando imágenes, audio y PDFs, y publicando en Moodle… esto puede tardar unos minutos.');

    try {
        const res = await fetch('/api/curso/publicar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ curso: cursoActual }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Error publicando el curso');
        }

        const resultado = await res.json();

        document.getElementById('publicadoTitulo').textContent = cursoActual.nombre_curso;
        document.getElementById('linkCurso').href = resultado.url_curso;
        document.getElementById('chatMessages').innerHTML = '';
        irAPaso(3);

    } catch (err) {
        alert('Ocurrió un error publicando el curso: ' + err.message);
    } finally {
        ocultarCarga();
    }
});

// ---------- PASO 3: Nuevo curso / Chat ----------

document.getElementById('btnNuevoCurso').addEventListener('click', () => {
    document.getElementById('inputInstruccion').value = '';
    cursoActual = null;
    irAPaso(1);
});

document.getElementById('formChat').addEventListener('submit', async (e) => {
    e.preventDefault();
    const input = document.getElementById('inputPregunta');
    const pregunta = input.value.trim();
    if (!pregunta) return;

    agregarMensajeChat(pregunta, 'user');
    input.value = '';

    try {
        const res = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ pregunta }),
        });

        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Error en el chat');
        }

        const data = await res.json();
        agregarMensajeChat(data.respuesta, 'ai');

    } catch (err) {
        agregarMensajeChat('Ocurrió un error: ' + err.message, 'ai');
    }
});

function agregarMensajeChat(texto, tipo) {
    const contenedor = document.getElementById('chatMessages');
    const msg = document.createElement('div');
    msg.className = `chat-msg chat-msg--${tipo}`;
    msg.textContent = texto;
    contenedor.appendChild(msg);
    contenedor.scrollTop = contenedor.scrollHeight;
}