import os
from dotenv import load_dotenv, find_dotenv
from termcolor import colored
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
import requests
import json
load_dotenv(find_dotenv())

def get_chat_response(system_prompt, user_prompt, tool_planner=False):
    # By default, use the local LLM
    llm_type = os.environ.get('LLM_TYPE', "local")
    if llm_type == "local":
        return get_local_llm_response(system_prompt, user_prompt)
    else:
        return get_openai_response(system_prompt, user_prompt, tool_planner=tool_planner)


# def get_local_llm_response(system_prompt, user_prompt, model="ggml-gpt4all-j", temperature=0.9):
#     base_path = os.environ.get('OPENAI_API_BASE', 'http://localhost:8080/v1')
#     model_name = os.environ.get('MODEL_NAME', model)
#     llm = OpenAI(temperature=temperature, openai_api_base=base_path, model_name=model_name, openai_api_key="null")
#     text = system_prompt + "\n\n" + user_prompt + "\n\n"
#     response = llm(text)
#     print(response)
#     return response

def get_local_llm_response(system_prompt, user_prompt, model="llama2"):
    API_URL = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama2",
        "stream": False, 
        "messages": [
            {"role": "system", "content": system_prompt}, 
            {"role": "user", "content": user_prompt}
        ]
    }
    response = requests.post(API_URL, data=json.dumps(payload))
    print(response.text)
    return json.loads(response.text)["message"]["content"]

def extract_text_from_response(response_text):
    full_response = ''
    for line in response_text.splitlines():
        try:
            json_data = json.loads(line)
            full_response += json_data.get("response", "")
            if json_data.get("done"):
                break
        except json.JSONDecodeError:
            continue
    return full_response

def get_openai_response(system_prompt, user_prompt, model="gpt-4", temperature=0, tool_planner=False):
    chat = ChatOpenAI(model_name=model, temperature=temperature)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    response = chat(messages)
    print(response)
    return response.content
