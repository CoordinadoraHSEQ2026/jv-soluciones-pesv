import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
from fpdf import FPDF

# Configuración de la página
st.set_page_config(page_title="JV Soluciones - PESV", page_icon="🚚", layout="wide")

# Inicializar el historial y variables temporales en sesión
if "historial_rutas" not in st.session_state:
    st.session_state.historial_rutas = pd.DataFrame(columns=[
        "Fecha", "Vehiculo", "Placa", "Origen", "Destino", "Ciudad", 
        "Hora Salida", "Hora Llegada", "Conductor Principal", 
        "Quien Elabora", "Quien Ejecuta", "Coordinador/Supervisor", 
        "Conductor Externo", "Requiere Escolta", "Ruta Retorno", "Observaciones"
    ])

if "pdf_generado" not in st.session_state:
    st.session_state.pdf_generado = None
    st.session_state.pdf_nombre = ""
    st.session_state.whatsapp_url = ""

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
            
        st.subheader("2. Planificación de Salida y Retorno")
        col4, col5, col6 = st.columns(3)
        with col4:
            origen = st.text_input("Dir. Salida (Origen)", value="Mamonal km6 MZ H Lt 10")
        with col5:
            destino = st.text_input("Dir. Destino", value="Oficinas seguros mundial")
        with col6:
            ciudad = st.text_input("Ciudad Salida", value="Cartagena")
            
        col7, col8, col_ret = st.columns(3)
        with col7:
            h_salida = st.time_input("Hora Salida", value=datetime.strptime("13:00", "%H:%M").time())
        with col8:
            h_llegada = st.time_input("Hora Llegada Estimada", value=datetime.strptime("14:00", "%H:%M").time())
        with col_ret:
            ruta_retorno = st.text_input("Ruta de Retorno", value="Misma ruta de origen")
            
        st.subheader("3. Personal Involucrado y Autorizaciones")
        col9, col10 = st.columns(2)
        with col9:
            quien_hace = st.text_input("Nombre de quien hace la ruta")
            quien_ejecuta = st.text_input("Nombre de quien ejecuta la ruta")
        with col10:
            coordinador = st.text_input("Nombre del Coordinador de Operaciones / Supervisor de Patio")
            conductor_ext = st.text_input("Nombre del conductor (si es vehículo externo)")

        st.subheader("4. Detalles Adicionales y Seguridad")
        col11, col12 = st.columns(2)
        with col11:
            escolta = st.selectbox("¿Requiere Escolta?", ["No", "Sí"])
        with col12:
            conductor = st.text_input("Nombre del Conductor Principal")
            
        observaciones = st.text_area("Observaciones de la Ruta / Recomendaciones de Seguridad", value="")
        
        submitted = st.form_submit_button("Generar Planificación y PDF")
        
        if submitted:
            # Guardar entrada en el historial
            nueva_ruta = pd.DataFrame([{
                "Fecha": str(fecha),
                "Vehiculo": vehiculo,
                "Placa": placa,
                "Origen": origen,
                "Destino": destino,
                "Ciudad": ciudad,
                "Hora Salida": str(h_salida),
                "Hora Llegada": str(h_llegada),
                "Conductor Principal": conductor,
                "Quien Elabora": quien_hace,
                "Quien Ejecuta": quien_ejecuta,
                "Coordinador/Supervisor": coordinador,
                "Conductor Externo": conductor_ext,
                "Requiere Escolta": escolta,
                "Ruta Retorno": ruta_retorno,
                "Observaciones": observaciones
            }])
            st.session_state.historial_rutas = pd.concat([st.session_state.historial_rutas, nueva_ruta], ignore_index=True)
            
            # Clase del PDF con Encabezado SGI-F-42
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
                ("Ruta de Retorno:", str(ruta_retorno)),
                ("Ciudad:", str(ciudad)),
                ("Hora Salida:", str(h_salida)),
                ("Hora Llegada:", str(h_llegada)),
                ("Conductor Principal:", str(conductor)),
                ("Elaborado Por:", str(quien_hace)),
                ("Ejecutado Por:", str(quien_ejecuta)),
                ("Coord. / Supervisor:", str(coordinador)),
                ("Conductor Ext.:", str(conductor_ext)),
                ("Requiere Escolta:", str(escolta)),
                ("Observaciones:", str(observaciones))
            ]
            
            for label, val in campos:
                pdf.set_font("Helvetica", 'B', 9)
                pdf.cell(60, 7, label, 1)
                pdf.set_font("Helvetica", '', 9)
                pdf.cell(130, 7, val, 1, new_x="LMARGIN", new_y="NEXT")
            
            # Guardar PDF y URL de WhatsApp en sesión
            st.session_state.pdf_generado = bytes(pdf.output())
            st.session_state.pdf_nombre = f"Planificacion_Ruta_{placa}_{fecha}.pdf"
            
            whatsapp_text = (
                f"🚚 *PLANIFICACION DE RUTA PESV (SGI-F-42)*\n"
                f"- Vehículo: {vehiculo} ({placa})\n"
                f"- Conductor: {conductor}\n"
                f"- Origen: {origen}\n"
                f"- Destino: {destino}\n"
                f"- Ruta Retorno: {ruta_retorno}\n"
                f"- Elabora: {quien_hace}\n"
                f"- Ejecuta: {quien_ejecuta}\n"
                f"- Coord/Supervisor: {coordinador}\n"
                f"- Fecha: {fecha} ({h_salida})"
            )
            encoded_text = urllib.parse.quote(whatsapp_text)
            st.session_state.whatsapp_url = f"https://api.whatsapp.com/send?text={encoded_text}"

    # Opciones de descarga fuera del formulario
    if st.session_state.pdf_generado is not None:
        st.success("✅ ¡Planificación guardada con éxito en el historial!")
        
        st.download_button(
            label="📥 Descargar Formato PDF Oficial",
            data=st.session_state.pdf_generado,
            file_name=st.session_state.pdf_nombre,
            mime="application/pdf"
        )
        
        st.markdown(f"""
            <a href="{st.session_state.whatsapp_url}" target="_blank">
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
