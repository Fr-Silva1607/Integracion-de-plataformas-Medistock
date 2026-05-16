/* ── CARRITO DE COMPRAS ── */

// Variable global para tracking del item que se está editando
let itemEditandoIdx = -1;

// Cargar y mostrar el carrito en la página
function loadCarritoPage() {
    const user = getCurrentUser();

    // Redirigir si no está logeado
    if (!user) {
        alert('Por favor inicia sesión primero');
        window.location.href = '/login/';
        return;
    }

    // Mostrar tipo de usuario
    const tipoUsuario = document.getElementById('tipo-usuario');
    const textoUsuario = document.getElementById('texto-usuario');
    if (tipoUsuario && textoUsuario) {
        tipoUsuario.style.display = 'block';
        const tipo = user.tipo === 'empresa' ? 'Empresa' : 'Persona';
        textoUsuario.innerHTML = `Compra como: <strong>${tipo}</strong>`;
    }

    // Cargar y mostrar carrito
    displayCarritoPage();

    // Mostrar botones según tipo
    configurarBotonesCarrito(user.tipo);
}

// Mostrar tabla de carrito
function displayCarritoPage() {
    const cart = loadCart();
    const tbody = document.getElementById('carrito-body');
    const carritoVacio = document.getElementById('carrito-vacio');
    const botonesPersonal = document.getElementById('botones-personal');
    const botonesEmpresa = document.getElementById('botones-empresa');

    if (cart.length === 0) {
        tbody.innerHTML = '';
        if (carritoVacio) carritoVacio.style.display = 'block';
        if (botonesPersonal) botonesPersonal.style.display = 'none';
        if (botonesEmpresa) botonesEmpresa.style.display = 'none';
        return;
    }

    if (carritoVacio) carritoVacio.style.display = 'none';

    tbody.innerHTML = cart.map((item, idx) => `
        <tr>
            <td class="col-imagen">
                <img src="${item.imagen_url || '/static/assets/img/placeholder.jpg'}" alt="${item.nombre}" class="img-carrito">
                <div>
                    <strong>${item.nombre}</strong>
                    <br>
                    <small class="text-muted">${item.categoria || ''}</small>
                </div>
            </td>
            <td class="col-precio">
                $${Number(item.precio).toLocaleString('es-CL')}
            </td>
            <td class="col-cantidad">
                <div class="cantidad-control">
                    <button onclick="decrementarCantidadCarrito(${idx})" class="btn-qty">-</button>
                    <input type="number" value="${item.cantidad}" min="1" readonly onclick="editarCantidad(${idx}, ${item.cantidad})">
                    <button onclick="incrementarCantidadCarrito(${idx})" class="btn-qty">+</button>
                </div>
            </td>
            <td class="col-subtotal">
                $${Number(item.precio * item.cantidad).toLocaleString('es-CL')}
            </td>
            <td class="col-acciones">
                <button onclick="eliminarDelCarrito(${idx})" class="btn-eliminar" title="Eliminar">
                    <i class="fa fa-trash"></i>
                </button>
            </td>
        </tr>
    `).join('');

    // Calcular totales
    calculateTotalsCarrito();
}

// Incrementar cantidad de un item
function incrementarCantidadCarrito(idx) {
    let cart = loadCart();
    if (idx >= 0 && idx < cart.length) {
        cart[idx].cantidad++;
        saveCart(cart);
        displayCarritoPage();
    }
}

// Decrementar cantidad de un item
function decrementarCantidadCarrito(idx) {
    let cart = loadCart();
    if (idx >= 0 && idx < cart.length && cart[idx].cantidad > 1) {
        cart[idx].cantidad--;
        saveCart(cart);
        displayCarritoPage();
    }
}

// Editar cantidad (abre modal)
function editarCantidad(idx, cantidadActual) {
    itemEditandoIdx = idx;
    document.getElementById('nueva-cantidad').value = cantidadActual;
    $('#modal-cantidad').modal('show');
}

// Confirmar cambio de cantidad
function confirmaCambioyCantidad() {
    const nuevaCantidad = parseInt(document.getElementById('nueva-cantidad').value);

    if (isNaN(nuevaCantidad) || nuevaCantidad < 1) {
        alert('Ingresa una cantidad válida');
        return;
    }

    let cart = loadCart();
    if (itemEditandoIdx >= 0 && itemEditandoIdx < cart.length) {
        cart[itemEditandoIdx].cantidad = nuevaCantidad;
        saveCart(cart);
        displayCarritoPage();
        $('#modal-cantidad').modal('hide');
        itemEditandoIdx = -1;
    }
}

