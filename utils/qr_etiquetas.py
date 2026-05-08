from PIL import Image, ImageDraw, ImageFont
import qrcode
from io import BytesIO
import os

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
    COLOR_PRIMARIO = "#00A844"   # Verde vivo (puedes cambiar)
    COLOR_SECUNDARIO = "#1B5E36" # Verde oscuro (ejemplo)
    COLOR_TEXTO = "#2D3748"    # Gris oscuro para texto
    Color_TEXTO_CUERPO = "#4A5568" # Gris medio para cuerpo de texto

    # =========================
    # CREAR BASE
    # =========================
    ancho = 450
    alto =600

    img = Image.new("RGB", (ancho, alto), COLOR_FONDO)
    draw = ImageDraw.Draw(img)

    # =========================
    # BORDES
    # =========================
    draw.rectangle([(0,0),(ancho-1,alto-1)], outline=COLOR_PRIMARIO, width=4)

    # =========================
    # HEADER (barra superior)
    # =========================
    header_h = 100
    draw.rectangle([(0,0),(ancho,header_h)], fill=COLOR_PRIMARIO)

    # =========================
    # CARGAR LOGO
    # =========================
    logo_x = 10
    fondo_w = 0
    try:
        ruta_logo = os.path.join(os.path.dirname(__file__), "logo_CIACA.png")

        logo = Image.open(ruta_logo).convert("RGBA")
        
        # tamaño máximo permitido dentro del header
        max_width = 120
        max_height = 60
        logo.thumbnail((max_width, max_height), Image.LANCZOS)

        logo_w, logo_h = logo.size
        logo_y = (header_h - logo_h) // 2

        # 🔥 crear fondo blanco (padding)
        padding = 8
        fondo_w = logo_w + padding*2
        fondo_h = logo_h + padding*2

        fondo_logo = Image.new("RGBA", (fondo_w, fondo_h), (255,255,255,255))

        # pegar logo dentro del fondo
        fondo_logo.paste(logo, (padding, padding), logo)

        # pegar fondo en imagen principal
        img.paste(fondo_logo, (logo_x, logo_y - padding//2), fondo_logo)

    except Exception as e:
        print("Error cargando logooooo:", e)

    # =========================
    # FUENTES (PRODUCCIÓN SEGURA)
    # =========================

    # rutas absolutas (clave para producción)
    ruta_base = os.path.dirname(__file__)

    font_regular_path = os.path.join(ruta_base, "fonts", "Roboto-Regular.ttf")
    font_bold_path = os.path.join(ruta_base, "fonts", "Roboto-Bold.ttf")

    # fallback
    font_title = ImageFont.load_default()
    font_titulo = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_small = ImageFont.load_default()

    # cargar fuentes
    try:
        font_title = ImageFont.truetype(font_bold_path, 22)
    except Exception as e:
        print("Error font_title:", e)

    try:
        font_titulo = ImageFont.truetype(font_bold_path, 30)
    except Exception as e:
        print("Error font_titulo:", e)

    try:
        font_sub = ImageFont.truetype(font_regular_path, 18)
    except Exception as e:
        print("Error font_sub:", e)

    try:
        font_small = ImageFont.truetype(font_regular_path, 16)
    except Exception as e:
        print("Error font_small:", e)


    # =========================
    # TEXTO HEADER
    # =========================
    texto_header = "Inspección Preoperacional"

    try:
        bbox = draw.textbbox((0,0), texto_header, font=font_title)
    except:
        bbox = draw.textsize(texto_header, font=font_title)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    text_x = logo_x + fondo_w + 20
    text_y = (header_h - text_h) // 2
    
    # sombra
    draw.text((text_x+1, text_y+1), texto_header, fill="black", font=font_title)
    # texto principal
    draw.text((text_x, text_y), texto_header, fill="white", font=font_title)
        
    # =========================
    # INFO MÁQUINA
    # =========================
    draw.text((20, 120), f"{tipo} {equipo}", fill=COLOR_TEXTO, font=font_titulo)
    draw.text((20, 160), f"{activo}", fill=COLOR_TEXTO, font=font_sub)
    #draw.text((20, 170), f"Equipo: {equipo}", fill=COLOR_TEXTO, font=font_sub)

    # =========================
    # QR PERSONALIZADO
    # =========================
    qr = qrcode.QRCode(
        version=2,
        box_size=10,
        border=2
    )

    qr.add_data(url)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color=COLOR_SECUNDARIO,
        back_color="white"
    )

    qr_img = qr_img.resize((300, 300))

    qr_x = (ancho - 300) // 2
    img.paste(qr_img, (qr_x, 200))

    # =========================
    # TEXTO INFERIOR
    # =========================
    draw.rectangle([(0, 560), (ancho, alto+10)], fill=COLOR_PRIMARIO)

    draw.text(
        (60, 570),
        "ESCANEE PARA REGISTRAR INSPECCIÓN",
        fill="black",
        font=font_small
    )
    
    # =========================
    # EXPORTAR
    # =========================
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return buffer