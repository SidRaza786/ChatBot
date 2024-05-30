import os
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from langchain_google_genai import GoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate

from data_ingestion import FaissVDB

################# Google-Text-Bison ##################
GOOGLE_API_KEY = "AIzaSyAhy_sZ1HzJv6iZ2Ez7AFEW1_yjtcVVzas" 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
LLM = GoogleGenerativeAI(model="models/text-bison-001", google_api_key=GOOGLE_API_KEY)
##############################################################

# ########### Google-Gemini-Pro #################
# os.environ["GOOGLE_API_KEY"]
# LLM = ChatGoogleGenerativeAI(model="gemini-pro")
# ################################################


class RAGSystemWithCOT:
    def __init__(self):
        self.templete = """You are an assistant for question-answering tasks.
        Use the following pieces of retrieved context to answer the question.
        If you don't know the answer, just say that you don't know.
        Use ten sentences maximum and keep the answer concise.
        Question: {question}
        Context: {context}
        Answer:
        """
        self.obj_retriever = FaissVDB()

    def RAGResponseWithCOT(self, RAGRetriever) :
        output_parser=StrOutputParser()
        prompt=ChatPromptTemplate.from_template(self.templete)
        rag_chain_response = (
            {"context" : RAGRetriever, "question" : RunnablePassthrough()}
            | prompt
            | LLM
            | output_parser
        )

        return rag_chain_response









