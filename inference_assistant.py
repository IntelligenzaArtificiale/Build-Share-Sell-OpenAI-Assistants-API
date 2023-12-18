import streamlit as st
import openai
import time

def inference(id_assistente):
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


    input = st.chat_input(placeholder="Scrivi quì la tua domanda...")

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