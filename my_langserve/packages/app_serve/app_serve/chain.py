from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

import os



# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")


# _prompt = ChatPromptTemplate.from_messages(
#     [
#         (
#             "system",
#             "You are a helpful assistant who speaks like a pirate",
#         ),
#         ("human", "{text}"),
#     ]
# )
# _model = ChatOpenAI(model="gpt-3.5-turbo-1106", temperature=0.1, openai_api_key=OPENAI_API_KEY) #gpt-4-1106-preview

# # if you update this, you MUST also update ../pyproject.toml
# # with the new `tool.langserve.export_attr`
# chain = _prompt | _model
