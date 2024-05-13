from langchain.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_groq import ChatGroq
from langchain_community.graphs import Neo4jGraph

graph = Neo4jGraph(
    url="neo4j+s://e89ec291.databases.neo4j.io", username="neo4j", password="5qfTZ43ehzbUa-FOuK_mgX1iLTkHBV_QCKS5IZMqNB8"
)
api_key = None
with open('<GROQ_KEY>', 'r') as f:
    api_key = f.read().strip()
llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="llama3-70b-8192")

cypher_qa = GraphCypherQAChain.from_llm(
    llm,    
    graph=graph,
    top_k = 40,
    chain_type="refine"
)
