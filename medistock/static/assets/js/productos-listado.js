/* ── LISTADO DE PRODUCTOS CORRECTO Y BLINDADO ── */

let allProductosListado = [];

// Inicializar la página de productos
async function initProductosListado() {
    await loadProductosListado();
    setupFiltrosListado();
}

// Cargar productos desde Supabase
async function loadProductosListado() {
    const grid = document.getElementById('productos-grid');
    const loading = document.getElementById('loading-state');
    const emptyState = document.getElementById('empty-state');

    try {
        // Validación de seguridad para comprobar si existe la conexión con Supabase
        if (typeof sb === 'undefined') {
            throw new Error("El cliente de Supabase ('sb') no está definido. Asegúrate de cargarlo en el HTML.");
        }

        const { data, error } = await sb
            .from('productos')
            .select('*')
            .order('nombre', { ascending: true });

        if (error) throw error;

        if (!data || data.length === 0) {
            if (loading) loading.style.display = 'none';
            if (emptyState) emptyState.style.display = 'block';
            return;
        }

        // SOLUCIÓN AL ERROR CRÍTICO: Eliminamos la función inexistente 'filterProductosByType' 
        // Asignamos directamente la data limpia a nuestra variable de control global
        allProductosListado = data;

        // Construir lista de categorías para el filtro
        buildCategoriasFiltro(allProductosListado);

        // Mostrar productos y apagar el loading de inmediato
        if (loading) loading.style.display = 'none';
        displayProductosListado(allProductosListado);

    } catch (err) {
        console.error('Error cargando productos:', err);
        if (loading) loading.style.display = 'none';
        if (grid) {
            grid.innerHTML = `
                <div class="error-state" style="text-align: center; padding: 2rem; color: #e74c3c;">
                    <i class="fa fa-exclamation-triangle fa-2x"></i>
                    <p>No se pudieron cargar los productos.<br>
                       <small>${err.message || 'Error de conexión'}</small>
                    </p>
                </div>`;
        }
    }
}

// Construir lista de categorías para el filtro limpiando espacios invisibles
function buildCategoriasFiltro(productos) {
    const select = document.getElementById('categoria');
    if (!select) return;

    // Extraemos las categorías pasándolas a minúsculas y removiendo espacios raros (ej: "insumo " -> "insumo")
    const categorias = [...new Set(productos.map(p => p.categoria ? p.categoria.trim().toLowerCase() : ''))].filter(Boolean).sort();

    // Limpiar opciones excepto "Todas"
    select.innerHTML = '<option value="">Todas</option>';
    categorias.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        // Capitalizamos la primera letra de manera estética en el select
        option.textContent = cat.charAt(0).toUpperCase() + cat.slice(1);
        select.appendChild(option);
    });
}

