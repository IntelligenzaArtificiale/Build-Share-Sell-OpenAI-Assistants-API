import openai
from openai import OpenAI
from tempfile import NamedTemporaryFile
import streamlit as st
import time


st.title("Assistant BUILDER")


openaiKey = st.text_input("Inserisci la tua API Key di OpenAI")

def upload_to_openai(filepath):
    """Upload a file to OpenAI and return its file ID."""
    with open(filepath, "rb") as file:
        response = openai.files.create(file=file.read(), purpose="assistants")
    return response.id

if openaiKey:

    import os

    os.environ["OPENAI_API_KEY"] = openaiKey
    openai.api_key = openaiKey
    client = OpenAI()
    col1, col2 = st.columns(2)

    with col1:
        nome_assistente = st.text_input("Nome dell'assistente")

    with col2:
        modello_assistente = st.selectbox(
        'Scegli il modello ',
        ('gpt-4-1106-preview', 'gpt-4-1106-preview', 'gpt-4-1106-preview'))

    if nome_assistente and modello_assistente:

        prompt_sistema = st.text_area("Prompt del sistema", height=200)

    stored_file = []

    if st.checkbox("Vuoi caricare File ? "):
        file_up = st.file_uploader("Carica il file", type=['csv',"txt","pdf"] ,accept_multiple_files = True)
        

        if file_up:
            if st.button("Carica i file su OpenAI"):
                with st.status("Carico i file su OpenAI..", expanded=True) as status:
                    for file in file_up:
                        time.sleep(2)
                        status.update(label="Sto caricando il file: " + file.name)
                        with open(f"{file.name}", "wb") as f:
                            f.write(file.getbuffer())
                        additional_file_id = upload_to_openai(f"{file.name}")
                        st.write(additional_file_id)
                        stored_file.append(additional_file_id)
                    status.update(label="File caricati con successo", state="complete")



    if (st.button("Crea Assistente") and nome_assistente and modello_assistente and prompt_sistema):

        with st.status("Mi sto collegando ad OpenAI..", expanded=True) as status:

            if file_up: 
                time.sleep(2)
                status.update(label="Creo l'assistente..")
                st.write(stored_file)
                my_assistant = client.beta.assistants.create(
                    instructions=prompt_sistema,
                    name=nome_assistente,
                    tools=[{"type": "retrieval"}],
                    model=modello_assistente,
                    file_ids=stored_file,
                )
                time.sleep(2)
                status.update(label="Assistente creato con successo", state="complete")
                
                st.success("Assistente creato con successo")
                st.info("L'id dell'assistente è: " + my_assistant.id)
                st.error("Ricorda di salvare l'id dell'assistente per poterlo utilizzare in seguito")

            else:
                status.update(label="Creo l'assistente..")
                my_assistant = client.beta.assistants.create(
                    instructions=prompt_sistema,
                    name=nome_assistente,
                    model=modello_assistente,
                )
                time.sleep(2)
                status.update(label="Assistente creato con successo", state="complete")

                st.success("Assistente creato con successo")
                st.info("L'id dell'assistente è: " + my_assistant.id)
                st.error("Ricorda di salvare l'id dell'assistente per poterlo utilizzare in seguito")

        