import streamlit as st
import pandas as pd
from datetime import datetime
import os
import urllib.parse
import base64
import io

# Intento de librerías para renderizar el logo PDF a Imagen
try:
    import fitz  # PyMuPDF
    HAS_FITZ = True
except ImportError:
    HAS_FITZ = False

try:
    import pypdfium2 as pdfium
    HAS_PDFIUM = True
except ImportError:
    HAS_PDFIUM = False

# Configuración de la página
st.set_page_config(
    page_title="JV Soluciones - PESV Planificación de Ruta",
    page_icon="🚚",
    layout="wide"
)

# Estilos CSS
st.markdown("""
<style>
    .pesv-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 10px;
        font-size: 13px;
        background-color: #ffffff;
        color: #000000;
    }
    .pesv-table th, .pesv-table td {
        border: 1px solid #333;
        padding: 6px 10px;
        text-align: left;
    }
    .pesv-header-title {
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        background-color: #f2f2f2;
    }
    .signature-grid {
        display: flex;
        justify-content: space-between;
        margin-top: 15px;
        border-top: 1px solid #333;
        padding-top: 10px;
        font-size: 12px;
    }
</style>
""", unsafe_allow_html=True)

DB_FILE = "planificacion_rutas_pesv.csv"
DEFAULT_PDF_LOGO_PATH = r"C:\Users\Usuario\OneDrive\Desktop\logo.pdf"

def cargar_datos():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame()

def obtener_logo_bytes(pdf_path):
    if not os.path.exists(pdf_path):
        return None
    try:
        if HAS_FITZ:
            doc = fitz.open(pdf_path)
            page = doc.load_page(0)
            pix = page.get_pixmap(dpi=150)
            return pix.tobytes("png")
        if HAS_PDFIUM:
            pdf = pdfium.PdfDocument(pdf_path)
            page = pdf[0]
            image = page.render(scale=2).to_pil()
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            return img_byte_arr.getvalue()
    except Exception:
        pass
    return None

def image_to_base64(img_bytes):
    if img_bytes:
        return f"data:image/png;base64,{base64.b64encode(img_bytes).decode()}"
    return ""

def generar_url_gmaps(origen, destino, ciudad):
    ori_enc = urllib.parse.quote(f"{origen}, {ciudad}")
    dest_enc = urllib.parse.quote(f"{destino}, {ciudad}")
    return f"https://www.google.com/maps/dir/?api=1&origin={ori_enc}&destination={dest_enc}&travelmode=driving"

logo_bytes = obtener_logo_bytes(DEFAULT_PDF_LOGO_PATH)

st.sidebar.title("🚚 JV Soluciones PESV")
opcion = st.sidebar.radio(
    "Navegación",
    ["📝 Nueva Planificación de Ruta", "📊 Historial y Formatos"]
)

