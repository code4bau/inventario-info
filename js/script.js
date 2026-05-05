let app;
let $$;
let state = {
    items: [],
    transactions: [],
    areas: [],
    personas: [],
    inventoryMap: {},
};

document.addEventListener('DOMContentLoaded', () => {
    app = new Framework7({
        el: '#app',
        name: 'Inventario Informatica',
        theme: 'auto',
        colors: {
            primary: '#1c705b',
        },
    });

    $$ = Dom7;
    
    // Función de Login centralizada
    const handleLogin = async () => {
        const password = $$('#login-pass').val();
        if (!password) {
            app.dialog.alert("Por favor, ingresá la contraseña");
            return;
        }

        app.preloader.show();
        try {
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username: 'admin', password })
            });
            
            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('inv_token', data.token);
                app.loginScreen.close('#login-screen');
                fetchData();
            } else {
                app.dialog.alert("Contraseña incorrecta");
                $$('#login-error').show();
            }
        } catch (err) { 
            app.dialog.alert("Error de conexión con el servidor"); 
        } finally {
            app.preloader.hide();
        }
    };

    $$('#btn-login-submit').on('click', (e) => {
        e.preventDefault();
        handleLogin();
    });

    $$('#login-form').on('submit', (e) => {
        e.preventDefault();
        handleLogin();
    });

    // Mover aquí la lógica del botón (+)
    $$('#btn-add-transaction').on('click', () => {
        const popupHtml = `
            <div class="popup popup-swipe-to-close">
                <div class="view">
                    <div class="page">
                        <div class="navbar">
                            <div class="navbar-bg"></div>
                            <div class="navbar-inner">
                                <div class="title">Nuevo Movimiento</div>
                                <div class="right"><a href="#" class="link popup-close">Cerrar</a></div>
                            </div>
                        </div>
                        <div class="page-content">
                            <form id="form-transaction" class="list no-hairlines-md">
                                <ul>
                                    <li class="item-content item-input">
                                        <div class="item-inner">
                                            <div class="item-title item-label">Activo</div>
                                            <div class="item-input-wrap">
                                                <select id="f-item" required>
                                                    <option value="">Seleccionar...</option>
                                                    ${state.items.map(i => `<option value="${i.id}">${i.nombre} (${i.codigo_patrimonial})</option>`).join('')}
                                                </select>
                                            </div>
                                        </div>
                                    </li>
                                    <li class="item-content item-input">
                                        <div class="item-inner">
                                            <div class="item-title item-label">Acción</div>
                                            <div class="item-input-wrap">
                                                <select id="f-type" required>
                                                    <option value="ENTRADA">ENTRADA (+)</option>
                                                    <option value="SALIDA">SALIDA (-)</option>
                                                </select>
                                            </div>
                                        </div>
                                    </li>
                                    <li class="item-content item-input">
                                        <div class="item-inner">
                                            <div class="item-title item-label">Responsable</div>
                                            <div class="item-input-wrap">
                                                <select id="f-persona" required>
                                                    <option value="">Seleccionar...</option>
                                                    ${state.personas.map(p => `<option value="${p.id}">${p.nombre_completo}</option>`).join('')}
                                                </select>
                                            </div>
                                        </div>
                                    </li>
                                    <li class="item-content item-input">
                                        <div class="item-inner">
                                            <div class="item-title item-label">Área</div>
                                            <div class="item-input-wrap">
                                                <select id="f-area" required>
                                                    <option value="">Ubicación...</option>
                                                    ${state.areas.map(a => `<option value="${a.id}">${a.nombre_area}</option>`).join('')}
                                                </select>
                                            </div>
                                        </div>
                                    </li>
                                    <li class="item-content item-input">
                                        <div class="item-inner">
                                            <div class="item-title item-label">Observaciones</div>
                                            <div class="item-input-wrap">
                                                <textarea id="f-obs" placeholder="Detalles..."></textarea>
                                            </div>
                                        </div>
                                    </li>
                                </ul>
                                <div class="block">
                                    <button type="submit" class="button button-fill button-large">Confirmar Registro</button>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        `;
        app.popup.create({ content: popupHtml, swipeToClose: true }).open();
        
        $$('#form-transaction').on('submit', async (e) => {
            e.preventDefault();
            const d = {
                item_id: $$('#f-item').val(),
                type: $$('#f-type').val(),
                persona_id: $$('#f-persona').val(),
                area_id: $$('#f-area').val(),
                observaciones: $$('#f-obs').val()
            };

            if (d.type === 'SALIDA' && (state.inventoryMap[d.item_id]?.stock || 0) <= 0) {
                app.dialog.alert("ERROR: Stock insuficiente.");
                return;
            }

            try {
                const res = await fetch('/api/transactions', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(d)
                });
                if (res.ok) {
                    app.popup.close();
                    app.toast.create({ text: "Movimiento guardado", closeTimeout: 2000 }).open();
                    fetchData();
                }
            } catch (err) { app.dialog.alert("Error de servidor"); }
        });
    });

    init();
});

