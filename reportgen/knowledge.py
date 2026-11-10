"""Explicaciones en lenguaje simple para cada tipo de hallazgo, pensadas para el cliente final."""
from __future__ import annotations

from dataclasses import dataclass

EFFORT = {1: "Rápido · minutos", 2: "Moderado · horas", 3: "Mayor · días"}
WHO = {
    "hosting": "Quien administra el hosting o servidor",
    "dev": "Quien desarrolla o mantiene el sitio web",
    "dns": "Quien administra el dominio y el correo",
    "ti": "Equipo técnico / proveedor web",
}


@dataclass(frozen=True)
class Category:
    key: str
    name: str
    blurb: str
    icon: str
    checks: frozenset[str]


CATEGORIES: dict[str, Category] = {c.key: c for c in [
    Category("https", "Conexión segura (HTTPS)",
             "Que lo que viaja entre tus visitantes y el sitio vaya cifrado, y que el sitio sea auténtico.",
             '<rect x="5" y="11" width="14" height="9" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/>',
             frozenset({"tls", "transport"})),
    Category("headers", "Escudos del navegador",
             "Instrucciones que el sitio le da al navegador para defenderse de ataques comunes.",
             '<path d="M12 3l7 3v5c0 4.5-3 8-7 10-4-2-7-5.5-7-10V6z"/>',
             frozenset({"headers"})),
    Category("cookies", "Sesiones y cookies",
             "Cómo se protegen los datos que recuerdan quién es cada visitante.",
             '<circle cx="12" cy="12" r="9"/><circle cx="9" cy="10" r="1"/><circle cx="14" cy="14" r="1"/>'
             '<circle cx="15" cy="9" r="1"/>',
             frozenset({"cookies"})),
    Category("cors", "Acceso desde otros sitios",
             "Qué otras páginas web pueden pedirle datos a tu sitio.",
             '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
             frozenset({"cors"})),
    Category("content", "Contenido y formularios",
             "Cómo está construida la página: formularios, scripts externos y datos visibles en el código.",
             '<rect x="4" y="4" width="16" height="16" rx="2"/><path d="M8 9h8M8 13h8M8 17h5"/>',
             frozenset({"content"})),
    Category("email", "Correo y dominio",
             "Que nadie pueda enviar correos falsos haciéndose pasar por tu empresa.",
             '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
             frozenset({"dns"})),
    Category("exposure", "Archivos expuestos",
             "Archivos internos que no deberían poder verse desde internet.",
             '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
             frozenset({"exposure"})),
    Category("ports", "Puertas de red (puertos)",
             "Qué servicios de tus equipos quedan visibles desde la red y si alguno no debería estarlo.",
             '<rect x="4" y="6" width="16" height="12" rx="2"/><path d="M8 10h.01M12 10h.01M16 10h.01M8 14h8"/>',
             frozenset({"tcp-connect", "tcp-syn", "udp", "service-detection", "host-discovery"})),
    Category("active", "Pruebas avanzadas",
             "Pruebas controladas que simulan ataques reales contra los formularios y parámetros.",
             '<path d="M13 2L4 14h7l-1 8 9-12h-7z"/>',
             frozenset({"xss_reflected", "sqli", "open_redirect", "cmd_injection", "ssti"})),
    Category("other", "Otros hallazgos",
             "Puntos detectados que no encajan en las categorías anteriores.",
             '<circle cx="12" cy="12" r="9"/><path d="M12 8v5M12 16v.5"/>',
             frozenset()),
]}

_PREFIX_CATEGORY = [("tls.", "https"), ("transport.", "https"), ("headers.", "headers"), ("cookies.", "cookies"),
                    ("cors.", "cors"), ("content.", "content"), ("dns.", "email"), ("exposure.", "exposure"),
                    ("active.", "active"), ("ports.", "ports")]

CHECK_INFO = {
    "tls": "Certificado digital y versión del cifrado del sitio.",
    "transport": "Que el sitio obligue a usar la versión segura (HTTPS).",
    "headers": "Cabeceras de seguridad que protegen al visitante en el navegador.",
    "cookies": "Configuración de seguridad de las cookies de sesión.",
    "cors": "Qué sitios externos pueden leer información de tu sitio.",
    "content": "Formularios, scripts externos y datos sensibles en el código de la página.",
    "dns": "Registros de correo (SPF, DMARC) y de certificados (CAA) del dominio.",
    "exposure": "Archivos de configuración, respaldos o carpetas visibles por error.",
    "host-discovery": "Qué equipos de la red están encendidos y responden.",
    "tcp-connect": "Qué puertos TCP (puertas de red) tiene abiertos cada equipo.",
    "tcp-syn": "Qué puertos TCP (puertas de red) tiene abiertos cada equipo (escaneo SYN).",
    "udp": "Qué puertos UDP (servicios como DNS, SNMP o NTP) responden.",
    "service-detection": "Qué programa y qué versión hay detrás de cada puerto abierto.",
    "xss_reflected": "Prueba activa: inyección de scripts en parámetros (XSS).",
    "sqli": "Prueba activa: inyección en la base de datos (SQL).",
    "open_redirect": "Prueba activa: redirecciones que pueden usarse para engañar.",
    "cmd_injection": "Prueba activa: ejecución de comandos en el servidor.",
    "ssti": "Prueba activa: inyección en plantillas del servidor.",
}


