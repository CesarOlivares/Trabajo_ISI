import streamlit as st
import numpy as np
import pandas as pd
import time
import datetime
import altair as alt
import os

#espacio de configuracion de la pagina
st.set_page_config(layout="wide", page_title="Monitor BioVertia Pro")
FILE_NAME = "camiones.xlsx"
# fin de espacio de configuracion

#definicion de las clases 
class Sensor:
    def __init__(self, serial_id: int, umbral_max: float, umbral_min: float, historial_inicial=None):
        self.serial_id = serial_id  
        self.umbral_max = umbral_max
        self.umbral_min = umbral_min
        
        cols_esperadas = ["Hora", "Valor", "LimSup", "LimInf"]
        
        # espacio dedicaco a verificar el historial de datos de un sensor
        if historial_inicial is not None and not historial_inicial.empty:
            # Si faltan columnas, descartamos los datos y empezamos de cero
            if not all(col in historial_inicial.columns for col in cols_esperadas):
                self.historial_db = pd.DataFrame(columns=cols_esperadas) #.historial_db genera un historial de database simulado
            else:
                self.historial_db = historial_inicial
        else:
            # Si no hay datos, iniciamos vacío y generamos dummy data
            self.historial_db = pd.DataFrame(columns=cols_esperadas)
            self._generar_datos_iniciales()

    # metodo de simulacion de datos iniciales
    def _generar_datos_iniciales(self):
        now = datetime.datetime.now()
        data = []
        #este genera unos datos de simulacio
        for i in range(10):
            tiempo = now - datetime.timedelta(seconds=(10-i)*5)
            valor = np.random.uniform(self.umbral_min, self.umbral_max)
            data.append({
                "Hora": tiempo.strftime("%H:%M:%S"),
                "Valor": valor,
                "LimSup": self.umbral_max,
                "LimInf": self.umbral_min
            })
        self.historial_db = pd.concat([self.historial_db, pd.DataFrame(data)], ignore_index=True)

    def Lectura_simulacion(self, id_hoja_excel=None):
        """Simula dato, actualiza RAM y guarda en Excel si se pide"""
        # 1. Crear dato nuevo
        valor_nuevo = np.random.uniform(self.umbral_min - 2, self.umbral_max + 2)
        hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
        
        nueva_fila = pd.DataFrame([{
            "Hora": hora_actual,
            "Valor": valor_nuevo,
            "LimSup": self.umbral_max,
            "LimInf": self.umbral_min
        }])
        
        # 2. Actualizar
        self.historial_db = pd.concat([self.historial_db, nueva_fila], ignore_index=True)

        #limpieza de datos en caso de ser necesario para optimizar memoria
        if len(self.historial_db) > 100:
            self.historial_db = self.historial_db.iloc[-100:]

        # 3. Guardar en Excel
        if id_hoja_excel:
            try:
                self._actualizar_excel(id_hoja_excel)
            except Exception as e:
                print(f"⚠️ No se pudo guardar Excel (Posiblemente abierto): {e}")

    def _actualizar_excel(self, sheet_name):
        # Usamos 'try' interno por si el archivo está bloqueado por el usuario
        with pd.ExcelWriter(FILE_NAME, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_meta = pd.DataFrame([{
                "Serial_ID": self.serial_id, 
                "Umbral_Max": self.umbral_max, 
                "Umbral_Min": self.umbral_min
            }])
            df_meta.to_excel(writer, sheet_name=sheet_name, index=False, startrow=0)            
            # Historial (Fila 3 en adelante)
            self.historial_db.to_excel(writer, sheet_name=sheet_name, index=False, startrow=3)

class Camion:
    def __init__(self, id_camion: str, patente: str, sensor_asignado: Sensor):
        self.id_camion = id_camion
        self.patente = patente
        self.asignacion = sensor_asignado

    def __str__(self):
        return f"{self.id_camion} | {self.patente}"


#fin de clases
    
#gestion del excel de datos

def inicializar_excel_si_no_existe():
    if not os.path.exists(FILE_NAME):
        try:
            with pd.ExcelWriter(FILE_NAME, engine='openpyxl') as writer:
                for i in range(1, 201):
                    id_cam = f"C-{i:03d}"
                    temp_sensor = Sensor(1000+i, 10.0, -5.0) # Sensor temporal para datos iniciales
                    
                    # Guardamos estructura inicial
                    df_meta = pd.DataFrame([{"Serial_ID": 1000+i, "Umbral_Max": 10.0, "Umbral_Min": -5.0}])
                    df_meta.to_excel(writer, sheet_name=id_cam, index=False, startrow=0)
                    temp_sensor.historial_db.to_excel(writer, sheet_name=id_cam, index=False, startrow=3)
            return True
        except Exception as e:
            st.error(f"No se pudo crear el archivo: {e}")
            return False
    return False

@st.cache_resource
#esta funcion carga los datos de un excel que tiene la informacion de los camiones y el sensor que tiene dentro y al
#leer esta informacion traduce los datos leidos a objetos
def cargar_datos_desde_excel():
    inicializar_excel_si_no_existe()
    flota = {}
    try:
        xls = pd.ExcelFile(FILE_NAME)
        for sheet_name in xls.sheet_names:
            try:
                #lee los parametros
                df_meta = pd.read_excel(xls, sheet_name=sheet_name, nrows=1)
                
                if df_meta.empty or "Serial_ID" not in df_meta.columns:
                    continue
                
                serial_id = int(df_meta.iloc[0]["Serial_ID"])
                u_max = float(df_meta.iloc[0]["Umbral_Max"])
                u_min = float(df_meta.iloc[0]["Umbral_Min"])
                
                #Lee Historial
                df_historial = pd.read_excel(xls, sheet_name=sheet_name, skiprows=3)
                
                #Crear Objetos
                nuevo_sensor = Sensor(serial_id, u_max, u_min, historial_inicial=df_historial)
                
                parts = sheet_name.split("-")
                num = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                patente = f"JJ-KL-{num:02d}"
                
                nuevo_camion = Camion(sheet_name, patente, nuevo_sensor)
                flota[str(nuevo_camion)] = nuevo_camion
                
            except Exception as e:
                print(f"Error en hoja {sheet_name}: {e}")
                continue # Si falla una hoja, seguimos con las demás

    except Exception as e:
        st.error(f"Error accediendo al archivo Excel: {e}")
        return {}
        
    return flota

#sistema de login de pagina
def credenciales():
    # Validamos las credenciales almacenadas en el estado
    user = st.session_state.get("user", "").strip()
    pwd = st.session_state.get("contraseña", "").strip()
    
    if user == "admin" and pwd == "admin":
        st.session_state["autorizado"] = True
    else:
        st.session_state["autorizado"] = False
        st.error("Usuario o contraseña incorrectos")

def autorizar_usuario():
    #Inicializar estado si no existe
    if "autorizado" not in st.session_state:
        st.session_state["autorizado"] = False
    
    #Si ya está autorizado, dejamos pasar al código principal
    if st.session_state["autorizado"]:
        return True
    
    #Diseño del login
    col_izq, col_centro, col_der = st.columns([1, 2, 1])
    
    with col_centro:
        st.write("") 
        st.write("") 
        with st.container(border=True):
            st.markdown("## Acceso Monitoreo de Temperatura")    
            #Inputs (esperan al botón)
            st.text_input("Usuario", key="user", placeholder="Ingrese usuario...")
            st.text_input("Contraseña", type="password", key="contraseña", placeholder="Ingrese contraseña...")
            
            st.write("") # Espacio
            
            #Boton de inicio de sesion
            st.button("Iniciar Sesión", on_click=credenciales, type="primary", use_container_width=True)
            
        return False
    

#bloque de aplicacion principal

    
# Carga de datos
datos_camiones = cargar_datos_desde_excel()

if autorizar_usuario():
    st.title("Sistema de monitoreo de Temperatura")

    # Layout de 3 Columnas
    col_izq, col_centro, col_der = st.columns([1, 3, 1])

    #columna izquierda
    with col_izq:
        st.subheader("Flota")
        busqueda = st.text_input("Buscar ID/Patente", placeholder="Eje: C-001").upper()
        
        if datos_camiones:
            opciones = list(datos_camiones.keys())
            filtradas = [op for op in opciones if busqueda in op.upper()]
            
            with st.container(height=450, border=True):
                if filtradas:
                    seleccion = st.radio("Resultados:", options=filtradas, label_visibility="collapsed")
                else:
                    st.warning("No encontrado.")
                    st.stop()
        else:
            st.error("Error crítico de datos. Reinicia.")
            st.stop()

    # Obtenemos objetos seleccionados
    camion_actual = datos_camiones[seleccion]
    sensor_actual = camion_actual.asignacion

    #columna derecha
    with col_der:
        st.write("### Control")
        
        #Definimos el interruptor
        monitoreo_activo = st.toggle("Activar Monitoreo en Vivo")
        
        #Lógica de Métricas y Alertas
        if not sensor_actual.historial_db.empty:
            ultimo_dato = sensor_actual.historial_db.iloc[-1]["Valor"]
            promedio = sensor_actual.historial_db["Valor"].mean()
            
            st.metric("Temperatura Promedio", f"{promedio:.2f} °C")

            #Se supera cota superior
            if ultimo_dato > sensor_actual.umbral_max:
                st.metric("Temperatura Actual", f"{ultimo_dato:.2f} °C", delta=f"{ultimo_dato - sensor_actual.umbral_max:.2f} °C (Exceso)", delta_color="inverse")
                st.error(f"¡ALERTA CRÍTICA! Temp Alta ({ultimo_dato:.2f} > {sensor_actual.umbral_max})")
            
            #Se supera cota inferior
            elif ultimo_dato < sensor_actual.umbral_min:
                st.metric("Temperatura Actual", f"{ultimo_dato:.2f} °C", delta=f"{ultimo_dato - sensor_actual.umbral_min:.2f} °C (Baja)", delta_color="inverse")
                st.error(f"¡ALERTA CRÍTICA! Congelamiento ({ultimo_dato:.2f} < {sensor_actual.umbral_min})")
            
            #Todo normal
            else:
                st.metric("Temperatura Actual", f"{ultimo_dato:.2f} °C", delta="Normal")
                st.success("Estado: Temperatura Óptima")
        
        st.divider()

        #Botón de Reinicio, este solo limpia la memoria actual
        if st.button("Reiniciar Datos", type="primary", use_container_width=True):
            sensor_actual.historial_db = pd.DataFrame(columns=["Hora", "Valor", "LimSup", "LimInf"])
            sensor_actual._generar_datos_iniciales()
            st.rerun()

    #columna central
    with col_centro:
        st.subheader(f"Análisis: {camion_actual.id_camion}")
        
        if not sensor_actual.historial_db.empty:
            #Copia de seguridad para no romper la base de datos
            df_grafico = sensor_actual.historial_db.copy()
            
            #Transformamos a formato largo para Altair
            df_melt = df_grafico.melt(
                id_vars='Hora', 
                value_vars=['Valor', 'LimSup', 'LimInf'], 
                var_name='Tipo', 
                value_name='Temp'
            )
            
            #creamos el grafico
            c = alt.Chart(df_melt).mark_line().encode(
                x=alt.X('Hora', title='Hora de Lectura'),
                y=alt.Y('Temp', title='Temperatura [C°]', scale=alt.Scale(zero=False)),
                color=alt.Color('Tipo', legend=alt.Legend(title="Referencias"), scale=alt.Scale(
                    domain=['Valor', 'LimSup', 'LimInf'],
                    range=['#10B981', '#EF4444', '#3B82F6']
                )),
                
                
                tooltip=[
                    alt.Tooltip('Hora', title='Hora'),
                    alt.Tooltip('Tipo', title='Variable'),
                    alt.Tooltip('Temp', title='Temp [°C]', format='.2f')
                ]
            ).properties(height=350).interactive()
            
            st.altair_chart(c, use_container_width=True)
            
            #Tabla de Alertas
            st.write("##### Eventos Recientes")
            df = sensor_actual.historial_db
            criticos = df[ (df["Valor"] > df["LimSup"]) | (df["Valor"] < df["LimInf"]) ].copy()
            
            if not criticos.empty:
                criticos["Alerta"] = np.where(criticos["Valor"] > criticos["LimSup"], "Sobrecalentamiento", "Congelamiento")
                
                st.dataframe(
                    criticos[["Hora", "Valor", "Alerta"]].rename(columns={"Valor": "Temp [C°]"}).tail(5).sort_values("Hora", ascending=False),
                    use_container_width=True, 
                    hide_index=True
                )
            else:
                st.success("Operación estable sin alertas.")

    #bucle de simulacion de datos en "tiempo real"
    if monitoreo_activo:
        time.sleep(1.5) # Pausa para no saturar disco duro
        # Recorremos la flota
        for key, camion in datos_camiones.items():
            # Solo guardamos en Excel el camión que estamos mirando para no bloquear el PC
            if camion.id_camion == camion_actual.id_camion:
                camion.asignacion.Lectura_simulacion(id_hoja_excel=camion.id_camion)
            else:
                camion.asignacion.Lectura_simulacion(id_hoja_excel=None)
        st.rerun()