// --- AUTH LOGIC (Fuera del listener) ---
const checkAuth = () => {
    const token = localStorage.getItem('inv_token');
    if (!token) {
        app.loginScreen.open('#login-screen', false);
        return false;
    }
    return true;
};

// ... Resto de funciones auxiliares (fetchData, render, etc) se mantienen iguales ...


const init = async () => {
    // Limpiamos tokens viejos si existen para asegurar el primer login
    if (!localStorage.getItem('inv_initialized')) {
        localStorage.removeItem('inv_token');
        localStorage.setItem('inv_initialized', 'true');
    }
    
    if (!checkAuth()) return;
    fetchData();
};


const fetchData = async () => {
    app.preloader.show();
    try {
        const res = await fetch('/api/init');
        const data = await res.json();
        
        state.areas = data.areas;
        state.personas = data.personas;
        state.items = data.items;
        state.transactions = data.transactions.map(t => ({
            ...t,
            timestamp: new Date(t.timestamp)
        }));
        
        processState();
        rebuild();
    } catch (e) {
        app.dialog.alert("Error cargando base de datos");
    } finally {
        app.preloader.hide();
    }
};

const processState = () => {
    const projection = {};
    state.items.forEach(i => projection[i.id] = { ...i, stock: 0, last: null });

    [...state.transactions].reverse().forEach(t => {
        if (projection[t.item_id]) {
            projection[t.item_id].stock += (t.type === 'ENTRADA' ? 1 : -1);
            projection[t.item_id].last = t.timestamp;
        }
    });
    state.inventoryMap = projection;
};

const rebuild = () => {
    renderDashboard();
    renderItems();
    renderHistory();
    renderAdmin();
    
    // Seed button visibility
    if (state.items.length === 0) {
        $$('#seed-btn-container').html('<a href="#" onclick="seedData()" class="link">Cargar Semillas</a>');
    } else {
        $$('#seed-btn-container').html('');
    }
};

// --- RENDERING ---

const renderDashboard = () => {
    const items = Object.values(state.inventoryMap);
    const critical = items.filter(i => i.stock <= 0).length;

    $$('#view-dashboard').html(`
        <div class="block-title">Resumen de Estado</div>
        <div class="row">
            <div class="col-50">
                <div class="card card-outline color-blue">
                    <div class="card-content card-content-padding text-align-center">
                        <div style="font-size:24px; font-weight:bold">${state.items.length}</div>
                        <div style="font-size:12px">Activos</div>
                    </div>
                </div>
            </div>
            <div class="col-50">
                <div class="card card-outline color-red">
                    <div class="card-content card-content-padding text-align-center">
                        <div style="font-size:24px; font-weight:bold">${critical}</div>
                        <div style="font-size:12px">Stock Crítico</div>
                    </div>
                </div>
            </div>
        </div>

        <div class="block-title">Actividad Reciente</div>
        <div class="list media-list inset">
            <ul>
                ${state.transactions.slice(0, 5).map(t => `
                    <li>
                        <div class="item-content">
                            <div class="item-inner">
                                <div class="item-title-row">
                                    <div class="item-title" style="font-weight:bold">${state.items.find(i => i.id === t.item_id)?.nombre || '---'}</div>
                                    <div class="item-after" style="color:${t.type === 'ENTRADA' ? 'green' : 'orange'}">${t.type}</div>
                                </div>
                                <div class="item-subtitle">${t.timestamp.toLocaleString()}</div>
                                <div class="item-text">${t.observaciones || ''}</div>
                            </div>
                        </div>
                    </li>
                `).join('') || '<li class="item-content"><div class="item-inner">Sin movimientos recientes</div></li>'}
            </ul>
        </div>
    `);
};

const renderItems = () => {
    $$('#view-items').html(`
        <div class="list media-list inset">
            <ul>
                ${state.items.map(i => `
                    <li>
                        <a href="#" class="item-link item-content" onclick="viewTrace('${i.id}')">
                            <div class="item-inner">
                                <div class="item-title-row">
                                    <div class="item-title" style="font-weight:bold">${i.nombre}</div>
                                    <div class="item-after">
                                        <span class="badge ${state.inventoryMap[i.id]?.stock > 0 ? 'color-green' : 'color-red'}">
                                            Stock: ${state.inventoryMap[i.id]?.stock || 0}
                                        </span>
                                    </div>
                                </div>
                                <div class="item-subtitle">${i.categoria} | ${i.codigo_patrimonial}</div>
                                <div class="item-text">${i.descripcion || ''}</div>
                            </div>
                        </a>
                    </li>
                `).join('')}
            </ul>
        </div>
    `);
};

const renderHistory = (filterId = null) => {
    const data = filterId ? state.transactions.filter(t => t.item_id === filterId) : state.transactions;
    
    $$('#view-history').html(`
        <div class="block-title display-flex justify-content-space-between align-items-center">
            ${filterId ? 'Historial de Activo' : 'Ledger Global'}
            ${filterId ? '<a href="#" class="button button-small button-outline" onclick="renderHistory()">Ver Todo</a>' : ''}
        </div>
        <div class="list accordion-list inset">
            <ul>
                ${data.map(t => `
                    <li class="accordion-item">
                        <a href="#" class="item-content item-link">
                            <div class="item-inner">
                                <div class="item-title">
                                    <b style="color:${t.type === 'ENTRADA' ? 'green' : 'orange'}">${t.type}</b> - 
                                    ${state.items.find(i => i.id === t.item_id)?.nombre || '---'}
                                </div>
                                <div class="item-after" style="font-size:10px">${t.timestamp.toLocaleDateString()}</div>
                            </div>
                        </a>
                        <div class="accordion-item-content">
                            <div class="block">
                                <p><b>Fecha:</b> ${t.timestamp.toLocaleString()}</p>
                                <p><b>Responsable:</b> ${state.personas.find(p => p.id === t.persona_id)?.nombre_completo || '---'}</p>
                                <p><b>Área:</b> ${state.areas.find(a => a.id === t.area_id)?.nombre_area || '---'}</p>
                                <p><b>Observaciones:</b> ${t.observaciones || '---'}</p>
                            </div>
                        </div>
                    </li>
                `).join('') || '<li class="item-content"><div class="item-inner">Sin registros</div></li>'}
            </ul>
        </div>
    `);
};