@dataclass(frozen=True)
class Explanation:
    what: str  # qué significa, con analogía
    why: str  # por qué importa al negocio
    fix: str  # qué hacer, en simple
    effort: int
    who: str
    terms: tuple[str, ...] = ()


E = Explanation

KB: dict[str, Explanation] = {
    # ---- HTTPS / TLS ----
    "tls.cert_invalid": E(
        "El 'carnet de identidad' digital del sitio no es reconocido por los navegadores.",
        "Los visitantes ven una advertencia roja de 'sitio no seguro' y muchos se van. Además, la conexión no "
        "garantiza que estén hablando con tu sitio real.",
        "Instalar un certificado válido emitido para este dominio exacto (existen opciones gratuitas como "
        "Let's Encrypt) y verificar que incluya también la versión con y sin 'www'.", 1, "hosting", ("Certificado TLS",)),
    "tls.unreachable": E(
        "No se pudo establecer la conexión cifrada para revisarla.",
        "Si el sitio no ofrece conexión cifrada, todo lo que escriben los visitantes (contraseñas, formularios) "
        "viaja a la vista de terceros.",
        "Confirmar con el proveedor de hosting que el puerto 443 (HTTPS) esté activo y con certificado instalado.",
        2, "hosting", ("HTTPS", "Certificado TLS")),
    "tls.expired": E(
        "El certificado de seguridad del sitio ya venció, como un documento de identidad caducado.",
        "Los navegadores bloquean o advierten al visitante al entrar, se pierde confianza y ventas, y el sitio "
        "puede dejar de funcionar para integraciones.",
        "Renovar el certificado hoy mismo y activar la renovación automática para que no vuelva a ocurrir.",
        1, "hosting", ("Certificado TLS",)),
    "tls.expiring": E(
        "El certificado de seguridad está cerca de vencer, como un documento a punto de caducar.",
        "Si nadie lo renueva a tiempo, el sitio mostrará advertencias de seguridad a todos los visitantes.",
        "Renovarlo ahora y, mejor aún, activar la renovación automática.", 1, "hosting", ("Certificado TLS",)),
    "tls.expiring_soon": E(
        "El certificado de seguridad vencerá en menos de un mes.",
        "Aún no hay problema, pero es el momento de programar la renovación para evitar una caída sorpresa.",
        "Agendar la renovación o activar la renovación automática.", 1, "hosting", ("Certificado TLS",)),
    "tls.legacy": E(
        "El servidor todavía acepta versiones antiguas del cifrado, como una puerta con una cerradura vieja "
        "que sigue funcionando junto a la nueva.",
        "Las versiones antiguas tienen fallas conocidas; un atacante podría forzar a usarlas y espiar la conexión.",
        "Desactivar TLS 1.0 y 1.1 en la configuración del servidor y dejar solo TLS 1.2 y 1.3.",
        2, "hosting", ("TLS",)),
    "tls.no_tls13": E(
        "El sitio no usa la versión más moderna del cifrado (TLS 1.3).",
        "No es un riesgo grave, pero TLS 1.3 es más rápido y más seguro.",
        "Pedir al proveedor de hosting que habilite TLS 1.3.", 1, "hosting", ("TLS",)),
    "tls.weak_cipher": E(
        "El sitio usa un método de cifrado considerado débil, como cerrar con candado de juguete.",
        "Un atacante con recursos podría llegar a descifrar la información que viaja por la conexión.",
        "Configurar el servidor para usar solo métodos modernos (AES-GCM o ChaCha20).",
        2, "hosting", ("TLS",)),
    "transport.no_redirect": E(
        "Quien escribe la dirección sin 'https' entra a una versión sin cifrar del sitio.",
        "Esas visitas viajan sin protección: en una red WiFi pública alguien podría ver o alterar lo que hacen.",
        "Configurar una redirección automática de http:// a https:// en todo el sitio.", 1, "hosting", ("HTTPS",)),
    "transport.plain_http": E(
        "El sitio funciona solo sin cifrado (http), como enviar cartas sin sobre.",
        "Cualquier dato que los visitantes escriban puede ser leído o modificado en el camino, y los navegadores "
        "marcan el sitio como 'no seguro'.",
        "Instalar un certificado HTTPS y obligar a que todo el sitio lo use.", 2, "hosting", ("HTTPS",)),
    # ---- Cabeceras ----
    "headers.hsts": E(
        "El sitio no le indica al navegador que debe usar SIEMPRE la conexión segura.",
        "Un atacante en la misma red WiFi podría forzar una conexión sin cifrar la primera vez que alguien visita.",
        "Agregar la cabecera Strict-Transport-Security con una duración larga (por ejemplo, un año).",
        1, "hosting", ("HSTS", "Cabecera")),
    "headers.hsts_short": E(
        "El aviso 'usa siempre HTTPS' dura muy poco tiempo en el navegador del visitante.",
        "La protección se pierde rápido y el visitante queda expuesto de nuevo.",
        "Aumentar la duración (max-age) de HSTS a al menos seis meses.", 1, "hosting", ("HSTS",)),
    "headers.csp": E(
        "El sitio no define una 'lista de invitados' de qué scripts y recursos puede cargar.",
        "Si un atacante lograra insertar código malicioso en la página, el navegador lo ejecutaría sin cuestionarlo "
        "(robo de datos, formularios falsos).",
        "Definir una política Content-Security-Policy que permita solo los orígenes que el sitio realmente usa.",
        3, "dev", ("CSP", "Cabecera", "XSS")),
    "headers.csp_weak": E(
        "La 'lista de invitados' de scripts existe, pero es tan permisiva que protege poco.",
        "Mantiene abierta la puerta que la política debía cerrar.",
        "Quitar permisos amplios como 'unsafe-inline' o comodines (*) y listar solo orígenes necesarios.",
        3, "dev", ("CSP", "XSS")),
    "headers.clickjacking": E(
        "Otra página podría mostrar tu sitio escondido dentro de la suya para engañar a los usuarios y "
        "hacerles hacer clic donde no quieren (clickjacking).",
        "Un visitante podría, sin saberlo, aprobar una compra, un cambio de datos o un permiso.",
        "Agregar la cabecera X-Frame-Options o la directiva frame-ancestors en la política CSP.",
        1, "hosting", ("Clickjacking", "Cabecera")),
    "headers.nosniff": E(
        "El navegador puede 'adivinar' el tipo de un archivo en lugar de confiar en lo que dice el servidor.",
        "Un archivo subido como imagen podría llegar a ejecutarse como script.",
        "Agregar la cabecera X-Content-Type-Options con el valor nosniff.", 1, "hosting", ("Cabecera",)),
    "headers.referrer": E(
        "Al hacer clic en un enlace externo, el sitio le cuenta al destino exactamente de qué página venía.",
        "Pueden filtrarse direcciones internas o datos incluidos en la URL.",
        "Agregar la cabecera Referrer-Policy (por ejemplo, strict-origin-when-cross-origin).",
        1, "hosting", ("Cabecera",)),
    "headers.permissions": E(
        "El sitio no restringe qué funciones del dispositivo (cámara, micrófono, ubicación) puede usar la página.",
        "Es una medida de orden: reduce el daño si algún script externo fuese comprometido.",
        "Agregar la cabecera Permissions-Policy desactivando lo que el sitio no necesita.",
        1, "hosting", ("Cabecera",)),
    "headers.disclosure": E(
        "El servidor anuncia con qué tecnología y versión está hecho, como dejar un letrero con el modelo "
        "de tu cerradura.",
        "Facilita a un atacante buscar fallas conocidas de esa versión exacta.",
        "Ocultar o simplificar esa cabecera en la configuración del servidor.", 1, "hosting", ("Cabecera",)),
    "headers.cache": E(
        "Páginas con datos de sesión podrían quedar guardadas en la memoria (caché) del navegador o de "
        "intermediarios.",
        "En un computador compartido, otra persona podría ver páginas privadas con el botón 'atrás'.",
        "Agregar Cache-Control: no-store en las páginas que muestran información personal.",
        1, "dev", ("Caché",)),
    # ---- Cookies ----
    "cookies.secure": E(
        "Las cookies de sesión pueden viajar por conexiones sin cifrar.",
        "Alguien en la misma red podría copiarlas y entrar a la cuenta de otra persona sin saber su clave.",
        "Marcar las cookies con el atributo Secure.", 1, "dev", ("Cookie",)),
    "cookies.httponly": E(
        "Los scripts de la página pueden leer las cookies de sesión.",
        "Si algún script malicioso se colara, podría robar la sesión del usuario.",
        "Marcar las cookies de sesión con el atributo HttpOnly.", 1, "dev", ("Cookie", "XSS")),
    "cookies.samesite": E(
        "Las cookies no indican si pueden enviarse cuando la petición viene desde otro sitio.",
        "Facilita ataques en los que otra web hace acciones en nombre del usuario (CSRF).",
        "Definir el atributo SameSite (Lax o Strict) en las cookies.", 1, "dev", ("Cookie", "CSRF")),
    "cookies.samesite_none": E(
        "Las cookies se envían incluso en peticiones iniciadas desde otros sitios.",
        "Solo es necesario en casos especiales (contenido incrustado); de lo contrario aumenta el riesgo de CSRF.",
        "Usar SameSite=Lax salvo que realmente se requiera lo contrario.", 1, "dev", ("Cookie", "CSRF")),
    "cookies.prefix": E(
        "Las cookies no usan los prefijos de seguridad modernos (__Host- / __Secure-).",
        "Es una capa extra de protección que evita que una cookie sea reemplazada por una falsa.",
        "Renombrar las cookies de sesión con el prefijo __Host- cuando sea posible.", 2, "dev", ("Cookie",)),
    # ---- CORS ----
    "cors.reflected_origin": E(
        "El sitio acepta pedidos de datos desde cualquier página que lo solicite, como un guardia que deja "
        "pasar a quien diga que lo conoce.",
        "Una web maliciosa podría leer información privada de un usuario que esté con sesión iniciada en tu sitio.",
        "Permitir solo una lista fija de dominios de confianza en la configuración CORS.", 2, "dev", ("CORS",)),
    "cors.wildcard": E(
        "Cualquier otra web puede leer las respuestas públicas de tu sitio.",
        "Es aceptable para datos públicos, pero riesgoso si algún dato no debería ser visible para todos.",
        "Revisar qué respuestas se exponen y restringir el origen permitido si hay datos sensibles.",
        2, "dev", ("CORS",)),
    "cors.null_origin": E(
        "El sitio acepta pedidos que llegan con un origen 'nulo', algo que un atacante puede fabricar.",
        "Permite saltarse la restricción entre sitios para leer datos privados.",
        "No aceptar el origen 'null' en la configuración CORS.", 1, "dev", ("CORS",)),
    # ---- Contenido ----
    "content.mixed": E(
        "Una página segura (https) carga imágenes o scripts por una conexión no segura (http).",
        "Esos elementos pueden ser alterados en el camino y el navegador puede mostrar el candado como 'no seguro'.",
        "Cambiar todas las direcciones http:// del contenido por https://.", 1, "dev", ("HTTPS",)),
    "content.sri": E(
        "La página carga scripts de otros sitios sin comprobar que sean los originales.",
        "Si ese sitio externo fuese comprometido, su script alterado se ejecutaría dentro de tu página.",
        "Agregar el atributo integrity (SRI) a los scripts y estilos externos, o alojarlos en tu propio servidor.",
        2, "dev", ("SRI",)),
    "content.form_http": E(
        "Hay un formulario que envía los datos por una conexión sin cifrar.",
        "Lo que escriba el usuario (correo, clave, datos personales) puede ser leído por terceros.",
        "Cambiar la dirección de envío del formulario a https://.", 1, "dev", ("HTTPS",)),
    "content.form_get": E(
        "Un formulario con campo de contraseña envía los datos en la dirección (URL) de la página.",
        "Las claves quedan guardadas en el historial del navegador y en los registros del servidor.",
        "Cambiar el método del formulario a POST.", 1, "dev"),
    "content.csrf": E(
        "Un formulario no incluye una 'contraseña de un solo uso' que pruebe que lo envió el propio usuario.",
        "Otra web podría hacer que el navegador del usuario envíe el formulario sin que se dé cuenta (CSRF).",
        "Agregar un token anti-CSRF a los formularios que modifican datos.", 2, "dev", ("CSRF",)),
    "content.comments": E(
        "En el código fuente de la página quedaron comentarios internos que cualquiera puede leer.",
        "Pueden revelar rutas internas, nombres de sistemas o notas del equipo útiles para un atacante.",
        "Eliminar comentarios sensibles antes de publicar.", 1, "dev"),
    "content.secret": E(
        "Se detectó lo que parece una clave o credencial dentro del código visible de la página.",
        "Cualquiera podría copiarla y usar el servicio asociado a nombre de la empresa.",
        "Revocar y reemplazar de inmediato la clave, y moverla a configuración del servidor (nunca en la web pública).",
        2, "dev", ("Credencial",)),
    "content.generator": E(
        "La página declara con qué programa fue creada (por ejemplo, el CMS y su versión).",
        "Ayuda a un atacante a buscar fallas conocidas de esa versión.",
        "Ocultar la etiqueta 'generator' y mantener el sistema siempre actualizado.", 1, "dev", ("CMS",)),
    # ---- Correo / DNS ----
    "dns.spf_missing": E(
        "El dominio no declara qué servidores están autorizados para enviar correo en su nombre.",
        "Cualquiera puede enviar correos que parezcan venir de tu empresa (suplantación) y tus propios correos "
        "legítimos pueden caer en spam.",
        "Publicar un registro SPF en el DNS listando tus servicios de correo.", 1, "dns", ("SPF",)),
    "dns.spf_permissive": E(
        "El registro SPF dice que CUALQUIER servidor puede enviar correo como tu dominio.",
        "Es como no tener la protección: no impide la suplantación.",
        "Cambiar '+all' por '-all' (o '~all') y listar solo los servicios autorizados.", 1, "dns", ("SPF",)),
    "dns.spf_neutral": E(
        "El registro SPF no toma postura sobre los correos de servidores no autorizados.",
        "Los correos falsos no se rechazan con claridad.",
        "Reemplazar '?all' por '~all' o '-all'.", 1, "dns", ("SPF",)),
    "dns.dmarc_missing": E(
        "El dominio no indica qué hacer con correos que dicen ser tuyos pero no lo son.",
        "Los estafadores pueden enviar correos falsos con tu nombre a tus clientes sin que los servidores los frenen.",
        "Publicar un registro DMARC; empezar en modo monitoreo y subir gradualmente la exigencia.",
        1, "dns", ("DMARC", "SPF")),
    "dns.dmarc_none": E(
        "DMARC está en modo 'solo observar': detecta correos falsos pero no los bloquea.",
        "Es un buen primer paso, pero la suplantación todavía no se detiene.",
        "Una vez revisados los reportes, subir la política a 'quarantine' y luego a 'reject'.",
        2, "dns", ("DMARC",)),
    "dns.caa_missing": E(
        "No se limita qué entidades pueden emitir certificados para tu dominio.",
        "Es una medida de orden que reduce el riesgo de que alguien obtenga un certificado falso.",
        "Agregar un registro CAA con la entidad certificadora que usas.", 1, "dns", ("CAA", "Certificado TLS")),
    # ---- Exposición ----
    "exposure.sensitive": E(
        "Un archivo interno del sitio (configuración, respaldo o repositorio) se puede descargar desde internet, "
        "como dejar un archivador de la oficina en la vereda.",
        "Puede contener claves, contraseñas o el código fuente completo. Es una de las fallas más graves y más "
        "fáciles de aprovechar.",
        "Bloquear el acceso al archivo, eliminarlo del servidor público y cambiar todas las claves que contenía "
        "(asumir que ya fueron vistas).", 2, "hosting", ("Credencial",)),
    "exposure.dir_listing": E(
        "Al abrir una carpeta del sitio se muestra la lista completa de archivos que contiene.",
        "Facilita encontrar archivos que no se pensaban publicar (respaldos, documentos).",
        "Desactivar el listado de directorios en la configuración del servidor.", 1, "hosting"),
    "exposure.security_txt": E(
        "El sitio no publica un contacto para que investigadores reporten fallas de seguridad.",
        "Si alguien encuentra un problema, no sabrá a quién avisar de forma responsable.",
        "Publicar un archivo security.txt con un correo de contacto.", 1, "dev", ("security.txt",)),
    # ---- Activos ----
    "active.xss_reflected": E(
        "Un campo del sitio devuelve en pantalla lo que se escribe sin limpiarlo, y permite inyectar código "
        "(XSS).",
        "Un atacante podría armar un enlace que, al abrirse, robe sesiones o muestre formularios falsos.",
        "Escapar y validar todo dato que el usuario envía antes de mostrarlo en la página.", 3, "dev", ("XSS",)),
    "active.sqli_error": E(
        "Un parámetro del sitio llega a la base de datos sin ser limpiado y produce errores de la base de datos.",
        "Un atacante podría leer, modificar o borrar la información almacenada (clientes, pedidos).",
        "Usar consultas parametrizadas en lugar de armar las consultas concatenando texto.", 3, "dev", ("SQLi",)),
    "active.sqli_boolean": E(
        "El sitio cambia de respuesta según condiciones inyectadas en un parámetro; indica una posible "
        "inyección SQL.",
        "Un atacante podría extraer datos de la base de datos poco a poco.",
        "Usar consultas parametrizadas y validar los parámetros.", 3, "dev", ("SQLi",)),
    "active.open_redirect": E(
        "El sitio puede redirigir a cualquier dirección que se le indique en un parámetro.",
        "Los estafadores usan tu dominio confiable en enlaces que terminan en páginas falsas.",
        "Permitir redirecciones solo hacia una lista fija de destinos propios.", 2, "dev", ("Redirección abierta",)),
    "active.cmd_injection": E(
        "Un parámetro parece llegar a la línea de comandos del servidor sin ser limpiado.",
        "Es de lo más grave: un atacante podría ejecutar comandos y tomar control del servidor.",
        "Nunca construir comandos con datos del usuario; usar funciones seguras y validar estrictamente.",
        3, "dev", ("Inyección de comandos",)),
    "active.ssti": E(
        "Un parámetro se evalúa dentro de una plantilla del servidor, y eso puede permitir ejecutar código.",
        "Puede escalar a control completo del servidor.",
        "No pasar datos del usuario como plantilla; usarlos solo como valores a mostrar.", 3, "dev", ("SSTI",)),
    # ---- Puertos de red (port-scanner) ----
    "ports.exposed": E(
        "Un servicio del equipo está 'con la puerta abierta' en la red: cualquiera que llegue hasta él puede intentar "
        "conectarse.",
        "Cada servicio visible es un punto más por donde pueden intentar entrar. Si no se usa o no debería verse "
        "desde fuera, solo suma riesgo.",
        "Cerrar el servicio si no se necesita, o bloquearlo con el firewall para que solo lo vean los equipos que "
        "realmente lo usan.", 2, "ti", ("Puerto", "Firewall")),
    "ports.telnet": E(
        "Telnet es una forma antigua de controlar un equipo a distancia en la que todo viaja sin cifrar, como "
        "hablar por teléfono con el altavoz encendido.",
        "Quien esté en el camino puede leer el usuario y la contraseña y entrar como administrador.",
        "Apagar Telnet y usar SSH, que hace lo mismo pero cifrado.", 1, "ti", ("Puerto", "Firewall")),
    "ports.ftp": E(
        "FTP es un método antiguo para subir y bajar archivos que no cifra nada, ni siquiera la contraseña.",
        "Las claves y archivos pueden ser interceptados, y los servidores FTP suelen quedar mal configurados.",
        "Cambiar a SFTP o FTPS (versiones cifradas) y limitar quién puede conectarse.", 2, "ti", ("Puerto", "Firewall")),
    "ports.smb": E(
        "SMB es el sistema con el que Windows comparte carpetas e impresoras en la red; el puerto 445 es el más "
        "atacado por virus y ransomware.",
        "Si es visible desde fuera, programas maliciosos pueden intentar propagarse o cifrar los archivos de la empresa.",
        "Bloquear el puerto 445 hacia internet, mantener Windows actualizado y desactivar SMBv1.", 1, "ti",
        ("SMB", "Firewall", "Puerto")),
    "ports.rdp": E(
        "El Escritorio Remoto (RDP) permite manejar un computador a distancia, como sentarse frente a él.",
        "Cuando queda abierto a internet recibe ataques de contraseñas todo el día y ha tenido fallos graves; es una "
        "entrada habitual de ransomware.",
        "No dejarlo expuesto: acceder por VPN o con verificación en dos pasos, y activar NLA.", 2, "ti",
        ("RDP", "VPN", "Fuerza bruta")),
    "ports.vnc": E(
        "VNC permite ver y controlar el escritorio de un equipo a distancia.",
        "Suele usar claves débiles y poca protección: quien entre controla el equipo completo.",
        "Ponerlo detrás de una VPN o túnel SSH y usar contraseñas largas.", 2, "ti", ("VPN", "Puerto")),
    "ports.database": E(
        "Una base de datos (donde se guardan clientes, ventas o usuarios) es visible desde la red, como tener la "
        "bóveda con la puerta a la calle.",
        "Los atacantes buscan bases de datos expuestas para probar contraseñas, aprovechar fallos o copiar la "
        "información completa.",
        "Hacer que la base de datos acepte solo conexiones del propio servidor o de la red privada, y bloquear su "
        "puerto en el firewall.", 2, "ti", ("Puerto", "Firewall")),
    "ports.docker": E(
        "La API de Docker (el sistema que corre aplicaciones en contenedores) está abierta a la red.",
        "Es de lo más grave: quien llegue puede crear contenedores y tomar el control total del servidor.",
        "Cerrar el puerto 2375 de inmediato; si se necesita acceso remoto, usar conexión cifrada con certificados.",
        1, "ti", ("Puerto", "Firewall")),
    "ports.noauth": E(
        "Un servicio responde sin pedir usuario ni contraseña, como una oficina donde cualquiera entra y se sirve.",
        "Cualquiera que llegue hasta el puerto puede leer, modificar o borrar datos, y en varios casos tomar el "
        "control del servidor.",
        "Activar la autenticación del servicio, limitar a qué equipos escucha y bloquear su puerto en el firewall.",
        1, "ti", ("Puerto", "Firewall")),
    "ports.cert": E(
        "El certificado digital del servicio (su 'carnet de identidad') tiene un problema: está vencido, por vencer "
        "o lo firmó el propio servidor.",
        "Los usuarios ven advertencias de seguridad y la identidad del servicio no está garantizada.",
        "Renovar el certificado con una entidad reconocida (Let's Encrypt es gratis) y activar la renovación automática.",
        1, "hosting", ("Certificado TLS",)),
    "ports.legacy_tls": E(
        "El servicio acepta versiones antiguas del cifrado (TLS 1.0 o 1.1) que ya no se consideran seguras.",
        "Un atacante podría forzar el uso de una versión débil y descifrar parte de la conversación.",
        "Dejar habilitados solo TLS 1.2 y 1.3 en el servidor.", 1, "hosting", ("TLS",)),
    "ports.ssh": E(
        "El servicio de acceso remoto SSH usa una versión del protocolo o del programa que está obsoleta.",
        "Las versiones viejas tienen fallos públicos y algoritmos débiles.",
        "Actualizar OpenSSH y dejar solo el protocolo 2.", 1, "ti", ("Puerto",)),
    "ports.snmp": E(
        "SNMP es un 'chat' con el que se consultan equipos de red; aquí responde a la clave por defecto 'public'.",
        "Con esa clave conocida cualquiera puede ver detalles del equipo y de la red.",
        "Cambiar la clave, pasar a SNMPv3 y permitir consultas solo desde el equipo de monitoreo.", 1, "ti",
        ("Puerto", "Firewall")),
    "ports.dns": E(
        "El servidor DNS responde consultas de cualquier persona en internet, no solo de tu red.",
        "Puede ser usado como arma para ataques contra terceros y revela qué dominios se consultan.",
        "Limitar el DNS para que solo responda a tu red interna.", 1, "ti", ("Puerto", "Firewall")),
    "ports.smtp": E(
        "El servidor de correo no ofrece cifrado (STARTTLS) o es un servicio de correo visible.",
        "Los correos pueden leerse en el camino y un servidor mal configurado puede usarse para enviar spam.",
        "Activar STARTTLS con certificado válido y exigir autenticación para enviar.", 1, "ti", ("Puerto",)),
    "ports.http": E(
        "El servidor web muestra información de más: qué programa y versión usa, o métodos poco habituales.",
        "Esa información facilita buscar fallos conocidos para esa versión exacta.",
        "Ocultar la versión en la configuración y deshabilitar los métodos HTTP que no se usan.", 1, "hosting"),
    "ports.many-open": E(
        "El equipo tiene muchísimos servicios visibles en la red.",
        "Cada servicio extra es una puerta más que vigilar y mantener actualizada.",
        "Apagar lo que no se usa y dejar el resto detrás de un firewall.", 2, "ti", ("Puerto", "Firewall")),
    "ports.inventory": E(
        "Lista de las 'puertas' de red que están abiertas en este equipo y qué programa atiende cada una.",
        "Sirve como inventario: conviene confirmar que cada servicio abierto es necesario y está actualizado.",
        "Revisar la lista y cerrar lo que no se use.", 1, "ti", ("Puerto",)),
}

