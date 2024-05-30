
import os
from langchain_community.vectorstores import FAISS # vector databases
from langchain.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from data_preprocessing_unit import DataProcessor


import warnings
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from sentence_transformers import SentenceTransformer

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub.file_download")
warnings.filterwarnings("ignore", category=UserWarning, message="Can't initialize NVML")
# Set the environment variable to disable tokenizers parallelism
os.environ["TOKENIZERS_PARALLELISM"] = "false"

############# Use Huggingface Sentence-BERT for embedding ##############
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
HUGGINGFACE_TOKEN = "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"
embedding = HuggingFaceInferenceAPIEmbeddings(
    api_key=HUGGINGFACE_TOKEN, model_name="sentence-transformers/all-MiniLM-l6-v2"
)

class FaissVDB:
    def __init__(self):
        self.obj_data = DataProcessor()

    def CreateDocuments(self, base_url):
        # base_url =  f"http://localhost/wordpress"
        data = self.obj_data.get_data(base_url)
        # create a document for faiss vector database
        documents = []
        for item in data:
            metadata = {
                "id": item["id"],
                "date": item["date"],
                "link" : item["link"],
                "chunk" : item["chunk"]
                        }
            doc = Document(page_content=item["chunk"], metadata=metadata)
            documents.append(doc)
        return documents
    

    def Create_and_Update_FaissVDB(self, base_url, status = None):
        documents = self.CreateDocuments(base_url)
        # create FAISS Vector Database
        FaissVectorStore = FAISS.from_documents(documents, embedding)
        retriever = FaissVectorStore.as_retriever()
        # save Faiss Vector Database
        # save_directory = "faiss_vector_store"
        # FaissVectorStore.save_local(save_directory)
        storage = status
        if storage == None:
            return True #, save_directory
        else:
            return retriever


    
     