const renderAdmin = () => {
    $$('#view-admin').html(`
        <div class="block-title">Gestión de Datos Maestros</div>
        
        <div class="list accordion-list inset">
            <ul>
                <li class="accordion-item">
                    <a href="#" class="item-content item-link">
                        <div class="item-media"><i class="icon f7-icons">plus_app</i></div>
                        <div class="item-inner"><div class="item-title">Agregar Nuevo Ítem</div></div>
                    </a>
                    <div class="accordion-item-content">
                        <form id="form-add-item" class="list no-hairlines-md">
                            <ul>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Nombre</div>
                                        <div class="item-input-wrap"><input type="text" id="ai-nombre" required></div>
                                    </div>
                                </li>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Código Patrimonial</div>
                                        <div class="item-input-wrap"><input type="text" id="ai-codigo" required></div>
                                    </div>
                                </li>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Categoría</div>
                                        <div class="item-input-wrap">
                                            <select id="ai-categoria">
                                                <option value="Hardware">Hardware</option>
                                                <option value="Periférico">Periférico</option>
                                                <option value="Redes">Redes</option>
                                                <option value="Otro">Otro</option>
                                            </select>
                                        </div>
                                    </div>
                                </li>
                            </ul>
                            <div class="block"><button type="submit" class="button button-fill">Guardar Ítem</button></div>
                        </form>
                    </div>
                </li>
                
                <li class="accordion-item">
                    <a href="#" class="item-content item-link">
                        <div class="item-media"><i class="icon f7-icons">person_badge_plus</i></div>
                        <div class="item-inner"><div class="item-title">Agregar Persona</div></div>
                    </a>
                    <div class="accordion-item-content">
                        <form id="form-add-persona" class="list no-hairlines-md">
                            <ul>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Nombre Completo</div>
                                        <div class="item-input-wrap"><input type="text" id="ap-nombre" required></div>
                                    </div>
                                </li>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Rol</div>
                                        <div class="item-input-wrap"><input type="text" id="ap-rol"></div>
                                    </div>
                                </li>
                            </ul>
                            <div class="block"><button type="submit" class="button button-fill">Agregar Persona</button></div>
                        </form>
                    </div>
                </li>
                
                <li class="accordion-item">
                    <a href="#" class="item-content item-link">
                        <div class="item-media"><i class="icon f7-icons">map_pin_ellipse</i></div>
                        <div class="item-inner"><div class="item-title">Crear Área / Ubicación</div></div>
                    </a>
                    <div class="accordion-item-content">
                        <form id="form-add-area" class="list no-hairlines-md">
                            <ul>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Nombre del Área</div>
                                        <div class="item-input-wrap"><input type="text" id="aa-nombre" required></div>
                                    </div>
                                </li>
                            </ul>
                            <div class="block"><button type="submit" class="button button-fill">Crear Área</button></div>
                        </form>
                    </div>
                </li>
            </ul>
        </div>
        
        <div class="block">
            <a href="/api/report" target="_blank" class="button button-fill color-blue" style="margin-bottom:1rem">
                <i class="icon f7-icons" style="font-size:18px; margin-right:8px">cloud_download</i> 
                Descargar Reporte PDF
            </a>
            <button class="button button-fill color-red" onclick="logout()">Cerrar Sesión</button>
        </div>

    `);

    // Listeners
    $$('#form-add-item').on('submit', (e) => {
        e.preventDefault();
        handleAdminPost('/api/items', {
            nombre: $$('#ai-nombre').val(),
            codigo_patrimonial: $$('#ai-codigo').val(),
            categoria: $$('#ai-categoria').val()
        }, "Ítem guardado");
    });
    
    $$('#form-add-persona').on('submit', (e) => {
        e.preventDefault();
        handleAdminPost('/api/personas', {
            nombre_completo: $$('#ap-nombre').val(),
            rol: $$('#ap-rol').val()
        }, "Persona agregada");
    });
    
    $$('#form-add-area').on('submit', (e) => {
        e.preventDefault();
        handleAdminPost('/api/areas', {
            nombre_area: $$('#aa-nombre').val()
        }, "Área creada");
    });
};

const handleAdminPost = async (url, data, msg) => {
    app.preloader.show();
    try {
        const res = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        if (res.ok) {
            app.toast.create({ text: msg, closeTimeout: 2000 }).open();
            fetchData();
        }
    } catch (e) { app.dialog.alert("Error al guardar"); }
    finally { app.preloader.hide(); }
};

