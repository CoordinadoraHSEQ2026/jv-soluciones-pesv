import streamlit as st
import pandas as pd
from datetime import datetime
import urllib.parse
from fpdf import FPDF

# Configuración de la página
st.set_page_config(page_title="JV Soluciones - PESV", page_icon="🚚", layout="wide")

# Inicializar historial y variables de sesión
if "historial_rutas" not in st.session_state:
    st.session_state.historial_rutas = pd.DataFrame(columns=[
        "Fecha", "Vehiculo", "Placa", "Origen", "Destino", "Ciudad Salida", 
        "Hora Salida ID", "Hora Llegada ID", 
        "Direccion Retorno", "Hora Salida Retorno", "Hora Llegada Retorno",
        "Conductor Principal", "Quien Elabora", "Quien Ejecuta", 
        "Coordinador/Supervisor", "Conductor Externo", "Requiere Escolta", "Observaciones"
    ])

if "pdf_generado" not in st.session_state:
    st.session_state.pdf_generado = None
    st.session_state.pdf_nombre = ""
    st.session_state.url_ida = ""
    st.session_state.url_retorno = ""

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
            
        st.subheader("2. Planificación de Salida (Ida)")
        col4, col5, col6 = st.columns(3)
        with col4:
            origen = st.text_input("Dir. Salida (Origen)", value="Mamonal km6 MZ H Lt 10")
        with col5:
            destino = st.text_input("Dir. Destino", value="Oficinas seguros mundial")
        with col6:
            ciudad = st.text_input("Ciudad Salida", value="Cartagena")
            
        col7, col8 = st.columns(2)
        with col7:
            h_salida = st.time_input("Hora Salida (Ida)", value=datetime.strptime("13:00", "%H:%M").time())
        with col8:
            h_llegada = st.time_input("Hora Llegada Estimada (Ida)", value=datetime.strptime("14:00", "%H:%M").time())

        st.subheader("3. Planificación de Retorno")
        col_r1, col_r2, col_r3 = st.columns(3)
        with col_r1:
            dir_retorno = st.text_input("Dirección de Retorno", value="Mamonal km6 MZ H Lt 10")
        with col_r2:
            h_salida_ret = st.time_input("Hora Salida (Retorno)", value=datetime.strptime("16:00", "%H:%M").time())
        with col_r3:
            h_llegada_ret = st.time_input("Hora Llegada Estimada (Retorno)", value=datetime.strptime("17:00", "%H:%M").time())

        st.subheader("4. Personal Involucrado y Autorizaciones")
        col9, col10 = st.columns(2)
        with col9:
            quien_hace = st.text_input("Nombre de quien hace la ruta")
            quien_ejecuta = st.text_input("Nombre de quien ejecuta la ruta")
        with col10:
            coordinador = st.text_input("Nombre del Coordinador de Operaciones / Supervisor de Patio")
            conductor_ext = st.text_input("Nombre del conductor (si es vehículo externo)")

        st.subheader("5. Detalles Adicionales y Seguridad")
        col11, col12 = st.columns(2)
        with col11:
            escolta = st.selectbox("¿Requiere Escolta?", ["No", "Sí"])
        with col12:
            conductor = st.text_input("Nombre del Conductor Principal")
            
        observaciones = st.text_area("Observaciones de la Ruta / Recomendaciones de Seguridad", value="")
        
        submitted = st.form_submit_button("Generar Planificación, PDF y Rutas de Mapa")
        
        if submitted:
            # Guardar entrada en el historial
            nueva_ruta = pd.DataFrame([{
                "Fecha": str(fecha),
                "Vehiculo": vehiculo,
                "Placa": placa,
                "Origen": origen,
                "Destino": destino,
                "Ciudad Salida": ciudad,
                "Hora Salida ID": str(h_salida),
                "Hora Llegada ID": str(h_llegada),
                "Direccion Retorno": dir_retorno,
                "Hora Salida Retorno": str(h_salida_ret),
                "Hora Llegada Retorno": str(h_llegada_ret),
                "Conductor Principal": conductor,
                "Quien Elabora": quien_hace,
                "Quien Ejecuta": quien_ejecuta,
                "Coordinador/Supervisor": coordinador,
                "Conductor Externo": conductor_ext,
                "Requiere Escolta": escolta,
                "Observaciones": observaciones
            }])
            st.session_state.historial_rutas = pd.concat([st.session_state.historial_rutas, nueva_ruta], ignore_index=True)
            
            # Crear enlaces de Google Maps para Ida y Retorno
            orig_encoded = urllib.parse.quote(f"{origen}, {ciudad}")
            dest_encoded = urllib.parse.quote(f"{destino}, {ciudad}")
            retorno_encoded = urllib.parse.quote(f"{dir_retorno}, {ciudad}")
            
            url_ida = f"https://www.google.com/maps/dir/?api=1&origin={orig_encoded}&destination={dest_encoded}"
            url_retorno = f"https://www.google.com/maps/dir/?api=1&origin={dest_encoded}&destination={retorno_encoded}"
            
            st.session_state.url_ida = url_ida
            st.session_state.url_retorno = url_retorno

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
            
            pdf.set_font("Helvetica", 'B', 11)
            pdf.cell(190, 8, text="DETALLE DE PLANIFICACION DE RUTA", new_x="LMARGIN", new_y="NEXT", align='C')
            pdf.ln(3)
            
            campos = [
                ("Fecha:", str(fecha)),
                ("Equipo / Vehiculo:", str(vehiculo)),
                ("Cod Int / Placa:", str(placa)),
                ("Origen (Salida):", str(origen)),
                ("Destino:", str(destino)),
                ("Ciudad:", str(ciudad)),
                ("Hora Salida (Ida):", str(h_salida)),
                ("Hora Llegada (Ida):", str(h_llegada)),
                ("Mapa Ruta Ida:", url_ida),
                ("Direccion Retorno:", str(dir_retorno)),
                ("Hora Salida (Ret):", str(h_salida_ret)),
                ("Hora Llegada (Ret):", str(h_llegada_ret)),
                ("Mapa Ruta Retorno:", url_retorno),
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
                pdf.cell(50, 7, label, 1)
                
                # Si es un enlace a mapa, ponerlo azul y clicable
                if label.startswith("Mapa Ruta"):
                    pdf.set_font("Helvetica", 'U', 9)
                    pdf.set_text_color(0, 0, 255) # Azul
                    pdf.cell(140, 7, "Clic aqui para abrir en Google Maps", 1, new_x="LMARGIN", new_y="NEXT", link=val)
                    pdf.set_text_color(0, 0, 0)   # Volver a negro
                else:
                    pdf.set_font("Helvetica", '', 9)
                    # Limitar largo por si el texto es muy extenso para una celda
                    texto = val if len(val) < 85 else val[:82] + "..."
                    pdf.cell(140, 7, texto, 1, new_x="LMARGIN", new_y="NEXT")
            
            # Guardar PDF en sesión
            st.session_state.pdf_generado = bytes(pdf.output())
            st.session_state.pdf_nombre = f"Planificacion_Ruta_{placa}_{fecha}.pdf"

    # Mostrar botones FUERA del formulario
    if st.session_state.pdf_generado is not None:
        st.success("✅ ¡Planificación y rutas generadas con éxito!")
        
        # Botones de mapas visuales en la app
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown(f"""
                <a href="{st.session_state.url_ida}" target="_blank">
                    <button style="width:100%; background-color:#4285F4; color:white; padding:10px; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">
                        🗺️ Ver Ruta de Ida en Google Maps
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
            
        st.write("") # Espaciador
        
        # Botón para descargar el PDF
        st.download_button(
            label="📥 Descargar Formato PDF Oficial",
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
        st.info("No hay planificaciones registradas en la sesión actual.")
