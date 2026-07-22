import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
from fpdf import FPDF

# Configuración de la página
st.set_page_config(page_title="JV Soluciones - PESV", page_icon="🚚", layout="wide")

# Inicializar el historial en la memoria del sistema si no existe
if "historial_rutas" not in st.session_state:
    st.session_state.historial_rutas = pd.DataFrame(columns=[
        "Fecha", "Vehiculo", "Placa", "Origen", "Destino", 
        "Ciudad", "Hora Salida", "Hora Llegada", "Conductor", "Observaciones"
    ])

st.sidebar.title("🚚 JV Soluciones PESV")
menu = st.sidebar.radio("Navegación", ["Nueva Planificación de Ruta", "Historial y Formatos"])

if menu == "Nueva Planificación de Ruta":
    st.title("📋 Formato de Planificación de Ruta (PESV)")
    st.markdown("Sistema de Gestión Integral - Control de Movilización")
    
    with st.form("form_ruta"):
        st.subheader("1. Información General del Vehículo / Equipo")
        col1, col2, col3 = st.columns(3)
        with col1:
            fecha = st.date_input("Fecha", value=datetime.now())
        with col2:
            vehiculo = st.text_input("Equipo / Vehículo", value="Moto Suzuki Gsx125")
        with col3:
            placa = st.text_input("Cod Int / Placa", value="LZB 96G")
            
        st.subheader("2. Planificación de Salida")
        col4, col5, col6 = st.columns(3)
        with col4:
            origen = st.text_input("Dir. Salida (Origen)", value="Mamonal km6 MZ H Lt 10")
        with col5:
            destino = st.text_input("Dir. Destino", value="Oficinas seguros mundial")
        with col6:
            ciudad = st.text_input("Ciudad Salida", value="Cartagena")
            
        col7, col8 = st.columns(2)
        with col7:
            h_salida = st.time_input("Hora Salida", value=datetime.strptime("13:00", "%H:%M").time())
        with col8:
            h_llegada = st.time_input("Hora Llegada Estimada", value=datetime.strptime("14:00", "%H:%M").time())
            
        st.subheader("3. Conductor y Observaciones")
        conductor = st.text_input("Nombre del Conductor", value="")
        observaciones = st.text_area("Observaciones de la Ruta / Recomendaciones de Seguridad", value="")
        
        submitted = st.form_submit_button("Generar Planificación y PDF")
        
        if submitted:
            # Nueva entrada para el historial
            nueva_ruta = pd.DataFrame([{
                "Fecha": str(fecha),
                "Vehiculo": vehiculo,
                "Placa": placa,
                "Origen": origen,
                "Destino": destino,
                "Ciudad": ciudad,
                "Hora Salida": str(h_salida),
                "Hora Llegada": str(h_llegada),
                "Conductor": conductor,
                "Observaciones": observaciones
            }])
            
            # Guardar en la memoria persistente del sistema
            st.session_state.historial_rutas = pd.concat([st.session_state.historial_rutas, nueva_ruta], ignore_index=True)
            
            st.success("✅ ¡Planificación guardada con éxito en el historial!")
            
            # Clase personalizada para el PDF con Encabezado SGI-F-42
            class PDF(FPDF):
                def header(self):
                    self.set_font('Helvetica', 'B', 9)
                    self.cell(110, 8, 'PLANIFICACION DE LA RUTA PESV', 1, 0, 'L')
                    self.cell(80, 8, 'Codigo: SGI-F-42', 1, 1, 'L')
                    
                    self.set_font('Helvetica', '', 8)
                    self.cell(110, 7, 'SISTEMA DE GESTION INTEGRAL', 1, 0, 'L')
                    self.cell(80, 7, 'Version digital: 1', 1, 1, 'L')
                    
                    self.cell(110, 7, '', 0, 0, 'L')
                    self.cell(80, 7, 'Fecha de actualizacion: 22/07/2026', 1, 1, 'L')
                    self.ln(6)

            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=10)
            
            pdf.set_font("Helvetica", 'B', 11)
            pdf.cell(190, 8, text="DETALLE DE PLANIFICACION DE RUTA", new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(3)
            
            campos = [
                ("Fecha:", str(fecha)),
                ("Equipo / Vehiculo:", str(vehiculo)),
                ("Cod Int / Placa:", str(placa)),
                ("Origen:", str(origen)),
                ("Destino:", str(destino)),
                ("Ciudad:", str(ciudad)),
                ("Hora Salida:", str(h_salida)),
                ("Hora Llegada:", str(h_llegada)),
                ("Conductor:", str(conductor)),
                ("Observaciones:", str(observaciones))
            ]
            
            for label, val in campos:
                pdf.set_font("Helvetica", 'B', 9)
                pdf.cell(50, 7, label, 1)
                pdf.set_font("Helvetica", '', 9)
                pdf.cell(140, 7, val, 1, new_x="LMARGIN", new_y="NEXT")
            
            # Corrección del método output para fpdf2
            pdf_bytes = bytes(pdf.output())
            
            st.download_button(
                label="📥 Descargar Formato PDF Oficial",
                data=pdf_bytes,
                file_name=f"Planificacion_Ruta_{placa}_{fecha}.pdf",
                mime="application/pdf"
            )
            
            # Botón para compartir por WhatsApp
            whatsapp_text = f"🚚 *PLANIFICACION DE RUTA PESV (SGI-F-42)*\n- Vehículo: {vehiculo} ({placa})\n- Conductor: {conductor}\n- Origen: {origen}\n- Destino: {destino}\n- Fecha: {fecha} ({h_salida})"
            encoded_text = urllib.parse.quote(whatsapp_text)
            whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"
            
            st.markdown(f"""
                <a href="{whatsapp_url}" target="_blank">
                    <button style="background-color:#25D366; color:white; padding:10px 20px; border:none; border-radius:5px; font-size:15px; cursor:pointer; font-weight:bold; margin-top:10px;">
                        💬 Compartir Planificación por WhatsApp
                    </button>
                </a>
            """, unsafe_allow_html=True)

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
        st.info("No hay planificaciones registradas en la sesión actual.")