// --- TRANSACTIONS ---

$$('#btn-add-transaction').on('click', () => {
    const popupHtml = `
        <div class="popup popup-swipe-to-close">
            <div class="view">
                <div class="page">
                    <div class="navbar">
                        <div class="navbar-bg" style="background:#1c705b"></div>
                        <div class="navbar-inner">
                            <div class="title" style="color:white">Nuevo Movimiento</div>
                            <div class="right"><a href="#" class="link popup-close color-white">Cerrar</a></div>
                        </div>
                    </div>
                    <div class="page-content">
                        <form id="form-transaction" class="list no-hairlines-md">
                            <ul>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Activo</div>
                                        <div class="item-input-wrap">
                                            <select id="f-item" required>
                                                <option value="">Seleccionar...</option>
                                                ${state.items.map(i => `<option value="${i.id}">${i.nombre} (${i.codigo_patrimonial})</option>`).join('')}
                                            </select>
                                        </div>
                                    </div>
                                </li>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Acción</div>
                                        <div class="item-input-wrap">
                                            <select id="f-type" required>
                                                <option value="ENTRADA">ENTRADA (+)</option>
                                                <option value="SALIDA">SALIDA (-)</option>
                                            </select>
                                        </div>
                                    </div>
                                </li>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Responsable</div>
                                        <div class="item-input-wrap">
                                            <select id="f-persona" required>
                                                <option value="">Seleccionar...</option>
                                                ${state.personas.map(p => `<option value="${p.id}">${p.nombre_completo}</option>`).join('')}
                                            </select>
                                        </div>
                                    </div>
                                </li>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Área</div>
                                        <div class="item-input-wrap">
                                            <select id="f-area" required>
                                                <option value="">Ubicación...</option>
                                                ${state.areas.map(a => `<option value="${a.id}">${a.nombre_area}</option>`).join('')}
                                            </select>
                                        </div>
                                    </div>
                                </li>
                                <li class="item-content item-input">
                                    <div class="item-inner">
                                        <div class="item-title item-label">Observaciones</div>
                                        <div class="item-input-wrap">
                                            <textarea id="f-obs" placeholder="Detalles..."></textarea>
                                        </div>
                                    </div>
                                </li>
                            </ul>
                            <div class="block">
                                <button type="submit" class="button button-fill button-large">Confirmar Registro</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    `;
    app.popup.create({ content: popupHtml, swipeToClose: true }).open();
    
    $$('#form-transaction').on('submit', async (e) => {
        e.preventDefault();
        const d = {
            item_id: $$('#f-item').val(),
            type: $$('#f-type').val(),
            persona_id: $$('#f-persona').val(),
            area_id: $$('#f-area').val(),
            observaciones: $$('#f-obs').val()
        };

        if (d.type === 'SALIDA' && (state.inventoryMap[d.item_id]?.stock || 0) <= 0) {
            app.dialog.alert("ERROR: Stock insuficiente.");
            return;
        }

        try {
            const res = await fetch('/api/transactions', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(d)
            });
            if (res.ok) {
                app.popup.close();
                app.toast.create({ text: "Movimiento guardado", closeTimeout: 2000 }).open();
                fetchData();
            }
        } catch (err) { app.dialog.alert("Error de servidor"); }
    });
});

// --- HELPERS ---

window.viewTrace = (id) => {
    app.tab.show('#view-history');
    renderHistory(id);
};

window.logout = () => {
    localStorage.removeItem('inv_token');
    window.location.reload();
};

window.seedData = async () => {
    app.preloader.show();
    try {
        await fetch('/api/seed', { method: 'POST' });
        app.toast.create({ text: "Datos de prueba inyectados", closeTimeout: 2000 }).open();
        fetchData();
    } catch (e) { app.dialog.alert("Error"); }
    finally { app.preloader.hide(); }
};

// SW Registration
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js').catch(() => {});
    });
}