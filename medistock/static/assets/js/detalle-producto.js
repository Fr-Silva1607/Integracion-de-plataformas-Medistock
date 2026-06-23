/* ── DETALLE DE PRODUCTO ── */

const SUPABASE_URL = document.currentScript.dataset.supabaseUrl || '{{ SUPABASE_URL }}';
const SUPABASE_KEY = document.currentScript.dataset.supabaseKey || '{{ SUPABASE_KEY }}';

let sb = null;
let productoActual = null;

// Inicializar Supabase si no está ya inicializado
function initSupabase() {
    if (!window.supabase || !sb) {
        sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
    }
    return sb;
}

// Cargar producto desde Supabase
async function loadProducto(id) {
    try {
        initSupabase();

        const { data, error } = await sb
            .from('productos')
            .select('*')
            .eq('id', id)
            .single();

        if (error || !data) {
            alert('Producto no encontrado');
            window.location.href = '/productos/';
            return;
        }

        productoActual = data;
        displayProducto(data);
    } catch (err) {
        console.error('Error cargando producto:', err);
        alert('Error al cargar el producto');
    }
}

// Mostrar datos del producto en la página
function displayProducto(producto) {
    // Nombre y breadcrumb
    document.getElementById('producto-nombre').textContent = producto.nombre;
    document.getElementById('breadcrumb-nombre').textContent = producto.nombre;

    // Categoría
    document.getElementById('categoria').textContent = producto.categoria || 'General';

    // Imagen
    const imgPrincipal = document.getElementById('imagen-principal');
    if (producto.imagen_url) {
        imgPrincipal.src = producto.imagen_url;
        imgPrincipal.alt = producto.nombre;
    }

    // Etiqueta de precio (OFERTA, NUEVO, etc)
    const etiqueta = document.getElementById('etiqueta-precio');
    if (producto.etiqueta_precio) {
        etiqueta.textContent = producto.etiqueta_precio;
        etiqueta.style.display = 'block';
    }

    // Precio
    const precioEl = document.getElementById('precio');
    precioEl.textContent = `$${Number(producto.precio).toLocaleString('es-CL')}`;

    // Stock
    const stockEl = document.getElementById('stock-text');
    if (producto.cantidad > 0) {
        stockEl.textContent = `Stock disponible: ${producto.cantidad} unidades`;
        stockEl.className = 'stock-disponible';
    } else {
        stockEl.textContent = 'Producto agotado';
        stockEl.className = 'stock-agotado';
        document.getElementById('btn-compra-personal').disabled = true;
        document.getElementById('btn-compra-empresa').disabled = true;
    }

    // Descripción
    document.getElementById('descripcion').textContent = producto.descripcion || 'Descripción no disponible';

    // Especificaciones (datos simulados)
    displayEspecificaciones(producto);

    // Reseñas (datos simulados)
    displayResenas();

    // Productos relacionados
    loadProductosRelacionados(producto.categoria, producto.id);

    // Mostrar/ocultar botones según tipo_venta
    configurarBotonesCompra(producto.tipo_venta);

    // Rating simulado
    displayRating();
}

// Mostrar especificaciones
function displayEspecificaciones(producto) {
    const tabla = document.getElementById('especificaciones-tabla');
    const especificaciones = [
        { label: 'Código de producto', valor: `MED-${producto.id}` },
        { label: 'Categoría', valor: producto.categoria || 'N/A' },
        { label: 'Marca', valor: 'MediStock' },
        { label: 'Stock disponible', valor: `${producto.cantidad} unidades` },
    ];

    tabla.innerHTML = especificaciones.map(e => `
        <tr>
            <td><strong>${e.label}</strong></td>
            <td>${e.valor}</td>
        </tr>
    `).join('');
}