// Eliminar item del carrito
function eliminarDelCarrito(idx) {
    if (confirm('¿Eliminar este producto del carrito?')) {
        let cart = loadCart();
        cart.splice(idx, 1);
        saveCart(cart);
        displayCarritoPage();
    }
}

// Calcular totales
function calculateTotalsCarrito() {
    const cart = loadCart();

    let subtotal = 0;
    cart.forEach(item => {
        subtotal += item.precio * item.cantidad;
    });

    const iva = subtotal * 0.19;
    const total = subtotal + iva;

    document.getElementById('subtotal').textContent = `$${subtotal.toLocaleString('es-CL')}`;
    document.getElementById('iva').textContent = `$${iva.toLocaleString('es-CL')}`;
    document.getElementById('total').textContent = `$${total.toLocaleString('es-CL')}`;

    // Guardar total global para usar en pago
    window.montoTotal = total;
}

// Actualizar carrito (refresca la página)
function actualizarCarrito() {
    displayCarritoPage();
    alert('✓ Carrito actualizado');
}

// Configurar botones según tipo de usuario
function configurarBotonesCarrito(tipoUsuario) {
    const botonesPersonal = document.getElementById('botones-personal');
    const botonesEmpresa = document.getElementById('botones-empresa');

    if (tipoUsuario === 'empresa') {
        if (botonesPersonal) botonesPersonal.style.display = 'none';
        if (botonesEmpresa) botonesEmpresa.style.display = 'block';
    } else {
        if (botonesPersonal) botonesPersonal.style.display = 'block';
        if (botonesEmpresa) botonesEmpresa.style.display = 'none';
    }
}

// Proceder al pago
async function procederAlPago() {
    const cart = loadCart();

    if (cart.length === 0) {
        alert('Tu carrito está vacío');
        return;
    }

    const user = getCurrentUser();

    try {
        // Inicializar Supabase si no está
        if (!window.sb) {
            window.sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
        }

        const sb = window.sb;

        // Crear orden
        const orden = {
            usuario_id: user.tipo === 'usuario' ? user.id : null,
            empresa_id: user.tipo === 'empresa' ? user.id : null,
            estado: 'pendiente',
            items: cart,
            total_items: cart.length,
            subtotal: calculateSubtotal(),
            iva: calculateSubtotal() * 0.19,
            total: window.montoTotal,
            tipo_orden: user.tipo,
            fecha_creacion: new Date().toISOString(),
            metodo_pago: 'transbank',
        };

        const { data, error } = await sb
            .from('ordenes')
            .insert([orden])
            .select();

        if (error) {
            throw error;
        }

        // Guardar ID de orden en sesión
        localStorage.setItem('medistock_orden_actual', JSON.stringify(data[0]));

        // Redirigir a pago
        window.location.href = `/pago/?orden=${data[0].id}`;
    } catch (err) {
        console.error('Error al procesar orden:', err);
        alert('Error al procesar tu compra. Intenta nuevamente.');
    }
}

// Calcular subtotal
function calculateSubtotal() {
    const cart = loadCart();
    return cart.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
}

// Vaciar carrito
function vaciarCarrito() {
    if (confirm('¿Estás seguro de que deseas vaciar el carrito?')) {
        const key = getCartKey();
        if (key) {
            localStorage.removeItem(key);
            displayCarritoPage();
            alert('Carrito vaciado');
        }
    }
}

