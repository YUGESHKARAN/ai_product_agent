import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from mongodb_database import MongoDBDatabase
from langchain_groq import ChatGroq
import os



from langsmith import evaluate, Client
load_dotenv()

# Set API keys
os.environ['GROQ_API_KEY'] = os.getenv('GROQ_API_KEY')
os.environ['MONGODB_URI'] = os.getenv('MONGODB_URI')


app = Flask(__name__)

CORS(app)

db = MongoDBDatabase("mongodb+srv://yugeshkaran01:GEMBkFW5Ny5wi4ox@blog.adtwl.mongodb.net/JWT-AUTH?retryWrites=true&w=majority&appName=User","JWT-AUTH")

chat_history = []

def mogodb_query_generator(db):
    template = """
    You are a agent of a product website. You are interacting with a user who is asking you to do various actions on the database.
    Based on the collection schema below, write a MongoDB query that would answer the user's question. Take the Conversation History into account.

    NOTE:
    - You are only allowed to use the database collection of the specified user who has the email {email}.
    - For update and insert operations, extract the necessary values from the question.

    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}

    Write only the MongoDB query and nothing else. Do not wrap the query in any other text, not even backticks.

    Gerneral example:

    For example:
    Question: Show all the products ?
    MongoDB Query: collection.find({{"email": {email}}}, {{"productDetails": 1, "_id": 0}})

    Question: total number of products?
    MongoDB Query: collection.aggregate([{{"$match": {{"email": {email}}}}}, {{"$project": {{"numberOfProducts": {{"$size": "$productDetails"}}}}}}])

    Question: price of product Laptop?
    MongoDB Query: collection.find({{"email": {email}, "productDetails.product": "Laptop"}}, {{"productDetails.$": 1, "_id": 0}})

    Question: Change the price of the product Laptop to 200000
    MongoDB Query: collection.updateOne({{"email": {email}, "productDetails.product": "Laptop"}}, {{"$set": {{"productDetails.$.price": 200000}}}})

    Question: Add new product SSD, price 10000, warranty March 10, 2027
    MongoDB Query: collection.updateOne({{"email": "{email}"}}, {{"$push": {{"productDetails": {{ "product": "SSD", "price": 10000, "waranty": "2027-03-10"}}}}}})

    Question: Delete the product 'Smart Watch'
    MongoDB Query: collection.updateOne({{ "email": {email}}},{{ "$pull": {{ "productDetails": {{ "product": "Smart Watch" }}}}}})

    Question: Show the expensive product.
    MongoDB Query: collection.aggregate([{{ "$match": {{ "email": {email}}} }},
    {{ "$unwind": "$productDetails" }},
    {{ "$sort": {{ "productDetails.price": -1 }} }},
    {{ "$limit": 1 }},
    {{ "$project": {{
        "_id": 0,
        "product": "$productDetails.product",
        "price": "$productDetails.price",
        "waranty": "$productDetails.waranty",
        "image": "$productDetails.image"
    }} }}
   ])

   Question: Product with the highest warranty.
   MongoDB Query: collection.aggregate([
    {{ "$match": {{ "email": "{email}" }} }},
    {{ "$unwind": "$productDetails" }},
    {{ "$sort": {{ "productDetails.waranty": 1 }} }},
    {{ "$limit": 1 }},
    {{ "$project": {{
        "_id": 0,
        "product": "$productDetails.product",
        "price": "$productDetails.price",
        "waranty": "$productDetails.waranty",
        "image": "$productDetails.image"
    }} }}
  ])

 Question: Update the image of Shoe to red color shoe
 MongoDB Query: collection.updateOne(
  {{ "email": {email}, "productDetails.product": "Shoe" }},
  {{ "$set": {{ "productDetails.$.image": "red color shoe"}}}}
)
  
    Note:

    - Make sure to do update operation or insert operation only on productDetails field.
    - For adding new product only to productDetails array.
    - Do not use any other field except productDetails and email.
    - Follow all the above instruction and look the example Question and MongoDB Query before performing actions.


    Your turn:
    Question: {question}
    MongoDB Query: 
    """

    prompt = ChatPromptTemplate.from_template(template).partial(email="{email}")
    llm = ChatGroq(model_name="llama3-70b-8192")
    # llm = ChatGroq(model_name="llama-3.3-70b-versatile")


    return (
        RunnablePassthrough.assign(
            schema=lambda _: db.get_collection_schema('users')
        )
        | prompt
        | llm
        | StrOutputParser()
    )


def response_generator(user_query: str, db: MongoDBDatabase,email: str, chat_history: list):
    # Generate the MongoDB query using the query generator
    mongo_chain = mogodb_query_generator(db)
    template = """
    You are a agent for a Product website. You are interacting with a user who is asking you questions about the User database to generate content, add new products, statistics measure or required infromation from the database based on user query.
    Based on the collection schema below, use question, MongoDB query, and MongoDB response, write a natural language response with pre-size and compete the action. 
    note:
    1. Generate the content as per the conversation history and MongoDB response.
    2. Make sure to format the response as paragraph.
    4. Try to as pre-size by avoiding adding other stuffs like document query structure.
    5. Do not genearte the response more than 40 words.

    <SCHEMA>{schema}</SCHEMA>

    Conversation History: {chat_history}
    MongoDB Query: <QUERY>{query}</QUERY>
    User Question: {question}
    User email: {email}
    MongoDB Response: {response}

    If the MongoDB response is not empty, confirm the existence of the product details.
    """


    llm = ChatGroq(model_name="llama3-70b-8192")
    # llm = ChatGroq(model_name="llama-3.3-70b-versatile")

    # Create the prompt with the template
    prompt = ChatPromptTemplate.from_template(template)

    # Define the chain
    chain = (
        RunnablePassthrough.assign(query= lambda _:  mongo_chain)  # Ensure query is passed correctly
        .assign(
                schema=lambda _: db.get_collection_schema('users'),
                response=lambda var: db.run('users', var['query'].replace("{email}", f'"{var["email"]}"'))
                
        )

        | prompt
        | llm
        | StrOutputParser()
    )

    # Execute the chain and return the result
    return chain.invoke({"question": user_query, "email": email, "chat_history": chat_history})


@app.route("/")
def welcome_blog_backend():
    return "Welcome to Product Agent"

@app.route("/query-agent",methods=['POST'])
def query_MongoDB_RAG():
    
    data = request.json
    user_query = data.get("query","")
    user_email = data.get("email","")
    if user_query:
        chat_history.append(HumanMessage(content=user_query))

        response = response_generator(user_query, db,user_email, chat_history)
        print(f"Query: {user_query}")
        print(f"Response: {response}")

        # if response:
        #     chat_history.append(AIMessage(content=response))
        # return jsonify({"response":response})

        if response:
            # Remove leading sentence if it exists
            prefix1 = "Here is the natural language response:"
            prefix2 = "Here is the natural language response with pre-size and compete the action:"
            
            if response.startswith(prefix2):
                response = response[len(prefix2):].strip()
            elif response.startswith(prefix1):
                response = response[len(prefix1):].strip()

            chat_history.append(AIMessage(content=response))

        return jsonify({"response": response})


if __name__ == "__main__":
    app.run(port=4000, host="0.0.0.0", debug=False)

