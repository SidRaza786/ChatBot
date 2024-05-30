from flask import Flask, request, jsonify, render_template
import requests
import time
from data_preprocessing_unit import DataProcessor
from retrieval_generation import RAGSystemWithCOT
from data_ingestion import FaissVDB
import os




app = Flask(__name__, static_folder='static', template_folder='templates')

# Store the base_url globally
base_url_storage = {}

process_data = DataProcessor()
WordpressRAG = RAGSystemWithCOT()
Faiss_VDB = FaissVDB()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/CreateFAISSDatabase", methods=["POST"])
def CreateFAISSDatabase():

    """
    Request Body:
        {
            "base_url": "https://www.example.com"
        }
    """

    if request.method == 'POST':
        print(request)
        data = request.json
        if "base_url" not in data:
            return {"message": "base_url is not present."}, 400
    
        if data["base_url"] == "":
            return {"message": "base_url is not present."}, 400
        
        # check wordpress website wp/v2 support
        base_url = data["base_url"]
        # Store the base_url
        base_url_storage['base_url'] = base_url
        # response = requests.get(base_url)
        # response.raise_for_status()
        # link = response.links["alternate"]['url']
        # if "wp-json/wp/v2" not in link:
        #     return jsonify(message=f"Website does not support 'wp-json/wp/v2'"), 400
        
        print(f"Base url :- {base_url}, Type : {type(base_url)}")
        faiss_database_status = Faiss_VDB.Create_and_Update_FaissVDB(base_url)
        if faiss_database_status:
            return jsonify(message=f'Success: FAISS Vector Database has been created.')
        
    

@app.route("/Chat", methods=["GET", "POST"])
def Chat():
    """
    Request Body:
        {
            "base_url" : "http://localhost/wordpress",
            "message" : "user query"
        }
    """

    if request.method in ['POST', 'GET']:
        data = request.json
        if "base_url" not in data:
            return jsonify(message="base_url is not present")
        
        if "message" not in data:
            return jsonify(message="message is not present")
        
        print(f"Request for Chat : {data}")
        # base_url = data["base_url"]
        base_url = base_url_storage.get('base_url')
        user_query = data["message"]
        print(f"User Query:- {user_query}")
        start_time = time.time()
        retriever = Faiss_VDB.Create_and_Update_FaissVDB(base_url, "done")
        rag_chain = WordpressRAG.RAGResponseWithCOT(retriever)
        
        response_with_cot = rag_chain.invoke(user_query)
        end_time = time.time()
        response_time = end_time - start_time
        print(f"Response:- {response_with_cot} \n response_time: {response_time}")
        if response_with_cot != None:
            return jsonify(response=f"Response: {response_with_cot}", response_time=response_time)
        else:
            return jsonify(response=f"Response: I don't know", response_time=response_time)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5008, debug=True)



# from flask import Flask, request, jsonify, render_template
# import time
# from data_preprocessing_unit import DataProcessor
# from retrieval_generation import RAGSystemWithCOT
# from data_ingestion import FaissVDB

# app = Flask(__name__, static_folder='static', template_folder='templates')

# process_data = DataProcessor()
# WordpressRAG = RAGSystemWithCOT()
# Faiss_VDB = FaissVDB()

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/create_database")
# def create_database():
#     return render_template("create_database.html")

# @app.route("/CreateFAISSDatabase", methods=["POST"])
# def CreateFAISSDatabase():
#     if request.method == 'POST':
#         data = request.json
#         if "base_url" not in data or data["base_url"] == "":
#             return {"message": "base_url is not present."}, 400
#         base_url = data["base_url"]
#         print(f"Base url :- {base_url}")
#         faiss_database_status = Faiss_VDB.Create_and_Update_FaissVDB(base_url)
#         if faiss_database_status:
#             return jsonify(message='Success: FAISS Vector Database has been created.')

# @app.route("/Chat", methods=["POST"])
# def Chat():
#     if request.method == 'POST':
#         data = request.json
#         print(data)
#         if "base_url" not in data or "message" not in data:
#             return jsonify(message="base_url or message is not present")
#         base_url = data["base_url"]
#         user_query = data["message"]
#         print(f"User Query:- {base_url}")
#         start_time = time.time()
#         retriever = Faiss_VDB.Create_and_Update_FaissVDB(base_url, "done")
#         rag_chain = WordpressRAG.RAGResponseWithCOT(retriever)
#         response_with_cot = rag_chain.invoke(user_query)
#         end_time = time.time()
#         response_time = end_time - start_time
#         print(f"Response:- {response_with_cot} \n response_time: {response_time}")
#         return jsonify(response=response_with_cot or "I don't know", response_time=response_time)

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=5008, debug=True)
