import openai
import streamlit as st
import time


st.title("Assistant BUILDER")


openaiKey = st.input("Inserisci la tua API Key di OpenAI")


if openaiKey:

    try: 
        openai.api_key = openaiKey

        col1, col2 = st.columns(2)

        with col1:
            nome_assistente = st.text_input("Nome dell'assistente")

        with col2:
            modello_assistente = st.selectbox("gpt-4-1106-preview")

        if nome_assistente and modello_assistente:

            prompt_sistema = st.text_area("Prompt del sistema", height=200)

        stored_file = None

        if st.checkbox("Vuoi caricare File ? "):
            file = st.file_uploader("Carica il file", type=["txt, pdf"], accept_multiple_files = True)

            if file:
                stored_file = file






        if stored_file is not None:
            file_id = []
            for file in stored_file:
                try:
                    my_file =
                    client.files.create(
                    file=open(file, "rb"),
                    purpose="assistants"
                    )
                    file_id = file_id.append(my_file.id)
                    print(my_file.id)
                except:
                    print("file non caricato")



            my_assistant = client.beta.assistants.create(
                instructions=prompt_sistema,
                name=nome_assistente,
                tools=[{"type": "retrieval"}],
                model=modello_assistente,
                file_ids=file_id
            )
            st.write(my_assistant)
            st.success("Assistente creato con successo")
            st.info("L'id dell'assistente è: " + my_assistant.id)

        else:
            my_assistant = client.beta.assistants.create(
                instructions=prompt_sistema,
                name=nome_assistente,
                model=modello_assistente,
            )
            print(my_assistant)

    
    except:
        st.error("API Key non valida")