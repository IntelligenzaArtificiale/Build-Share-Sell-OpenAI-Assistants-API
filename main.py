import openai
import streamlit as st
import time
import os
import zipfile
import yaml

st.title("Assistant BUILDER & SHARING")

utilizzo = st.selectbox("Ciao, cosa vuoi fare?", ("Crea o Importa un Assistente", "Usa un Assistente"))

openaiKey = st.text_input("Inserisci la tua API Key di OpenAI")

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


if openaiKey:
    os.environ["OPENAI_API_KEY"] = openaiKey
    openai.api_key = openaiKey
    client = openai.OpenAI()

    if utilizzo != "Usa un Assistente":
        scelta_creazione = st.selectbox(
            'Cosa vuoi fare?',
            ('Crea un Assistente da Zero', 'Importa un Assistente'),
            index=0
        )

        if scelta_creazione == "Crea un Assistente da Zero":
            col1, col2 = st.columns(2)

            with col1:
                nome_assistente = st.text_input("Nome dell'assistente")

            with col2:
                modello_assistente = st.selectbox(
                    'Scegli il modello',
                    ('gpt-4-1106-preview', 'gpt-4'),
                    index=0
                )

            if nome_assistente and modello_assistente:
                prompt_sistema = st.text_area("Prompt del sistema", height=200)
                carica_file = st.checkbox("Vuoi caricare File? ")

                stored_file = []
                if carica_file:
                    file_up = st.file_uploader("Carica il file", type=['csv', 'txt', 'pdf'], accept_multiple_files=True)
                    if file_up:
                        if st.button("Carica File"):
                            with st.status("Caricamento file su OpenAI in corso...", expanded=True) as status:
                                for file in file_up:
                                    time.sleep(2)
                                    status.update(label="Sto caricando il file: " + file.name)
                                    with open(file.name, "wb") as f:
                                        f.write(file.getbuffer())
                                    additional_file_id = upload_to_openai(file)
                                    if additional_file_id:
                                        st.write("File caricato con successo: " + file.name)
                                        stored_file.append(additional_file_id)
                                status.update(label="File caricati con successo", state="complete", expanded=False)

                if st.button("Crea Assistente") and prompt_sistema:
                    with st.status("Creazione assistente in corso...", expanded=True) as status:
                        time.sleep(2)
                        status.update(label="Creo l'assistente...")
                        if stored_file:
                            my_assistant = client.beta.assistants.create(
                                instructions=prompt_sistema,
                                name=nome_assistente,
                                tools=[{"type": "retrieval"}],
                                model=modello_assistente,
                                file_ids=stored_file,
                            )
                        else:
                            my_assistant = client.beta.assistants.create(
                                instructions=prompt_sistema,
                                name=nome_assistente,
                                model=modello_assistente,
                            )

                        time.sleep(2)
                        status.update(label="Assistente creato con successo", state="complete")

                        st.success("Assistente creato con successo")
                        st.info("L'ID dell'assistente è: " + my_assistant.id)
                        st.error("Ricorda di salvare l'ID dell'assistente per utilizzarlo in seguito")
                        st.success("Per utilizzare l'assistente importato, copia l'ID e incollalo nella sezione 'Usa un Assistente'")


                    col3, col4 = st.columns(2)
                    #crea un bottone per scaricare un file.txt con l'ID dell'assistente
                    col3.download_button(
                        label="Scarica l'ID dell'assistente",
                        data="ID dell'assistente: " + my_assistant.id + "\nOpenAI API Key: " + openaiKey,
                        file_name="id_assistente_" + nome_assistente.replace(" ", "_") + ".txt",
                        mime="text/plain",
                    )

                    with st.spinner("Creo il file di configurazione dell'assistente..."):
                        time.sleep(2)
                        
                        #CREO IL FILE DI CONFIGURAZIONE YAML con i dati dell'assistente : Nome, Modello, Sistem_prompt
                        file_yaml = open("config_assistente.yaml", "w")
                        file_yaml.write("name: " + nome_assistente + "\n")
                        file_yaml.write("model: " + modello_assistente + "\n")
                        file_yaml.write("prompt: " + prompt_sistema + "\n")
                        file_yaml.close()

                        #CREO IL FILE ZIP
                        zip_file = zipfile.ZipFile("config_assistente.zip", "w")
                        zip_file.write("config_assistente.yaml")

                        if file_up:
                            for file in file_up:
                                with open(file.name, "rb") as f:
                                    zip_file.write(file.name)
                        zip_file.close()

                        #cambia estensione e nome del file nome_assistente.iaItaliaBotConfig e st.download_button
                        col4.download_button(
                            label="Scarica il file di configurazione dell'assistente",
                            data=open("config_assistente.zip", "rb"),
                            file_name=nome_assistente + ".iaItaliaBotConfig",
                            mime="application/zip",
                        )


                        st.balloons()


        else:
            file_up = st.file_uploader("Carica il file .iaItaliaBotConfig", type=['iaItaliaBotConfig'], accept_multiple_files=False)
            if file_up:
                if st.button("Crea Assistant Importato"):
                    client = openai.OpenAI()
                    my_assistant = create_assistant_from_config_file(file_up, client)

                    with st.status("Creazione assistente importato in corso...", expanded=True) as status:
                        time.sleep(2)
                        status.update(label="Assistente importato creato con successo", state="complete")

                        st.success("Assistente importato creato con successo")
                        st.info("L'ID dell'assistente importato è: " + my_assistant.id)
                        st.error("Ricorda di salvare l'ID dell'assistente per utilizzarlo in seguito")
                        st.success("Per utilizzare l'assistente importato, copia l'ID e incollalo nella sezione 'Usa un Assistente'")

                    st.download_button(
                        label="Scarica l'ID dell'assistente importato",
                        data="ID dell'assistente: " + my_assistant.id + "\nOpenAI API Key: " + openaiKey,
                        file_name="id_assistente.txt",
                        mime="text/plain",
                    )


    else:
        # Inferenza con Assistente

        id_assistente = st.text_input("Inserisci l'ID dell'assistente")

        if "msg_bot" not in st.session_state:
            st.session_state.msg_bot = []
            st.session_state.msg_bot.append("Ciao, sono il tuo assistente AI...")
            st.session_state.msg = []
            
            try :
                #create a thread
                thread = openai.beta.threads.create()
                my_thread_id = thread.id
            
                st.session_state.thread_id = my_thread_id
            except:
                st.error("C'è stato un problema con i Server di OpenAI")
                time.sleep(5)
                st.rerun()
                
            

        def get_response(domanda):
            #create a message
            if "thread_id" in st.session_state:
                try:
                    message = openai.beta.threads.messages.create(
                        thread_id=st.session_state.thread_id,
                        role="user",
                        content=domanda
                    )
                
                    #run
                    run = openai.beta.threads.runs.create(
                        thread_id=st.session_state.thread_id,
                        assistant_id=id_assistente,
                    )
                
                    return run.id
                except:
                    st.error("C'è stato un problema con i Server di OpenAI")

            time.sleep(5)
            st.rerun()

        def check_status(run_id):
            try: 
                run = openai.beta.threads.runs.retrieve(
                    thread_id=st.session_state.thread_id,
                    run_id=run_id,
                )
                return run.status
            except:
                st.error("C'è stato un problema con i Server di OpenAI")
                time.sleep(5)
                st.rerun()


        input = st.chat_input(placeholder="Scrivi quì il tuo problema legale...")

        if input:
            st.session_state.msg.append(input)
            with st.spinner("Sto pensando..."):
                run_id = get_response(input)
                status = check_status(run_id)
                
                while status != "completed":
                    status = check_status(run_id)
                    time.sleep(3)
                
                response = openai.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )

                if response.data:
                    print(response.data[0].content[0].text.value)
                    st.session_state.msg_bot.append(response.data[0].content[0].text.value) 
                else:
                    st.session_state.msg_bot.append("Non ho capito la domanda...")

        if "msg_bot" in st.session_state:
            bot_messages_count = len(st.session_state.msg_bot)
            for i in range(len(st.session_state.msg_bot)):
                with st.chat_message("ai"):
                    st.write(st.session_state.msg_bot[i])
                    if bot_messages_count == 10:
                        st.write("Attenzione, la conversazione sta diventando lunga. Potrei avere difficoltà a mantenere tutto in memoria. TI CONSIGLIO DI RICARICARE LA PAGINA ")
                    if bot_messages_count >= 12:
                        st.write("Attenzione, la conversazione sta diventando lunga. Potrei avere difficoltà a mantenere tutto in memoria. TI CONSIGLIO DI RICARICARE LA PAGINA ")
                
                if "msg" in st.session_state:
                    if i < len(st.session_state.msg):
                        if st.session_state.msg[i]:
                            with st.chat_message("user"):
                                st.write(st.session_state.msg[i])