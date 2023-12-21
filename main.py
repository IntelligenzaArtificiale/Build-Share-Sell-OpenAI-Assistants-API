import openai
import streamlit as st
import time
import os
import zipfile
import yaml
 
from inference_assistant import inference
from utils import create_assistant_from_config_file, upload_to_openai, export_assistant

st.set_page_config(
    page_title="Build, Share and Sell OpenAI Assistants API",
    page_icon="🤖",
    layout="wide",
    menu_items={
        'Get Help': 'mailto:servizi@intelligenzaartificialeitalia.net',
        'Report a bug': "https://github.com/IntelligenzaArtificiale/Build-Share-Sell-OpenAI-Assistants-API/issues",
        'About': "# This is a simple web app to build, share and sell OpenAI Assistants API\n\n"
    }
)

st.title("Build🚧, Share🤗 and Sell💸 OpenAI Assistants🤖")


utilizzo = st.selectbox("🤖 Hi, what do you want to do?", ("Create or Import an Assistant", "Use an Assistant"))

if utilizzo != "Use an Assistant":
    scelta_creazione = st.selectbox(
        '💻 Do you want to create an assistant from scratch or import an assistant?',
        ('Create an Assistant from Scratch', 'Import an Assistant from .iaItaliaBotConfig'),
        index=0
    )

