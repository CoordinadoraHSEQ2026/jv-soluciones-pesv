import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
from fpdf import FPDF
import os
import glob

# Archivo para persistencia del historial
HISTORIAL_FILE = "historial_rutas.csv"

# Configuración de la página
st.set_page_config(page_title="JV Soluciones - PESV", page_icon="🚚", layout="wide")

# Función para encontrar cualquier archivo de logo disponible sin importar mayúsculas/minúsculas
def obtener_ruta_logo():
    extensiones = ["logo.png", "logo.jpg", "logo.jpeg", "Logo.png", "Logo.jpg", "LOGO.PNG", "logo.PNG"]
    for ext in extensiones:
        if os.path.exists(ext):
            return ext
    # Buscar cualquier archivo que empiece por logo
    busqueda = glob.glob("logo*.*") + glob.glob("Logo*.*")
    if busqueda:
        return busqueda[0]
    return None

LOGO_PATH = obtener_ruta_logo()

# Cargar historial persistente desde CSV si existe
if "historial_rutas" not in st.session_state:
    if os.path.exists(HISTORIAL_FILE):
        try:
            st.session_state.historial_rutas = pd.read_csv(HISTORIAL_FILE)
        except Exception:
            st.session_state.historial_rutas = pd.DataFrame()
    else:
        st.session_state.historial_rutas = pd.DataFrame(columns=[
            "Fecha", "Equipo", "Cod Int", 
            "Dir Salida Ida", "Dir Destino Ida", "Ciudad Ida", "Hora Salida Ida", "Llegada Ida", 
            "Dir Salida Retorno", "Dir Destino Retorno", "Ciudad Retorno", "Hora Salida Retorno", "Llegada Retorno",
            "Perimetro Mamonal", "Notificacion", "Escolta", "Socializacion",
            "Ruta Salida", "Ruta Retorno", "Ruta Alterna",
            "Supervisor", "Conductor", "Nombre Escolta"
        ])

if "pdf_generado" not in st.session_state:
    st.session_state.pdf_generado = None
    st.session_state.pdf_nombre = ""
    st.session_state.url_ida = ""
    st.session_state.url_retorno = ""

# Mostrar logo en la barra lateral si existe
if LOGO_PATH:
    st.sidebar.image(LOGO_PATH, use_column_width=True)

st.sidebar.title("🚚 JV Soluciones PESV")
menu = st.sidebar.radio("Navegación", ["Nueva Planificación de Ruta", "Historial y Formatos"])