// Generar cotización (función llamada desde carrito.html)
function generarCotizacion() {
    const cart = loadCart();

    if (cart.length === 0) {
        alert('Tu carrito está vacío');
        return;
    }

    // Crear contenido HTML del PDF
    const user = getCurrentUser();
    const fecha = new Date().toLocaleDateString('es-CL');
    const hora = new Date().toLocaleTimeString('es-CL');

    let htmlContent = `
        <div style="font-family: Arial, sans-serif; padding: 20px; max-width: 800px;">
            <div style="text-align: center; margin-bottom: 30px; border-bottom: 3px solid #667eea; padding-bottom: 20px;">
                <h1 style="margin: 0; color: #667eea;">COTIZACIÓN</h1>
                <p style="margin: 5px 0; color: #999;">MediStock - Comercializadora de Productos Médicos</p>
            </div>

            <div style="margin-bottom: 30px;">
                <h3 style="margin-bottom: 15px; color: #333;">Datos de Empresa</h3>
                <table style="width: 100%;">
                    <tr>
                        <td style="padding: 5px;"><strong>Razón Social:</strong></td>
                        <td>${user.nombre}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Email:</strong></td>
                        <td>${user.email}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Fecha de Cotización:</strong></td>
                        <td>${fecha} ${hora}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><strong>Vigencia:</strong></td>
                        <td>30 días desde la emisión</td>
                    </tr>
                </table>
            </div>

            <div style="margin-bottom: 30px;">
                <h3 style="margin-bottom: 15px; color: #333;">Productos</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <thead>
                        <tr style="background-color: #f0f0f0;">
                            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">Producto</th>
                            <th style="padding: 10px; border: 1px solid #ddd; text-align: center;">Cantidad</th>
                            <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Precio Unit.</th>
                            <th style="padding: 10px; border: 1px solid #ddd; text-align: right;">Subtotal</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${cart.map(item => `
                            <tr>
                                <td style="padding: 10px; border: 1px solid #ddd;">${item.nombre}</td>
                                <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${item.cantidad}</td>
                                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">$${Number(item.precio).toLocaleString('es-CL')}</td>
                                <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">$${Number(item.precio * item.cantidad).toLocaleString('es-CL')}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>

            <div style="text-align: right; margin-bottom: 30px;">
                <table style="width: 300px; margin-left: auto;">
                    <tr>
                        <td><strong>Subtotal:</strong></td>
                        <td style="text-align: right;">$${calculateSubtotal().toLocaleString('es-CL')}</td>
                    </tr>
                    <tr>
                        <td><strong>IVA (19%):</strong></td>
                        <td style="text-align: right;">$${(calculateSubtotal() * 0.19).toLocaleString('es-CL')}</td>
                    </tr>
                    <tr style="border-top: 2px solid #667eea;">
                        <td><strong style="font-size: 16px;">Total:</strong></td>
                        <td style="text-align: right; font-size: 16px; font-weight: bold; color: #667eea;">$${window.montoTotal.toLocaleString('es-CL')}</td>
                    </tr>
                </table>
            </div>

            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; border-left: 4px solid #667eea;">
                <p style="margin: 0; font-size: 12px; color: #666;">
                    <strong>Condiciones:</strong> Esta cotización es válida por 30 días desde la emisión.
                    Para confirmar tu pedido, por favor contáctanos a través de nuestro sitio web o por email.
                </p>
            </div>

            <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; font-size: 12px; color: #999;">
                <p>MediStock - Comercializadora de Productos Médicos</p>
                <p>Gracias por tu confianza</p>
            </div>
        </div>
    `;

    // Usar html2pdf si está disponible, si no avisar
    if (typeof html2pdf === 'undefined') {
        // Fallback: descargar como texto
        const element = document.createElement('div');
        element.innerHTML = htmlContent;

        const opt = {
            margin: 10,
            filename: `cotizacion-${user.nombre.replace(/\s+/g, '_')}-${new Date().toISOString().split('T')[0]}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { orientation: 'portrait', unit: 'mm', format: 'a4' }
        };

        // Si html2pdf está disponible, usarlo
        if (window.html2pdf && window.html2pdf.default) {
            window.html2pdf.default().set(opt).from(element).save();
        } else {
            // Fallback: mostrar advertencia
            alert('Para descargar la cotización en PDF, necesitas instalar html2pdf');
            // Alternativamente, podrías abrir una nueva ventana con el contenido
            window.open().document.write(htmlContent);
        }
    }

    // Guardar cotización en Supabase
    saveCotizacion(cart, user);
}

// Guardar cotización en Supabase
async function saveCotizacion(cart, user) {
    try {
        if (!window.sb) {
            window.sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
        }

        const sb = window.sb;

        const cotizacion = {
            empresa_id: user.id,
            estado: 'solicitada',
            items: cart,
            total: window.montoTotal,
            fecha_solicitud: new Date().toISOString(),
        };

        const { error } = await sb
            .from('cotizaciones')
            .insert([cotizacion]);

        if (!error) {
            console.log('Cotización guardada correctamente');
        }
    } catch (err) {
        console.error('Error guardando cotización:', err);
    }
}