// Mostrar productos en grid
function displayProductosListado(productos) {
    const grid = document.getElementById('productos-grid');
    const emptyState = document.getElementById('empty-state');

    if (!grid) return;

    if (productos.length === 0) {
        grid.innerHTML = '';
        if (emptyState) emptyState.style.display = 'block';
        return;
    }

    if (emptyState) emptyState.style.display = 'none';

    grid.innerHTML = productos.map(p => {
        const img = p.imagen_url || 'https://via.placeholder.com/280x220?text=Sin+imagen';
        const stockBajo = (p.cantidad || 0) <= 5 && (p.cantidad || 0) > 0;
        const sinStock = (p.cantidad || 0) <= 0;

        return `
            <div class="producto-card" onclick="window.location.href='/producto/${p.id}/'" style="cursor: pointer; border: 1px solid #ddd; padding: 15px; margin: 10px; background: white; border-radius: 8px; display: inline-block; width: 280px; vertical-align: top; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: left;">
                <div class="producto-image" style="position: relative; text-align: center;">
                    <img src="${img}" alt="${p.nombre}" style="width: 100%; height: 200px; object-fit: contain; border-bottom: 1px solid #eee; padding-bottom: 10px;">
                    ${p.etiqueta_precio ? `<span class="producto-badge" style="position: absolute; top: 10px; left: 10px; background: #2ecc71; color: white; padding: 3px 8px; font-size: 0.75rem; border-radius: 3px;">${p.etiqueta_precio}</span>` : ''}
                    ${p.tipo_venta === 'empresa' ? '<span class="producto-badge badge-empresa" style="position: absolute; top: 10px; right: 10px; background: #e67e22; color: white; padding: 3px 8px; font-size: 0.75rem; border-radius: 3px;">EMPRESAS</span>' : ''}
                </div>
                <div class="producto-content" style="padding: 10px 0;">
                    <h3 class="producto-name" style="margin: 10px 0 5px 0; font-size: 1.2rem; color: #333;">${p.nombre}</h3>
                    <p class="producto-description" style="color: #666; font-size: 0.9rem; height: 50px; overflow: hidden; margin-bottom: 10px;">${p.descripcion || 'Producto MediStock'}</p>

                    <div class="producto-price-section" style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 10px;">
                        <div class="producto-price" style="display: flex; flex-direction: column;">
                            <span class="product-price-unit" style="color: #888; font-size: 0.8rem;">${p.etiqueta_precio || 'Precio'}</span>
                            <span class="product-price-value" style="font-weight: bold; color: #2ecc71; font-size: 1.1rem;">$${Number(p.precio).toLocaleString('es-CL')}</span>
                        </div>
                        <div class="product-stock ${stockBajo ? 'low' : ''} ${sinStock ? 'out' : ''}" style="font-size: 0.85rem; color: ${sinStock ? '#e74c3c' : (stockBajo ? '#f39c12' : '#27ae60')}; font-weight: bold;">
                            ${sinStock ? 'Agotado' : `Stock: ${p.cantidad}`}
                        </div>
                    </div>

                    <div class="producto-buttons" onclick="event.stopPropagation();" style="display: flex; gap: 10px; margin-top: 15px;">
                        <button class="btn-carrito" onclick="agregarRapido(${p.id})" ${sinStock ? 'disabled' : ''} style="flex: 1; padding: 8px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer;">
                            <i class="fa fa-shopping-cart"></i> Carrito
                        </button>
                        <a href="/producto/${p.id}/" class="btn-detalles" style="flex: 1; padding: 8px; background: #eee; color: #333; text-align: center; text-decoration: none; border-radius: 4px; font-size: 0.9rem;">
                            <i class="fa fa-eye"></i> Detalles
                        </a>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// Agregar rápido al carrito (desde botón en listado)
async function agregarRapido(productoId) {
    // Verificación segura para evitar caídas si las funciones de sesión no existen aún
    if (typeof getCurrentUser !== 'function') {
        alert('Módulo de autenticación no cargado.');
        return;
    }

    const user = getCurrentUser();
    if (!user) {
        alert('Por favor inicia sesión primero');
        window.location.href = '/login/';
        return;
    }

    const producto = allProductosListado.find(p => p.id === productoId);
    if (!producto) {
        alert('Producto no encontrado');
        return;
    }

    if (producto.tipo_venta === 'empresa' && user.tipo !== 'empresa') {
        alert('Este producto está disponible solo para empresas');
        return;
    }

    if (typeof addToCart === 'function') {
        addToCart(producto);
    } else {
        alert('Producto seleccionado: ' + producto.nombre + '. (Módulo de carrito en desarrollo)');
    }
}

// Configurar filtros listeners
function setupFiltrosListado() {
    const buscar = document.getElementById('buscar');
    const categoria = document.getElementById('categoria');
    const precio = document.getElementById('precio');
    const ordenar = document.getElementById('ordenar');

    // Cambiamos a eventos nativos estables ('input' y 'change')
    if (buscar) buscar.addEventListener('input', applyFiltrosListado);
    if (categoria) categoria.addEventListener('change', applyFiltrosListado);
    if (precio) precio.addEventListener('input', applyFiltrosListado);
    if (ordenar) ordenar.addEventListener('change', applyFiltrosListado);
}

// Aplicar filtros y mostrar resultados de forma limpia y tolerante a espacios
function applyFiltrosListado() {
    const buscarVal = (document.getElementById('buscar')?.value || '').toLowerCase().trim();
    const categoriaVal = (document.getElementById('categoria')?.value || '').trim().toLowerCase();
    const precioMax = parseInt(document.getElementById('precio')?.value) || Infinity;
    const ordenarVal = document.getElementById('ordenar')?.value || 'nombre';

    let filtered = allProductosListado.filter(p => {
        // Filtro por nombre o descripción
        if (buscarVal && !p.nombre.toLowerCase().includes(buscarVal) &&
            !(p.descripcion || '').toLowerCase().includes(buscarVal)) {
            return false;
        }
        
        // SOLUCIÓN AL ESPACIO BLANCO: Sincronizamos la comparación de categorías en minúscula limpia
        const pCatLimpia = p.categoria ? p.categoria.trim().toLowerCase() : '';
        if (categoriaVal && pCatLimpia !== categoriaVal) {
            return false;
        }
        
        // Filtro por precio máximo
        if (Number(p.precio) > precioMax) {
            return false;
        }
        return true;
    });

    // Ordenar
    switch (ordenarVal) {
        case 'precio-asc':
            filtered.sort((a, b) => Number(a.precio) - Number(b.precio));
            break;
        case 'precio-desc':
            filtered.sort((a, b) => Number(b.precio) - Number(a.precio));
            break;
        default:
            filtered.sort((a, b) => (a.nombre || '').localeCompare(b.nombre || ''));
    }

    displayProductosListado(filtered);
}