import streamlit as st
# import models.mysql as db
import pandas as pd

# Validación simple de usuario y clave con MySQL
def validarUsuario(usuario, clave):    
    """Permite la validación de usuario y clave

    Args:
        usuario (str): usuario a validar
        clave (str): clave del usuario

    Returns:
        bool: True usuario valido, False usuario invalido
    """

    # leer el csv usuarios.csv
    df = pd.read_csv('data/usuarios.csv')
    result = df.loc[(df['usuario']==usuario) & (df['usuario']==clave)]

    return len(result) > 0

def generarLogin():
    """Genera la ventana de login o muestra el menú si el login es valido
    """    
    # Validamos si el usuario ya fue ingresado    
    if 'usuario' in st.session_state:
        st.switch_page("pages/reportes.py")   
    else: 
        _, cent_co, _ = st.columns(3)
        with cent_co:
            st.image("static/escudo_audax.png", width=400)
        # Cargamos el formulario de login       
        with st.form('frmLogin'):
            parUsuario = st.text_input('Usuario')
            parPassword = st.text_input('Password', type='password')
            btnLogin = st.form_submit_button('Ingresar', type='primary')
            if btnLogin:
                if validarUsuario(parUsuario, parPassword):
                    st.session_state['usuario'] = parUsuario
                    # Si el usuario es correcto reiniciamos la app para que se cargue el menú
                    st.rerun()
                else:
                    # Si el usuario es invalido, mostramos el mensaje de error
                    st.error("Usuario o clave inválidos", icon=":material/gpp_maybe:")
        

