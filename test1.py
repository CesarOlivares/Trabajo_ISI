import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(layout="wide")

def credenciales():
    if st.session_state["user"].strip()=="admin" and st.session_state["contraseña"].strip()=="admin":
        st.session_state["autorizado"] = True
    else:
        st.session_state["desautorizado"] = False
        if not st.session_state["contraseña"]:
            st.warning("por favor pon contraseña")
        elif not st.session_state["usuario"]:
            st.warning("por favor pon usuario")
        else:
            st.error("usuario o contraseña invalidas")

def autorizar_usuario():
    if "autorizado" not in st.session_state:
        st.text_input(label="usuario: ",value="",key="user",on_change=credenciales)
        st.text_input(label="contraseña: ",value="",key="contraseña",type="password",on_change=credenciales)
        return False
    else:
        if st.session_state["autorizado"]:
            return True
        else:
            st.text_input(label="usuario: ",value="",key="user",on_change=credenciales)
            st.text_input(label="contraseña: ",value="",key="contraseña",type="password",on_change=credenciales)
            return False

if autorizar_usuario():
    #encabezado
    with st.container(border=True):
        st.header("Sistema de monitoreo de temperatura")

    #columnas desiguales
    with st.container(border=True):
        # proporción [1, 3, 1]
        col_izq, col_centro, col_der = st.columns([1, 3, 1])

        with col_izq:
            eleccion = st.radio(
        "Selecciona una opción:",
        ["Camion 1", "Camion 2", "Camion 3"],
        index=None 
    )
        
        with col_centro:
            if eleccion == "Camion 1":
                df = pd.DataFrame([[1,2,-1],[1,5,-1],[1,2,-1],[1,1,-1],[1,0,-1]], columns=["Limite superior de Temperatura", "Valor medido", "Limite inferior de Temperatura"])
                st.subheader("Camion 1")
                st.line_chart(df,x_label="Tiempo", y_label="Temperatura")

            if eleccion == "Camion 2":
                df = pd.DataFrame([[-1, -2,-10],[-1, -4,-10],[-1, -1,-10],[-1, -8,-10]], columns=["Limite superior de Temperatura", "Valor medido", "Limite inferior de Temperatura"])
                st.subheader("Camion 2")
                st.line_chart(df,x_label="Tiempo", y_label="Temperatura")

            if eleccion == "Camion 3":
                df = pd.DataFrame([[-1, 0,-10],[-1, -8,-10],[-1, -7,-10],[-1, -2,-10],[-1, -4,-10]], columns=["Limite superior de Temperatura", "Valor medido", "Limite inferior de Temperatura"])
                st.subheader("Camion 3")
                st.line_chart(df,x_label="Tiempo", y_label="Temperatura")

            if (eleccion != "Camion 1") and (eleccion != "Camion 2") and (eleccion != "Camion 3"):
                st.subheader("")
                st.line_chart([0, 0, 0, 0, 0],x_label="Tiempo", y_label="Temperatura")

                
        with col_der:
            st.success("Test exito")
            st.info("Test Informacion")
            st.warning("test warning")
            st.error("test Error")

    with st.container(border=True):
        st.success("este es el fondo")
