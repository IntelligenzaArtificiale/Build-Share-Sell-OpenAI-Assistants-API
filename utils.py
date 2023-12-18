import zipfile
import os
import yaml
import openai
import streamlit as st


def upload_to_openai(file):
    """Upload a file to OpenAI and return its file ID."""
    with open(file.name, "rb") as f:
        response = openai.files.create(file=f.read(), purpose="assistants")
    return response.id if response else None



def create_assistant_from_config_file(file_up, client):
    stored_file = []

    with st.spinner("Estrazione e caricamento file in corso..."):
        #cambia l'estensione del file da .iaItaliaBotConfig a .zip
        with open("config_assistente.zip", "wb") as f:
            f.write(file_up.getbuffer())
        f.close()

        with zipfile.ZipFile("config_assistente.zip", "r") as zip_ref:
            zip_ref.extractall("temp_folder")

        with open("temp_folder/config_assistente.yaml", "r") as yaml_file:
            config_data = yaml.safe_load(yaml_file)
            nome_assistente = config_data.get('name', '')
            modello_assistente = config_data.get('model', '')
            prompt_sistema = config_data.get('prompt', '')
            st.write("Nome Assistente: " + nome_assistente)
            st.write("Modello Assistente: " + modello_assistente)


        if os.path.exists("temp_folder"):
            for root, dirs, files in os.walk("temp_folder"):
                for file in files:
                    if file != "config_assistente.yaml":
                        additional_file_id = upload_to_openai(open(os.path.join(root, file), "rb"))
                        if additional_file_id:
                            stored_file.append(additional_file_id)

            my_assistant = client.beta.assistants.create(
                instructions=prompt_sistema,
                name=nome_assistente,
                tools=[{"type": "retrieval"}],
                model=modello_assistente,
                file_ids=stored_file,
            )

    return my_assistant