_RULES = [  # (prefijo del id, clave en KB)
    ("tls.legacy", "tls.legacy"), ("headers.disclosure", "headers.disclosure"),
    ("exposure.dir_listing", "exposure.dir_listing"), ("exposure.security_txt", "exposure.security_txt"),
    ("exposure.", "exposure.sensitive"),
    # port-scanner: los ids son ports.<servicio> y ports.script.<chequeo>
    ("ports.telnet", "ports.telnet"), ("ports.ftp", "ports.ftp"), ("ports.script.ftp", "ports.ftp"),
    ("ports.smb", "ports.smb"), ("ports.script.smb", "ports.smb"), ("ports.rdp", "ports.rdp"),
    ("ports.vnc", "ports.vnc"), ("ports.script.vnc", "ports.noauth"), ("ports.docker", "ports.docker"),
    ("ports.script.docker", "ports.docker"),
    ("ports.mysql", "ports.database"), ("ports.postgresql", "ports.database"), ("ports.mssql", "ports.database"),
    ("ports.oracle", "ports.database"), ("ports.mongodb", "ports.database"), ("ports.redis", "ports.database"),
    ("ports.memcached", "ports.database"), ("ports.elasticsearch", "ports.database"), ("ports.couchdb", "ports.database"),
    ("ports.cassandra", "ports.database"), ("ports.script.redis", "ports.noauth"), ("ports.script.mongodb", "ports.noauth"),
    ("ports.script.memcached", "ports.noauth"), ("ports.script.elasticsearch", "ports.noauth"),
    ("ports.script.cert", "ports.cert"), ("ports.script.tls", "ports.legacy_tls"), ("ports.script.ssh", "ports.ssh"),
    ("ports.script.snmp", "ports.snmp"), ("ports.snmp", "ports.snmp"), ("ports.script.dns", "ports.dns"),
    ("ports.script.smtp", "ports.smtp"), ("ports.smtp", "ports.smtp"), ("ports.script.http", "ports.http"),
    ("ports.many-open", "ports.many-open"), ("ports.inventory", "ports.inventory"),
    ("ports.", "ports.exposed"),
]

