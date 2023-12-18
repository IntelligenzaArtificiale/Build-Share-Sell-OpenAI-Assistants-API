import openai
from openai import OpenAI
from tempfile import NamedTemporaryFile
import streamlit as st
import time


st.title("Assistant BUILDER")


openaiKey = st.text_input("Inserisci la tua API Key di OpenAI")

def upload_file(file_path):
	# Upload a file with an "assistants" purpose
	file_to_upload = client.files.create(
  	file=open(file_path, "rb"),
  	purpose='assistants'
	)
	return file_to_upload

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
            if len(file_up) > 1:
                for file in file_up:
                    with NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(file.read())
                        st.write(tmp_file.name)

                        #carico il file su openai
                        file = client.files.create(
                        file=open(tmp_file.name, "rb"),
                        purpose='assistants'
                        )
                        stored_file.append(file)
                        st.write(file)
                        
            else:
                file = client.files.create(
                    file=open(file_up.name, "rb"),
                    purpose='assistants'
                    )
                stored_file.append(file)
                st.write(file)

    if st.button("Crea Assistente"):

        with st.status("Carico i documenti su OpenAI..", expanded=True) as status:

            

            if file_up: 
                st.write("Carico i file su OpenAI..")
                time.sleep(2)
                status.update(label="Creo l'assistente..")
                st.write(stored_file)
                my_assistant = client.beta.assistants.create(
                    instructions=prompt_sistema,
                    name=nome_assistente,
                    tools=[{"type": "retrieval"}],
                    model=modello_assistente,
                    file_ids=stored_file
                )
                st.write(my_assistant)
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
                st.write(my_assistant)
                status.update(label="Assistente creato con successo", state="complete")

                st.success("Assistente creato con successo")
                st.info("L'id dell'assistente è: " + my_assistant.id)
                st.error("Ricorda di salvare l'id dell'assistente per poterlo utilizzare in seguito")

        