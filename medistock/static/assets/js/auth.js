/* ── AUTENTICACIÓN Y SESIÓN ── */

// Obtiene la sesión actual del localStorage
function getCurrentUser() {
    const session = localStorage.getItem('medistock_session');
    return session ? JSON.parse(session) : null;
}

// Verifica si el usuario está logeado
function isLoggedIn() {
    return getCurrentUser() !== null;
}

// Obtiene el tipo de usuario ('usuario' o 'empresa')
function getUserType() {
    const user = getCurrentUser();
    return user ? user.tipo : null;
}

// Obtiene el nombre del usuario
function getUserName() {
    const user = getCurrentUser();
    return user ? user.nombre : null;
}

// Verifica si el usuario es empresa
function isEmpresa() {
    return getUserType() === 'empresa';
}

// Actualiza el navbar con la información del usuario
function updateNavbar() {
    const user = getCurrentUser();
    const perfilDiv = document.getElementById('navbar-perfil');
    const loginDiv = document.getElementById('navbar-login');
    const userNombreSpan = document.getElementById('user-nombre');

    if (user) {
        // Usuario logeado: mostrar perfil, ocultar login
        if (loginDiv) loginDiv.style.display = 'none';
        if (perfilDiv) perfilDiv.style.display = 'block';
        if (userNombreSpan) userNombreSpan.textContent = user.nombre;

        updateCartCount();
    } else {
        // Usuario no logeado: mostrar login, ocultar perfil
        if (perfilDiv) perfilDiv.style.display = 'none';
        if (loginDiv) loginDiv.style.display = 'block';
    }
}

// Actualiza el badge del carrito con el número de items
function updateCartCount() {
    const user = getCurrentUser();
    if (!user) return;

    const cartKey = user.tipo === 'empresa'
        ? 'medistock_cart_empresa'
        : 'medistock_cart_personal';

    const cart = JSON.parse(localStorage.getItem(cartKey) || '[]');
    const badge = document.getElementById('cart-badge');
    if (badge) {
        badge.textContent = cart.length;
    }
}

// Cierra la sesión del usuario
function logout() {
    if (confirm('¿Estás seguro de que deseas cerrar sesión?')) {
        localStorage.removeItem('medistock_session');
        localStorage.removeItem('medistock_cart_personal');
        localStorage.removeItem('medistock_cart_empresa');

        // Redirigir a inicio
        window.location.href = '/';
    }
}

// Obtiene la clave del carrito según el tipo de usuario
function getCartKey() {
    const user = getCurrentUser();
    if (!user) {
        return null;
    }
    return user.tipo === 'empresa'
        ? 'medistock_cart_empresa'
        : 'medistock_cart_personal';
}

// Carga el carrito del usuario
function loadCart() {
    const key = getCartKey();
    if (!key) return [];
    return JSON.parse(localStorage.getItem(key) || '[]');
}

// Guarda el carrito del usuario
function saveCart(cart) {
    const key = getCartKey();
    if (!key) return false;
    localStorage.setItem(key, JSON.stringify(cart));
    updateCartCount();
    return true;
}

// Agrega un item al carrito
function addToCart(producto) {
    const user = getCurrentUser();

    if (!user) {
        alert('Por favor inicia sesión primero');
        window.location.href = '/login/';
        return;
    }

    let cart = loadCart();

    const exists = cart.find(item => item.id === producto.id);
    if (exists) {
        exists.cantidad++;
    } else {
        cart.push({
            id: producto.id,
            nombre: producto.nombre,
            precio: producto.precio,
            cantidad: 1,
            imagen_url: producto.imagen_url || '',
            categoria: producto.categoria || '',
        });
    }

    saveCart(cart);
    alert('✓ Producto agregado al carrito');
}

// Valida que el usuario sea empresa antes de agregar al carrito como empresa
function addToCartAsEmpresa(producto) {
    const user = getCurrentUser();

    if (!user) {
        alert('Por favor inicia sesión primero');
        window.location.href = '/login/';
        return;
    }

    if (user.tipo !== 'empresa') {
        alert('Solo empresas pueden comprar en modo empresa. Por favor registra tu empresa.');
        return;
    }

    let cart = loadCart();

    const exists = cart.find(item => item.id === producto.id);
    if (exists) {
        exists.cantidad++;
    } else {
        cart.push({
            id: producto.id,
            nombre: producto.nombre,
            precio: producto.precio,
            cantidad: 1,
            imagen_url: producto.imagen_url || '',
            categoria: producto.categoria || '',
        });
    }

    saveCart(cart);
    alert('✓ Producto agregado al carrito (Compra Empresa)');
}

// Redirige a login si no está logeado
function requireLogin() {
    if (!isLoggedIn()) {
        window.location.href = '/login/';
        return false;
    }
    return true;
}

// Redirige a login si no es empresa
function requireEmpresa() {
    if (!isLoggedIn() || !isEmpresa()) {
        alert('Solo empresas pueden acceder a esta sección');
        window.location.href = '/';
        return false;
    }
    return true;
}

// Obtiene el tipo de venta permitido para el usuario
function getAllowedSaleTypes() {
    const user = getCurrentUser();

    if (!user) {
        // No logeado: solo ve productos 'personal' y 'ambos'
        return ['personal', 'ambos'];
    }

    if (user.tipo === 'empresa') {
        // Empresa: ve todos los tipos
        return ['personal', 'empresa', 'ambos'];
    }

    // Usuario personal: ve 'personal' y 'ambos'
    return ['personal', 'ambos'];
}

// Filtra productos según tipo_venta y estado del usuario
function filterProductosByType(productos) {
    const allowedTypes = getAllowedSaleTypes();
    return productos.filter(p => allowedTypes.includes(p.tipo_venta));
}