GENERIC = E(
    "Se detectó un punto de mejora en la configuración de seguridad.",
    "Dejar esto sin atender puede facilitar ataques o dañar la confianza de los visitantes.",
    "Revisar la recomendación técnica indicada y aplicarla con quien administra el sitio.", 2, "ti")

GLOSSARY = {
    "HTTPS": "La versión segura de la web: cifra lo que viaja entre el visitante y el sitio (el candado del navegador).",
    "TLS": "El sistema de cifrado que hace posible HTTPS. Tiene versiones; las antiguas ya no son seguras.",
    "Certificado TLS": "El 'carnet de identidad' digital del sitio. Lo emite una entidad confiable y tiene fecha de vencimiento.",
    "HSTS": "Una orden al navegador: 'con este sitio habla siempre por HTTPS'.",
    "Cabecera": "Mensajes que el servidor envía junto con la página para dar instrucciones al navegador.",
    "CSP": "Content-Security-Policy: lista de los orígenes desde los que el sitio permite cargar scripts y recursos.",
    "XSS": "Cross-Site Scripting: un atacante logra que la página ejecute código malicioso en el navegador de otras personas.",
    "Clickjacking": "Engaño en el que el sitio se muestra invisible bajo otra página para que el usuario haga clic sin saberlo.",
    "Cookie": "Pequeño dato que el sitio guarda en el navegador para recordar al visitante (por ejemplo, su sesión).",
    "CSRF": "Ataque que aprovecha que el usuario ya inició sesión para hacer acciones sin su consentimiento.",
    "CORS": "Reglas que definen qué otros sitios web pueden pedir datos a tu sitio desde el navegador.",
    "SRI": "Subresource Integrity: huella digital que comprueba que un script externo no fue alterado.",
    "SPF": "Registro del dominio que lista qué servidores pueden enviar correo con tu nombre.",
    "DMARC": "Registro que indica qué hacer con los correos que no pasan las verificaciones de SPF/DKIM.",
    "CAA": "Registro que limita qué entidades pueden emitir certificados para tu dominio.",
    "Caché": "Copia temporal que guardan los navegadores o intermediarios para cargar más rápido.",
    "Credencial": "Clave, contraseña o token que da acceso a un sistema.",
    "CMS": "Sistema de gestión de contenidos (WordPress, Joomla, etc.) con el que se administra el sitio.",
    "SQLi": "Inyección SQL: manipular las consultas a la base de datos a través de un campo del sitio.",
    "Redirección abierta": "El sitio redirige a cualquier dirección, lo que permite armar enlaces engañosos con tu dominio.",
    "Inyección de comandos": "Lograr que el servidor ejecute comandos elegidos por el atacante.",
    "SSTI": "Inyección en plantillas del servidor: datos del usuario interpretados como código.",
    "security.txt": "Archivo público con el contacto para reportar fallas de seguridad.",
    "Puerto": "Una 'puerta' numerada de un equipo en la red. Cada servicio (web, correo, acceso remoto) atiende en su propia puerta.",
    "Firewall": "Cortafuegos: filtra qué conexiones pueden entrar o salir de un equipo o de una red.",
    "SMB": "Protocolo con el que Windows comparte carpetas e impresoras en la red.",
    "RDP": "Escritorio Remoto de Windows: permite controlar un computador a distancia.",
    "VPN": "Túnel cifrado que permite conectarse a la red de la empresa de forma segura desde fuera.",
    "Fuerza bruta": "Probar contraseñas una tras otra, de forma automática, hasta acertar.",
}


def category_of(check_id: str) -> str:
    for prefix, key in _PREFIX_CATEGORY:
        if check_id.startswith(prefix):
            return key
    return "other"


def explain(check_id: str) -> Explanation:
    if check_id in KB:
        return KB[check_id]
    for prefix, key in _RULES:
        if check_id.startswith(prefix):
            return KB[key]
    return GENERIC