if menu == "Nueva Planificación de Ruta":
    # Encabezado principal
    col_logo, col_titulo = st.columns([1, 4])
    with col_logo:
        if LOGO_PATH:
            st.image(LOGO_PATH, width=130)
    with col_titulo:
        st.title("📋 Formato SGI-F-42: Planificación de Ruta")
        st.markdown("Sistema de Gestión Integral - PESV")
    
    with st.form("form_ruta"):
        st.subheader("1. Información General")
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha = st.date_input("Fecha", value=datetime.now())
        with col2:
            equipo = st.text_input("Equipo")
        with col3:
            cod_int = st.text_input("Cod Int")
            
        st.subheader("2. PLANIFICACIÓN DE SALIDA")
        col4, col5, col6 = st.columns(3)
        with col4:
            dir_salida_ida = st.text_input("Dir. salida (Ida)")
        with col5:
            dir_destino_ida = st.text_input("Dir. Destino (Ida)")
        with col6:
            ciudad_ida = st.text_input("Ciudad (Ida)", value="Cartagena")
            
        col7, col8 = st.columns(2)
        with col7:
            hora_salida_ida = st.time_input("Hora salida (Ida)", value=datetime.strptime("08:00", "%H:%M").time())
        with col8:
            hora_llegada_ida = st.time_input("Llegada (Ida)", value=datetime.strptime("10:00", "%H:%M").time())

        st.subheader("3. PLANIFICACIÓN DE RETORNO")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            dir_salida_ret = st.text_input("Dir. salida (Retorno)")
        with col_r2:
            dir_destino_ret = st.text_input("Dir. Destino (Retorno)")
        with col_r3:
            ciudad_ret = st.text_input("Ciudad (Retorno)", value="Cartagena")

        col_r4, col_r5 = st.columns(2)
        with col_r4:
            hora_salida_ret = st.time_input("Hora salida (Retorno)", value=datetime.strptime("14:00", "%H:%M").time())
        with col_r5:
            hora_llegada_ret = st.time_input("Llegada (Retorno)", value=datetime.strptime("16:00", "%H:%M").time())

        st.subheader("4. Verificaciones Antes de Arrancar")
        perimetro = st.checkbox("¿Perímetro Mamonal? Si la grúa sale del sector Mamonal, DEBE ir en Cama Baja o Camión Plancha.")
        notificacion = st.checkbox("¿Notificación? Ya se envió este plan por correo electrónico al líder del PESV.")
        escolta = st.checkbox("¿Escolta? Si supera el perímetro del barrio 20 de Julio, es obligatorio el acompañamiento de una camioneta guía.")
        socializacion = st.checkbox("¿Socialización? La ruta ya fue informada al conductor, supervisor y escoltas.")

        st.subheader("5. Descripción de Rutas (Identifique puntos críticos o cierres viales)")
        ruta_salida = st.text_area("Ruta de salida")
        ruta_retorno = st.text_area("Ruta de retorno")
        ruta_alterna = st.text_area("Ruta alterna")

        st.subheader("6. Firmas y Responsables")
        col9, col10, col11 = st.columns(3)
        with col9:
            supervisor = st.text_input("Nombre / Firma Supervisor")
        with col10:
            conductor = st.text_input("Nombre / Firma Conductor")
        with col11:
            nombre_escolta = st.text_input("Nombre / Firma Escolta (si aplica)")
        
        submitted = st.form_submit_button("Generar SGI-F-42, PDF y Rutas de Mapa")
        
        if submitted:
            # Guardar entrada en el historial
            nueva_ruta = pd.DataFrame([{
                "Fecha": str(fecha), "Equipo": equipo, "Cod Int": cod_int,
                "Dir Salida Ida": dir_salida_ida, "Dir Destino Ida": dir_destino_ida, "Ciudad Ida": ciudad_ida, 
                "Hora Salida Ida": str(hora_salida_ida), "Llegada Ida": str(hora_llegada_ida),
                "Dir Salida Retorno": dir_salida_ret, "Dir Destino Retorno": dir_destino_ret, "Ciudad Retorno": ciudad_ret, 
                "Hora Salida Retorno": str(hora_salida_ret), "Llegada Retorno": str(hora_llegada_ret),
                "Perimetro Mamonal": "Sí" if perimetro else "No",
                "Notificacion": "Sí" if notificacion else "No",
                "Escolta": "Sí" if escolta else "No",
                "Socializacion": "Sí" if socializacion else "No",
                "Ruta Salida": ruta_salida, "Ruta Retorno": ruta_retorno, "Ruta Alterna": ruta_alterna,
                "Supervisor": supervisor, "Conductor": conductor, "Nombre Escolta": nombre_escolta
            }])
            
            st.session_state.historial_rutas = pd.concat([st.session_state.historial_rutas, nueva_ruta], ignore_index=True)
            st.session_state.historial_rutas.to_csv(HISTORIAL_FILE, index=False)
            
            # Enlaces de Google Maps
            orig_ida_enc = urllib.parse.quote(f"{dir_salida_ida}, {ciudad_ida}")
            dest_ida_enc = urllib.parse.quote(f"{dir_destino_ida}, {ciudad_ida}")
            orig_ret_enc = urllib.parse.quote(f"{dir_salida_ret}, {ciudad_ret}")
            dest_ret_enc = urllib.parse.quote(f"{dir_destino_ret}, {ciudad_ret}")
            
            st.session_state.url_ida = f"https://www.google.com/maps/dir/?api=1&origin={orig_ida_enc}&destination={dest_ida_enc}"
            st.session_state.url_retorno = f"https://www.google.com/maps/dir/?api=1&origin={orig_ret_enc}&destination={dest_ret_enc}"

            # Creación del PDF
            class PDF(FPDF):
                def header(self):
                    if LOGO_PATH:
                        try:
                            self.image(LOGO_PATH, x=10, y=8, w=25)
                            self.set_x(38)
                            ancho_txt = 82
                        except Exception:
                            ancho_txt = 110
                    else:
                        ancho_txt = 110

                    self.set_font('Helvetica', 'B', 9)
                    self.cell(ancho_txt, 8, 'PLANIFICACION DE RUTA - PESV', 1, 0, 'C')
                    self.cell(80, 8, 'Codigo: SGI-F-42', 1, 1, 'C')
                    
                    if LOGO_PATH:
                        self.set_x(38)

                    self.set_font('Helvetica', '', 8)
                    self.cell(ancho_txt, 7, 'Versión: 2 | Fecha Emisión: 19/08/2025', 1, 0, 'C')
                    self.cell(80, 7, 'SISTEMA DE GESTION INTEGRAL', 1, 1, 'C')
                    self.ln(6)

            pdf = PDF()
            pdf.add_page()
            
            # Bloque 1: Info General
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(63, 7, f"Fecha: {fecha}", 1)
            pdf.cell(63, 7, f"Equipo: {equipo}", 1)
            pdf.cell(64, 7, f"Cod Int: {cod_int}", 1, ln=1)
            
            # Bloque 2: Salida
            pdf.set_fill_color(220, 220, 220)
            pdf.cell(190, 7, "PLANIFICACION DE SALIDA", 1, ln=1, fill=True, align='C')
            pdf.set_font("Helvetica", '', 8)
            pdf.cell(60, 7, f"Dir. salida: {dir_salida_ida}", 1)
            pdf.cell(60, 7, f"Dir. Destino: {dir_destino_ida}", 1)
            pdf.cell(70, 7, f"Ciudad: {ciudad_ida}", 1, ln=1)
            pdf.cell(95, 7, f"Hora salida: {hora_salida_ida}", 1)
            pdf.cell(95, 7, f"Llegada: {hora_llegada_ida}", 1, ln=1)

            # Bloque 3: Retorno
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(190, 7, "PLANIFICACION DE RETORNO", 1, ln=1, fill=True, align='C')
            pdf.set_font("Helvetica", '', 8)
            pdf.cell(60, 7, f"Dir. salida: {dir_salida_ret}", 1)
            pdf.cell(60, 7, f"Dir. Destino: {dir_destino_ret}", 1)
            pdf.cell(70, 7, f"Ciudad: {ciudad_ret}", 1, ln=1)
            pdf.cell(95, 7, f"Hora salida: {hora_salida_ret}", 1)
            pdf.cell(95, 7, f"Llegada: {hora_llegada_ret}", 1, ln=1)
            
            # Bloque 4: Verificaciones
            pdf.ln(3)
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(190, 7, "Antes de arrancar, asegurate de cumplir con lo siguiente:", 0, ln=1)
            pdf.set_font("Helvetica", '', 8)
            
            c_perimetro = "[X]" if perimetro else "[ ]"
            c_notif = "[X]" if notificacion else "[ ]"
            c_escolta = "[X]" if escolta else "[ ]"
            c_social = "[X]" if socializacion else "[ ]"
            
            pdf.cell(190, 6, f"{c_perimetro} Perimetro Mamonal? (Debe ir en Cama Baja o Camion Plancha si aplica)", 0, ln=1)
            pdf.cell(190, 6, f"{c_notif} Notificacion? (Enviado al lider del PESV por correo)", 0, ln=1)
            pdf.cell(190, 6, f"{c_escolta} Escolta? (Obligatorio si supera barrio 20 de Julio)", 0, ln=1)
            pdf.cell(190, 6, f"{c_social} Socializacion? (Ruta informada a conductor, supervisor y escoltas)", 0, ln=1)

            # Bloque 5: Rutas
            pdf.ln(3)
            pdf.set_font("Helvetica", 'B', 9)
            pdf.cell(190, 7, "RUTAS (Puntos criticos o cierres viales)", 1, ln=1, fill=True, align='C')
            pdf.set_font("Helvetica", '', 8)
            pdf.multi_cell(190, 6, f"Ruta de salida: {ruta_salida}", 1)
            pdf.multi_cell(190, 6, f"Ruta de retorno: {ruta_retorno}", 1)
            pdf.multi_cell(190, 6, f"Ruta alterna: {ruta_alterna}", 1)
            
            # Bloque 6: Firmas
            pdf.ln(10)
            pdf.cell(60, 7, f"Firma supervisor: {supervisor}", 0)
            pdf.cell(60, 7, f"Firma conductor: {conductor}", 0)
            pdf.cell(70, 7, f"Firma Escolta: {nombre_escolta}", 0, ln=1)
            
            pdf.ln(5)
            pdf.set_font("Helvetica", 'I', 8)
            pdf.cell(190, 7, "Se debe notificar al lider del PESV la planeacion de la ruta antes del inicio del recorrido por correo electronico.", 0, ln=1, align='C')

            st.session_state.pdf_generado = bytes(pdf.output())
            st.session_state.pdf_nombre = f"SGI-F-42_Ruta_{cod_int}_{fecha}.pdf"

    if st.session_state.pdf_generado is not None:
        st.success("✅ ¡Planificación (SGI-F-42) y rutas generadas con éxito!")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"""
                <a href="{st.session_state.url_ida}" target="_blank">
                    <button style="width:100%; background-color:#4285F4; color:white; padding:10px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
                        🗺️ Ver Ruta de Salida en Google Maps
                    </button>
                </a>
            """, unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"""
                <a href="{st.session_state.url_retorno}" target="_blank">
                    <button style="width:100%; background-color:#EA4335; color:white; padding:10px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
                        🗺️ Ver Ruta de Retorno en Google Maps
                    </button>
                </a>
            """, unsafe_allow_html=True)
            
        st.write("")
        
        st.download_button(
            label="📥 Descargar Documento SGI-F-42 en PDF",
            data=st.session_state.pdf_generado,
            file_name=st.session_state.pdf_nombre,
            mime="application/pdf",
            use_container_width=True
        )

elif menu == "Historial y Formatos":
    st.title("📂 Historial de Planificaciones PESV")
    
    if not st.session_state.historial_rutas.empty:
        st.dataframe(st.session_state.historial_rutas, use_container_width=True)
        
        csv = st.session_state.historial_rutas.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar Historial Completo (CSV)",
            csv,
            "historial_rutas_pesv.csv",
            "text/csv",
            key='download-csv'
        )
    else:
        st.info("No hay planificaciones registradas aún.")
