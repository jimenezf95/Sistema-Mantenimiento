from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import qrcode

def generar_qr_pdf(maquinas, base_url):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elementos = []

    data = []
    fila = []

    for i, m in enumerate(maquinas):

        maquina_id = m[0]
        activo = m[1]
        tipo = m[2]
        equipo = m[3]

        url = f"{base_url}?maquina_id={maquina_id}"

        # Generar QR
        qr = qrcode.make(url)
        qr_buffer = BytesIO()
        qr.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)

        img = Image(qr_buffer, width=100, height=100)

        texto = Paragraph(f"<b>{activo}</b><br/>{tipo}<br/>{equipo}", styles["Normal"])

        celda = [img, Spacer(1,5), texto]

        fila.append(celda)

        # 3 columnas por fila
        if (i + 1) % 3 == 0:
            data.append(fila)
            fila = []

    if fila:
        data.append(fila)

    tabla = Table(data)

    tabla.setStyle(TableStyle([
        ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))

    elementos.append(tabla)

    doc.build(elementos)

    buffer.seek(0)

    return buffer