if opcion == "📝 Nueva Planificación de Ruta":
    st.title("📋 Formato de Planificación de Ruta (PESV)")
    st.caption("Sistema de Gestión Integral - Control de Movilización")

    with st.form("form_pesv"):
        st.subheader("1. Información General del Vehículo / Equipo")
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha_act = st.date_input("Fecha:", datetime.now())
        with col2:
            equipo_nombre = st.text_input("Equipo / Vehículo:", value="Moto Suzuki Gsx125")
        with col3:
            cod_int = st.text_input("Cod Int / Placa:", value="LZB 96G")

        st.subheader("2. Planificación de Salida")
        col_s1, col_s2, col_s3 = st.columns([2, 2, 1])
        with col_s1:
            dir_salida_ori = st.text_input("Dir. Salida (Origen):", value="Mamonal km6 MZ H Lt 10")
        with col_s2:
            dir_destino_ori = st.text_input("Dir. Destino:", value="Oficinas seguros mundial")
        with col_s3:
            ciudad_salida = st.text_input("Ciudad Salida:", value="Cartagena")
            
        col_s4, col_s5 = st.columns(2)
        with col_s4:
            hora_salida_ori = st.text_input("Hora Salida:", value="1:00 PM")
        with col_s5:
            hora_llegada_ori = st.text_input("Hora Llegada Estimada:", value="2:00 PM")

        st.subheader("3. Planificación de Retorno")
        col_r1, col_r2, col_r3 = st.columns([2, 2, 1])
        with col_r1:
            dir_salida_ret = st.text_input("Dir. Salida Retorno:", value="Oficinas Seguros Mundial")
        with col_r2:
            dir_destino_ret = st.text_input("Dir. Destino Retorno:", value="Mamonal km6 MZ H Lt 10")
        with col_r3:
            ciudad_retorno = st.text_input("Ciudad Retorno:", value="Cartagena")
            
        col_r4, col_r5 = st.columns(2)
        with col_r4:
            hora_salida_ret = st.text_input("Hora Salida Retorno:", value="8:00 AM")
        with col_r5:
            hora_llegada_ret = st.text_input("Hora Llegada Retorno:", value="9:00 AM")

        st.subheader("4. Personal Responsable / Aprobaciones")
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)
        with col_p1:
            coordinador = st.text_input("Coordinador:", value="Luis F. Martin")
        with col_p2:
            supervisor = st.text_input("Supervisor:", value="Nelson Vargas")
        with col_p3:
            conductor = st.text_input("Conductor / Operador:", value="Nelson Vargas")
        with col_p4:
            escolta = st.text_input("Escolta (Si aplica):", value="N/A")

        guardar_btn = st.form_submit_button("💾 Guardar y Generar Formato PDF", type="primary")

    if guardar_btn:
        url_maps_salida = generar_url_gmaps(dir_salida_ori, dir_destino_ori, ciudad_salida)
        url_maps_retorno = generar_url_gmaps(dir_salida_ret, dir_destino_ret, ciudad_retorno)
        logo_b64 = image_to_base64(logo_bytes)

        st.success("✅ Ruta planificada con éxito.")

        st.write("---")
        st.header("📄 Formato PESV")

        html_format = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #fff; color: #000; padding: 10px; }}
            .pesv-table {{ width: 100%; border-collapse: collapse; margin-bottom: 10px; font-size: 13px; }}
            .pesv-table th, .pesv-table td {{ border: 1px solid #333; padding: 6px 10px; text-align: left; }}
            .pesv-header-title {{ text-align: center; font-weight: bold; font-size: 15px; background-color: #f2f2f2; }}
            .signature-grid {{ display: flex; justify-content: space-between; margin-top: 15px; border-top: 1px solid #333; padding-top: 10px; font-size: 12px; }}
            .btn-print {{
                background-color: #0d6efd; color: white; padding: 10px 20px; font-size: 14px;
                border: none; border-radius: 5px; cursor: pointer; margin-bottom: 15px; font-weight: bold;
            }}
            @media print {{
                .btn-print {{ display: none; }}
            }}
        </style>
        </head>
        <body>
            <button class="btn-print" onclick="window.print()">🖨️ Descargar o Imprimir en PDF</button>

            <table class="pesv-table">
                <tr>
                    <td style="width: 25%; text-align: center;">
                        {f'<img src="{logo_b64}" style="max-height:50px;">' if logo_b64 else '<b>JV SOLUCIONES</b>'}
                    </td>
                    <td class="pesv-header-title" style="width: 50%;">
                        SISTEMA DE GESTIÓN INTEGRAL<br><span style="font-size:13px; font-weight:normal;">PLANIFICACIÓN DE RUTA</span>
                    </td>
                    <td style="width: 25%; font-size:11px;">
                        <b>Fecha:</b> {fecha_act}
                    </td>
                </tr>
            </table>

            <table class="pesv-table">
                <tr>
                    <td><b>Equipo:</b> {equipo_nombre}</td>
                    <td><b>Cod Int / Placa:</b> {cod_int}</td>
                </tr>
                <tr style="background-color: #f2f2f2; font-weight: bold; text-align: center;">
                    <td colspan="2">PLANIFICACIÓN DE SALIDA</td>
                </tr>
                <tr>
                    <td><b>Origen:</b> {dir_salida_ori} | <b>Destino:</b> {dir_destino_ori}</td>
                    <td><b>Hora salida:</b> {hora_salida_ori} | <b>Llegada:</b> {hora_llegada_ori}</td>
                </tr>
                <tr style="background-color: #f2f2f2; font-weight: bold; text-align: center;">
                    <td colspan="2">PLANIFICACIÓN DE RETORNO</td>
                </tr>
                <tr>
                    <td><b>Origen:</b> {dir_salida_ret} | <b>Destino:</b> {dir_destino_ret}</td>
                    <td><b>Hora salida:</b> {hora_salida_ret} | <b>Llegada:</b> {hora_llegada_ret}</td>
                </tr>
            </table>

            <table class="pesv-table">
                <tr style="background-color: #f2f2f2; font-weight: bold;">
                    <td>Enlace GPS Ruta Salida</td>
                    <td>Enlace GPS Ruta Retorno</td>
                </tr>
                <tr>
                    <td><a href="{url_maps_salida}" target="_blank">🔗 Ver Trazado Interactivo Salida</a></td>
                    <td><a href="{url_maps_retorno}" target="_blank">🔗 Ver Trazado Interactivo Retorno</a></td>
                </tr>
            </table>

            <div class="signature-grid">
                <div><b>Coordinador:</b> {coordinador}</div>
                <div><b>Supervisor:</b> {supervisor}</div>
                <div><b>Conductor:</b> {conductor}</div>
                <div><b>Escolta:</b> {escolta}</div>
            </div>
        </body>
        </html>
        """

        st.components.v1.html(html_format, height=500, scrolling=True)

elif opcion == "📊 Historial y Formatos":
    st.title("📊 Historial de Planificaciones PESV")
    df_historial = cargar_datos()
    if not df_historial.empty:
        st.dataframe(df_historial, use_container_width=True)