// Mostrar reseñas (datos fake)
function displayResenas() {
    const resenas = [
        { nombre: 'Juan García', stars: 5, comentario: 'Excelente producto, muy recomendado' },
        { nombre: 'María López', stars: 5, comentario: 'Llegó rápido y en perfecto estado' },
        { nombre: 'Carlos Rodríguez', stars: 4, comentario: 'Buen producto, excelente calidad' },
        { nombre: 'Ana Martínez', stars: 5, comentario: 'Superó mis expectativas' },
    ];

    const container = document.getElementById('resenas-lista');
    container.innerHTML = resenas.map(r => `
        <div class="resena-item">
            <div class="resena-header">
                <strong>${r.nombre}</strong>
                <div class="resena-stars">
                    ${Array(r.stars).fill('<i class="fa fa-star"></i>').join('')}
                    ${Array(5 - r.stars).fill('<i class="fa fa-star-o"></i>').join('')}
                </div>
            </div>
            <p class="resena-texto">${r.comentario}</p>
        </div>
    `).join('');
}

// Rating simulado
function displayRating() {
    const ratingValue = 4.5;
    const ratingStars = document.getElementById('rating-stars');

    let starsHTML = '';
    for (let i = 1; i <= 5; i++) {
        if (i <= ratingValue) {
            starsHTML += '<i class="fa fa-star"></i>';
        } else if (i - 0.5 <= ratingValue) {
            starsHTML += '<i class="fa fa-star-half-o"></i>';
        } else {
            starsHTML += '<i class="fa fa-star-o"></i>';
        }
    }

    ratingStars.innerHTML = starsHTML;
    document.getElementById('rating-text').textContent = `(${Math.round(ratingValue * 10) / 10} de 5 - 234 reseñas)`;
}

// Configurar botones según tipo_venta y estado de login
function configurarBotonesCompra(tipoVenta) {
    const btnPersonal = document.getElementById('btn-compra-personal');
    const btnEmpresa = document.getElementById('btn-compra-empresa');

    const user = (typeof getCurrentUser === 'function') ? getCurrentUser() : null;
    const isLogged = !!user;
    const tipoUsuario = user ? user.tipo : null;

    // Resetear: ocultar ambos por defecto
    btnPersonal.style.display = 'none';
    btnEmpresa.style.display = 'none';

    if (!isLogged) {
        // No logeado: mostrar según tipo_venta del producto (ambos si "ambos")
        if (tipoVenta === 'personal' || tipoVenta === 'ambos' || tipoVenta === 'libre') {
            btnPersonal.style.display = 'block';
        }
        if (tipoVenta === 'empresa' || tipoVenta === 'ambos') {
            btnEmpresa.style.display = 'block';
        }

        // Cambiar texto a "Comprar" simple si no logeado (llevará a login)
        btnPersonal.innerHTML = '<i class="fa fa-shopping-cart"></i> Comprar';
        btnEmpresa.innerHTML = '<i class="fa fa-building"></i> Comprar Empresa';
        return;
    }

    // Logeado: mostrar UN SOLO botón "Comprar" según su tipo
    if (tipoUsuario === 'empresa') {
        // Empresa solo ve botón de empresa (si producto lo permite)
        if (tipoVenta === 'empresa' || tipoVenta === 'ambos' || tipoVenta === 'personal' || tipoVenta === 'libre') {
            btnEmpresa.style.display = 'block';
            btnEmpresa.innerHTML = '<i class="fa fa-shopping-cart"></i> Comprar';
        }
    } else {
        // Usuario personal solo ve botón personal
        if (tipoVenta === 'personal' || tipoVenta === 'ambos' || tipoVenta === 'libre') {
            btnPersonal.style.display = 'block';
            btnPersonal.innerHTML = '<i class="fa fa-shopping-cart"></i> Comprar';
        }
    }
}

// Cargar productos relacionados
async function loadProductosRelacionados(categoria, productoId) {
    try {
        initSupabase();

        const { data, error } = await sb
            .from('productos')
            .select('id, nombre, precio, imagen_url, etiqueta_precio')
            .eq('categoria', categoria)
            .neq('id', productoId)
            .limit(4);

        if (error || !data) return;

        displayProductosRelacionados(data);
    } catch (err) {
        console.error('Error cargando productos relacionados:', err);
    }
}

