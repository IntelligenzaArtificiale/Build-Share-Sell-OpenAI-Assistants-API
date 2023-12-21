import zipfile
import os
import yaml
import openai
import streamlit as st

def clean_environment():
    """Clean up environment variables."""
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    if "OPENAI_ORGANIZATION_ID" in os.environ:
        del os.environ["OPENAI_ORGANIZATION_ID"]
    if "OPENAI_DEFAULT_ORGANIZATION_ID" in os.environ:
        del os.environ["OPENAI_DEFAULT_ORGANIZATION_ID"]


def upload_to_openai(file):
    """Upload a file to OpenAI and return its file ID."""
    with open(file.name, "rb") as f:
        response = openai.files.create(file=f.read(), purpose="assistants")
    return response.id if response else None


def export_assistant(nome_assistente, modello_assistente, prompt_sistema, file_up):
    file_yaml = open("config_assistente.yaml", "w")
    file_yaml.write("name: " + nome_assistente + "\n")
    file_yaml.write("model: " + modello_assistente + "\n")
    file_yaml.close()

    #Crea file.txt per sistem_prompt
    file_prompt = open("prompt.txt", "w")
    file_prompt.write(prompt_sistema)
    file_prompt.close()


    #CREO IL FILE ZIP
    zip_file = zipfile.ZipFile("config_assistente.zip", "w")
    zip_file.write("config_assistente.yaml")
    zip_file.write("prompt.txt")

    if file_up:
        for file in file_up:
            with open(file.name, "rb") as f:
                zip_file.write(file.name)
    zip_file.close()

    return open("config_assistente.zip", "rb")



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
            st.write("Nome Assistente: " + nome_assistente)
            st.write("Modello Assistente: " + modello_assistente)

        with open("temp_folder/prompt.txt", "r") as prompt_file:
            prompt_sistema = prompt_file.read()


        if os.path.exists("temp_folder"):
            for root, dirs, files in os.walk("temp_folder"):
                for file in files:
                    if file != "config_assistente.yaml" and file != "prompt.txt":
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
