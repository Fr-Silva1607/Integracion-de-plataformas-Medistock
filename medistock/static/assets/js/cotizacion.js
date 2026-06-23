/* ── GENERADOR DE COTIZACIÓN PDF ── */

// Función mejorada para generar PDF con html2pdf
async function generarCotizacionPDF(cart, user) {
    if (!cart || cart.length === 0) {
        alert('Carrito vacío');
        return;
    }

    try {
        // Verificar que html2pdf está disponible
        if (typeof html2pdf === 'undefined' && !window.html2pdf) {
            alert('Nota: html2pdf no está instalado. Intenta con otro navegador o instala la librería.');
            return;
        }

        const fecha = new Date().toLocaleDateString('es-CL');
        const hora = new Date().toLocaleTimeString('es-CL');
        const subtotal = cart.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
        const iva = subtotal * 0.19;
        const total = subtotal + iva;

        // Crear elemento HTML para el PDF
        const element = document.createElement('div');
        element.innerHTML = `
            <div style="font-family: Arial, sans-serif; padding: 40px; background: white;">
                <!-- ENCABEZADO -->
                <div style="text-align: center; margin-bottom: 40px; border-bottom: 3px solid #667eea; padding-bottom: 20px;">
                    <h1 style="margin: 0 0 10px 0; color: #667eea; font-size: 28px;">COTIZACIÓN</h1>
                    <p style="margin: 0; color: #999; font-size: 14px;">MediStock - Comercializadora de Productos Médicos</p>
                </div>

                <!-- DATOS EMPRESA -->
                <div style="margin-bottom: 30px;">
                    <h3 style="margin-bottom: 15px; color: #333; font-size: 14px; font-weight: bold;">DATOS DE LA EMPRESA</h3>
                    <table style="width: 100%; font-size: 12px;">
                        <tr style="background-color: #f9f9f9;">
                            <td style="padding: 8px; width: 30%;"><strong>Empresa:</strong></td>
                            <td style="padding: 8px;">${user.nombre}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Email:</strong></td>
                            <td style="padding: 8px;">${user.email}</td>
                        </tr>
                        <tr style="background-color: #f9f9f9;">
                            <td style="padding: 8px;"><strong>Fecha de Emisión:</strong></td>
                            <td style="padding: 8px;">${fecha} - ${hora}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px;"><strong>Vigencia:</strong></td>
                            <td style="padding: 8px;">30 días desde la emisión</td>
                        </tr>
                    </table>
                </div>

                <!-- TABLA DE PRODUCTOS -->
                <div style="margin-bottom: 30px;">
                    <h3 style="margin-bottom: 15px; color: #333; font-size: 14px; font-weight: bold;">DETALLE DE PRODUCTOS</h3>
                    <table style="width: 100%; border-collapse: collapse; font-size: 11px;">
                        <thead>
                            <tr style="background-color: #667eea; color: white;">
                                <th style="padding: 10px; border: 1px solid #667eea; text-align: left;">Producto</th>
                                <th style="padding: 10px; border: 1px solid #667eea; text-align: center; width: 80px;">Cantidad</th>
                                <th style="padding: 10px; border: 1px solid #667eea; text-align: right; width: 100px;">Precio Unit.</th>
                                <th style="padding: 10px; border: 1px solid #667eea; text-align: right; width: 100px;">Subtotal</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${cart.map((item, idx) => `
                                <tr style="background-color: ${idx % 2 === 0 ? '#f9f9f9' : 'white';}">
                                    <td style="padding: 10px; border: 1px solid #ddd;">${item.nombre}</td>
                                    <td style="padding: 10px; border: 1px solid #ddd; text-align: center;">${item.cantidad}</td>
                                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">$${Number(item.precio).toLocaleString('es-CL')}</td>
                                    <td style="padding: 10px; border: 1px solid #ddd; text-align: right;">$${Number(item.precio * item.cantidad).toLocaleString('es-CL')}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                <!-- TOTALES -->
                <div style="text-align: right; margin-bottom: 30px;">
                    <table style="width: 350px; margin-left: auto; font-size: 12px;">
                        <tr style="background-color: #f9f9f9;">
                            <td style="padding: 8px; text-align: left;"><strong>Subtotal:</strong></td>
                            <td style="padding: 8px; text-align: right;">$${subtotal.toLocaleString('es-CL')}</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; text-align: left;"><strong>IVA (19%):</strong></td>
                            <td style="padding: 8px; text-align: right;">$${iva.toLocaleString('es-CL')}</td>
                        </tr>
                        <tr style="border-top: 3px solid #667eea; border-bottom: 3px solid #667eea;">
                            <td style="padding: 12px; text-align: left;"><strong style="font-size: 14px;">TOTAL:</strong></td>
                            <td style="padding: 12px; text-align: right; font-weight: bold; color: #667eea; font-size: 16px;">$${total.toLocaleString('es-CL')}</td>
                        </tr>
                    </table>
                </div>

                <!-- NOTAS -->
                <div style="background-color: #efe; padding: 15px; border-radius: 8px; border-left: 4px solid #27ae60; margin-bottom: 30px;">
                    <p style="margin: 0; font-size: 11px; color: #333; line-height: 1.6;">
                        <strong>✓ Validez:</strong> Esta cotización es válida por 30 días desde la fecha de emisión.<br>
                        <strong>✓ Confirmar:</strong> Para confirmar tu pedido, contacta directamente a nuestro equipo.<br>
                        <strong>✓ Condiciones:</strong> Sujeto a disponibilidad de stock y cambios sin previo aviso.
                    </p>
                </div>

                <!-- PIE DE PÁGINA -->
                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; font-size: 10px; color: #999;">
                    <p style="margin: 5px 0;">MediStock - Comercializadora de Productos Médicos</p>
                    <p style="margin: 5px 0;">Documento generado automáticamente</p>
                    <p style="margin: 5px 0;">Gracias por tu confianza</p>
                </div>
            </div>
        `;

        // Configurar opciones del PDF
        const opt = {
            margin: [10, 10, 10, 10],
            filename: `Cotizacion_${user.nombre.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`,
            image: { type: 'jpeg', quality: 0.98 },
            html2canvas: { scale: 2 },
            jsPDF: { orientation: 'portrait', unit: 'mm', format: 'a4' }
        };

        // Generar y descargar PDF
        if (window.html2pdf && typeof window.html2pdf === 'function') {
            window.html2pdf(element, opt);
        } else if (window.html2pdf && window.html2pdf.default) {
            window.html2pdf.default().set(opt).from(element).save();
        } else {
            console.error('html2pdf no disponible');
            alert('No se puede generar el PDF. Por favor intenta nuevamente.');
            return;
        }

        // Guardar cotización en BD después de generar PDF
        await saveCotizacionToDB(cart, user, total);

    } catch (err) {
        console.error('Error generando PDF:', err);
        alert('Error al generar la cotización');
    }
}

// Guardar cotización en base de datos
async function saveCotizacionToDB(cart, user, total) {
    try {
        if (!window.sb) {
            window.sb = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);
        }

        const sb = window.sb;

        const cotizacion = {
            empresa_id: user.id,
            estado: 'solicitada',
            items: cart,
            total: total,
            fecha_solicitud: new Date().toISOString(),
        };

        const { data, error } = await sb
            .from('cotizaciones')
            .insert([cotizacion]);

        if (error) {
            console.error('Error guardando cotización:', error);
        } else {
            console.log('✓ Cotización guardada en BD:', data);
        }
    } catch (err) {
        console.error('Error en saveCotizacionToDB:', err);
    }
}

// Función simple para descargar como texto (fallback)
function downloadCotizacionAsText(cart, user) {
    const fecha = new Date().toLocaleDateString('es-CL');
    const subtotal = cart.reduce((sum, item) => sum + (item.precio * item.cantidad), 0);
    const iva = subtotal * 0.19;
    const total = subtotal + iva;

    let contenido = `
COTIZACIÓN
================================================================================
MediStock - Comercializadora de Productos Médicos

DATOS DE LA EMPRESA
Empresa: ${user.nombre}
Email: ${user.email}
Fecha de Emisión: ${fecha}
Vigencia: 30 días

PRODUCTOS
================================================================================
`;

    cart.forEach((item, idx) => {
        contenido += `
${idx + 1}. ${item.nombre}
   Cantidad: ${item.cantidad}
   Precio Unit.: $${Number(item.precio).toLocaleString('es-CL')}
   Subtotal: $${Number(item.precio * item.cantidad).toLocaleString('es-CL')}
`;
    });

    contenido += `
================================================================================
TOTALES
Subtotal: $${subtotal.toLocaleString('es-CL')}
IVA (19%): $${iva.toLocaleString('es-CL')}
TOTAL: $${total.toLocaleString('es-CL')}

Documento generado automáticamente por MediStock
================================================================================
`;

    // Crear blob y descargar
    const blob = new Blob([contenido], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `Cotizacion_${user.nombre.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
}