// Mostrar productos relacionados
function displayProductosRelacionados(productos) {
    const container = document.getElementById('productos-relacionados');

    if (productos.length === 0) {
        container.innerHTML = '<p>No hay productos relacionados</p>';
        return;
    }

    container.innerHTML = `
        <div class="grid-productos">
            ${productos.map(p => `
                <div class="producto-card-relacionado">
                    <div class="imagen">
                        <img src="${p.imagen_url}" alt="${p.nombre}">
                        ${p.etiqueta_precio ? `<span class="etiqueta">${p.etiqueta_precio}</span>` : ''}
                    </div>
                    <h5>${p.nombre}</h5>
                    <p class="precio">$${Number(p.precio).toLocaleString('es-CL')}</p>
                    <a href="/producto/?id=${p.id}" class="btn btn-sm btn-primary">Ver detalle</a>
                </div>
            `).join('')}
        </div>
    `;
}

// ── INTERACCIÓN DEL USUARIO ──

// Incrementar cantidad
function incrementarCantidad() {
    const input = document.getElementById('cantidad');
    const maxCantidad = productoActual.cantidad;
    if (parseInt(input.value) < maxCantidad) {
        input.value = parseInt(input.value) + 1;
    }
}

// Decrementar cantidad
function decrementarCantidad() {
    const input = document.getElementById('cantidad');
    if (parseInt(input.value) > 1) {
        input.value = parseInt(input.value) - 1;
    }
}

// Agregar al carrito (personal)
function agregarAlCarritoPersonal() {
    if (!productoActual) return;

    const cantidad = parseInt(document.getElementById('cantidad').value) || 1;
    const user = getCurrentUser();

    if (!user) {
        alert('Por favor inicia sesión primero');
        window.location.href = '/login/';
        return;
    }

    let cart = loadCart();

    const exists = cart.find(item => item.id === productoActual.id);
    if (exists) {
        exists.cantidad += cantidad;
    } else {
        cart.push({
            id: productoActual.id,
            nombre: productoActual.nombre,
            precio: productoActual.precio,
            cantidad: cantidad,
            imagen_url: productoActual.imagen_url,
            categoria: productoActual.categoria,
        });
    }

    saveCart(cart);
    alert(`✓ ${productoActual.nombre} agregado al carrito (x${cantidad})`);

    // Resetear cantidad
    document.getElementById('cantidad').value = '1';
}

// Agregar al carrito (empresa)
function agregarAlCarritoEmpresa() {
    if (!productoActual) return;

    const cantidad = parseInt(document.getElementById('cantidad').value) || 1;
    const user = getCurrentUser();

    if (!user) {
        alert('Por favor inicia sesión primero');
        window.location.href = '/login/';
        return;
    }

    if (user.tipo !== 'empresa') {
        alert('Solo empresas pueden usar la compra empresa');
        return;
    }

    let cart = loadCart();

    const exists = cart.find(item => item.id === productoActual.id);
    if (exists) {
        exists.cantidad += cantidad;
    } else {
        cart.push({
            id: productoActual.id,
            nombre: productoActual.nombre,
            precio: productoActual.precio,
            cantidad: cantidad,
            imagen_url: productoActual.imagen_url,
            categoria: productoActual.categoria,
        });
    }

    saveCart(cart);
    alert(`✓ ${productoActual.nombre} agregado al carrito empresa (x${cantidad})`);

    // Resetear cantidad
    document.getElementById('cantidad').value = '1';
}

// Set rating (en formulario de reseña)
let ratingSeleccionado = 0;
function setRating(value) {
    ratingSeleccionado = value;
    const stars = document.querySelectorAll('.stars-input i');
    stars.forEach((star, idx) => {
        if (idx < value) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}