openaiKey = st.text_input("🔑 Pls insert your OpenAI API Key")
if openaiKey:
    os.environ["OPENAI_API_KEY"] = openaiKey
    openai.api_key = openaiKey
    client = openai.OpenAI()

    if utilizzo == "Create or Import an Assistant":
        if scelta_creazione == "Create an Assistant from Scratch":
            col1, col2 = st.columns(2)

            with col1:
                nome_assistente = st.text_input("👶 Insert the name of the assistant")

            with col2:
                modello_assistente = st.selectbox(
                    '🛒 Choose the model of the assistant',
                    ('gpt-4-1106-preview', 'gpt-4'),
                    index=0
                )

            if nome_assistente and modello_assistente:
                prompt_sistema = st.text_area("📄 Write the instructions for the assistant")

                carica_file = st.checkbox("📚 Do you want to upload files for knowledge?")

                stored_file = []
                if carica_file:
                    file_up = st.file_uploader("📚 Upload File", type=['.c', '.cpp', '.ipynb', '.docx', '.html', '.java', '.json', '.md', '.pdf', '.php', '.pptx', '.py', '.py', '.rb', '.tex', '.txt'], accept_multiple_files=True)
                    if file_up:
                        if len(file_up) > 20:
                            st.error("🛑 You can upload a maximum of 20 files")
                            st.stop()
                        st.info("HEY, Remember to click on the button 'Upload File' to upload the files to OpenAI")
                        if st.button("📩 Upload File"):
                            with st.status("📡 Upload File on OpenAI Server...", expanded=True) as status:
                                for file in file_up:
                                    time.sleep(2)
                                    status.update(label="🛰 Upload File: " + file.name)
                                    with open(file.name, "wb") as f:
                                        f.write(file.getbuffer())
                                    additional_file_id = upload_to_openai(file)
                                    if additional_file_id:
                                        st.write("File uploaded successfully: " + file.name + " with ID: " + additional_file_id)
                                        stored_file.append(additional_file_id)
                                st.write("👌 Files uploaded successfully: " + str(len(stored_file)))
                                if 'id_file' not in st.session_state:
                                    st.session_state.id_file = []
                                st.session_state.id_file = stored_file
                                status.update(label="Files uploaded successfully", state="complete", expanded=False)

                if st.button("🤖 Build Assistant") and prompt_sistema:
                    with st.status("⏲ Assistant creation in progress...", expanded=True) as status:
                        time.sleep(2)
                        status.update(label="🧐 Configuring the assistant...", state="running")
                        time.sleep(2)
                        if "id_file" in st.session_state and len(st.session_state.id_file) > 0:
                            status.update(label="📡 Create Assistant with File and Retrieval...", state="running")
                            my_assistant = client.beta.assistants.create(
                                instructions=prompt_sistema,
                                name=nome_assistente,
                                tools=[{"type": "retrieval"}],
                                model=modello_assistente,
                                file_ids=st.session_state.id_file,
                            )
                            st.write("👌 Assistant created successfully with File and Retrieval")
                        else:
                            
                            my_assistant = client.beta.assistants.create(
                                instructions=prompt_sistema,
                                name=nome_assistente,
                                model=modello_assistente,
                            )
                            status.update(label="👌 Assistant created successfully", state="complete", expanded=False)


                        time.sleep(1)

                        st.success("✅ Assistant created successfully")
                        st.info("🆗 ID of the assistant: " + my_assistant.id)
                        st.error("⛔ Remember to save the ID of the assistant to use it later")
                        cola, colb = st.columns(2)
                        cola.info("📥 To use the assistant, copy the ID and paste it in the 'Use an Assistant' section")
                        colb.info("📤 To share the assistant, download Assistant Configuration File and send it")


                    col3, col4 = st.columns(2)
                    #crea un bottone per scaricare un file.txt con l'ID dell'assistente
                    col3.download_button(
                        label="🗂 Download ID Assistant",
                        data="ASSISTANT ID : " + my_assistant.id + "\nOpenAI API Key: " + openaiKey,
                        file_name="id_ASSISTANT_" + nome_assistente.replace(" ", "_") + ".txt",
                        mime="text/plain",
                    )

                    with st.spinner("📥 Building Assistant Configuration File..."):
                        data_to_export = export_assistant(nome_assistente, modello_assistente, prompt_sistema, file_up)
                        
                        col4.download_button(
                            label="🗂 Download Assistant Configuration File",
                            data=data_to_export,
                            file_name=nome_assistente + ".iaItaliaBotConfig",
                            mime="application/zip",
                        )

                    
                    st.balloons()


        else:
            file_up = st.file_uploader("📥 Upload .iaItaliaBotConfig", type=['iaItaliaBotConfig'], accept_multiple_files=False)
            if file_up:
                if st.button("🤖 Build imported Assistant"):
                    client = openai.OpenAI()
                    

                    with st.status("⏲ Assistant creation in progress...", expanded=True) as status:
                        time.sleep(0.5)
                        status.update(label="Estrazione e caricamento file in corso...", state="running")
                        time.sleep(0.5)
                        my_assistant = create_assistant_from_config_file(file_up, client)
                        status.update(label="Assistente importato creato con successo", state="complete")

                        st.success("✅ Assistant created successfully")
                        st.info("🆗 ID of the assistant: " + my_assistant.id)
                        st.error("⛔ Remember to save the ID of the assistant to use it later")
                        cola, colb = st.columns(2)
                        cola.info("📥 To use the assistant, copy the ID and paste it in the 'Use an Assistant' section")
                        colb.info("📤 To share the assistant, download Assistant Configuration File and send it")

                    st.download_button(
                        label="🗂 Download ID Assistant",
                        data="ASSISTANT ID : " + my_assistant.id + "\nOpenAI API Key: " + openaiKey,
                        file_name="id_ASSISTANT.txt",
                        mime="text/plain",
                    )
        


    else:
        # Inferenza con Assistente

        id_assistente = st.text_input("🆔 Insert the ID of the assistant")

        if id_assistente:
            try: 
                inference(id_assistente)
            except Exception as e:
                st.error("🛑 There was a problem with OpenAI Servers")
                st.error(e)
                if st.button("🔄 Restart"):
                    st.rerun()

html_chat = '<center><h6>🤗 Support the project with a donation for the development of new features 🤗</h6>'
html_chat += '<br><a href="https://rebrand.ly/SupportAUTOGPTfree"><img src="https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif" alt="PayPal donate button" /></a><center><br>'
st.markdown(html_chat, unsafe_allow_html=True)
st.write('Made with ❤️ by [Alessandro CIciarelli](https://intelligenzaartificialeitalia.net)')
