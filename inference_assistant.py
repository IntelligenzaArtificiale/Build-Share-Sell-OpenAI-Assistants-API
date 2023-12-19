# THis file contains the code for the inference of the assistant
# Path: inference_assistant.py

import streamlit as st
import openai
import time
from utils import export_chat

def inference(id_assistente):
    if "msg_bot" not in st.session_state:
        st.session_state.msg_bot = []
        st.session_state.msg_bot.append("Hi🤗, I'm your assistant. How can I help you?")
        st.session_state.msg = []
        
        try :
            #create a thread
            thread = openai.beta.threads.create()
            my_thread_id = thread.id
        
            st.session_state.thread_id = my_thread_id
        except:
            st.error("🛑 There was a problem with OpenAI Servers")
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
                st.error("🛑 There was a problem with OpenAI Servers")

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
            st.error("🛑 There was a problem with OpenAI Servers")
            time.sleep(5)
            st.rerun()


    input = st.chat_input(placeholder="🖊 Write a message...")

    if input:
        st.session_state.msg.append(input)
        with st.spinner("🤖 Thinking..."):
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
                st.session_state.msg_bot.append("😫 Sorry, I didn't understand. Can you rephrase?")

    if "msg_bot" in st.session_state:
        bot_messages_count = len(st.session_state.msg_bot)
        for i in range(len(st.session_state.msg_bot)):
            with st.chat_message("ai"):
                st.write(st.session_state.msg_bot[i])
                
                
            if "msg" in st.session_state:
                if i < len(st.session_state.msg):
                    if st.session_state.msg[i]:
                        with st.chat_message("user"):
                            st.write(st.session_state.msg[i])

    if "msg_bot" in st.session_state:
        if len(st.session_state.msg) > 0 :
            export_chat()