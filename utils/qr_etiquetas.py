from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO

def generar_qr_etiqueta(maquina, base_url):

    maquina_id = maquina[0]
    activo = maquina[1]
    tipo = maquina[2]
    equipo = maquina[3]

    url = f"{base_url}?maquina_id={maquina_id}"

    # =========================
    # COLORES CORPORATIVOS
    # =========================
    COLOR_FONDO = "#FFFFFF"
    COLOR_PRIMARIO = "#0F2A44"   # Azul oscuro (puedes cambiar)
    COLOR_SECUNDARIO = "#F2C201" # Amarillo (ejemplo)
    COLOR_TEXTO = "#000000"

    # =========================
    # CREAR BASE
    # =========================
    ancho = 420
    alto = 520

    img = Image.new("RGB", (ancho, alto), COLOR_FONDO)
    draw = ImageDraw.Draw(img)

    # =========================
    # BORDES
    # =========================
    draw.rectangle([(0,0),(ancho-1,alto-1)], outline=COLOR_PRIMARIO, width=4)

    # =========================
    # HEADER (barra superior)
    # =========================
    draw.rectangle([(0,0),(ancho,80)], fill=COLOR_PRIMARIO)

    # =========================
    # CARGAR LOGO
    # =========================
    try:
        logo = Image.open("logo.png")
        logo = logo.resize((60, 60))
        img.paste(logo, (10,10), logo)
    except:
        pass  # si no hay logo no rompe

    # =========================
    # FUENTES
    # =========================
    try:
        font_titulo = ImageFont.truetype("arial.ttf", 30)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_titulo = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # =========================
    # TEXTO HEADER
    # =========================
    draw.text((90, 20), "CHECKLIST", fill="white", font=font_titulo)

    # =========================
    # INFO MÁQUINA
    # =========================
    draw.text((20, 100), f"{activo}", fill=COLOR_TEXTO, font=font_titulo)
    draw.text((20, 140), f"{tipo}", fill=COLOR_TEXTO, font=font_sub)
    draw.text((20, 170), f"Equipo: {equipo}", fill=COLOR_TEXTO, font=font_sub)

    # =========================
    # QR
    # =========================
    qr = qrcode.make(url)
    qr = qr.resize((260, 260))

    qr_x = (ancho - 260) // 2
    img.paste(qr, (qr_x, 210))

    # =========================
    # TEXTO INFERIOR
    # =========================
    draw.text((80, 480), "Escanee para inspección", fill=COLOR_TEXTO, font=font_small)

    # =========================
    # EXPORTAR
    # =========================
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer