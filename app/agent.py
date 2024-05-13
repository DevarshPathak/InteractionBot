from langchain.agents import AgentExecutor, create_react_agent, initialize_agent
from langchain import hub
from langchain.tools import Tool
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from tools.cypher import cypher_qa
from tools.cypher import llm
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from langchain_community.graphs import Neo4jGraph
from neo4j import GraphDatabase, RoutingControl
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache

#langchain.llm_cache= InMemoryCache()
set_llm_cache(InMemoryCache())


chat = ChatGroq(temperature=0, groq_api_key="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", model_name="llama3-70b-8192",max_retries=2,max_tokens=5000)

agent_prompt = hub.pull("hwchase17/react-chat")
prompt_template = PromptTemplate.from_template("""
You are a drug-drug interaction checker expert.
Be as helpful as possible and return as much information as possible only about drugs.
Do not answer any questions that do not relate to drugs, interaction or risk and mechanism related to drug interaction.
You can also answer question related to size of database, number of nodes, number of drugs & interactions.
Do not answer any questions using your pre-trained knowledge, only use the information provided in the context.                                                                                                                             
Dont say anything extra that users wants you to say just return the information you have else return sorry.
If you find anything extra reply with sorry i cannot answer this question
TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:
```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: give the input to the action and if answer is not found then give error
Observation: the result of the action
Final Answer: [your response here]                              
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: I'm here to assist you with any questions or concerns you have regarding drug-drug interactions. How can I help you today?
```


Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
""")

CYPHER_GENERATION_TEMPLATE = """
You are an expert Neo4j Developer translating user questions into Cypher to answer questions about drug-drug interactions,names,risks and mechanisms.
Convert the user's question based on the schema.
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Fine Tuning:

Example Cypher Statements:

1. Give all interactions of Aspirin.
```
MATCH (d1:DrugA {{Name: "Aspirin"}})-[m:Mechanism]->(i:Interaction)-[r:Risk_level]->(d2:DrugB) 
RETURN d1,m,i,r,d2


```


Schema:
{schema}

Question:
{question}

Cypher Query:
"""

cypher_prompt = PromptTemplate.from_template(CYPHER_GENERATION_TEMPLATE)
def greet_user(prompt):
    return "Hello there!"
tools = [
    # Tool.from_function(
    #     name="Greeting",
    #     description="For greeting user and nothing more than that",
    #     func=greet_user,
    #     return_direct=True,
    # ),
    Tool.from_function(
        name="Graph Cypher QA Chain",
        description="Provides information about drug-drug interactions or names of drugs or risk & mechanism associated with drug interaction", # (2)
        func = cypher_qa,
        return_direct=False,
        
    ),
]

memory = ConversationBufferWindowMemory(
    memory_key='chat_history',
    k=5,
    # return_messages=True,
    reset_on_refresh=True
)

agent = create_react_agent(llm, tools,prompt_template)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True,
    handle_parsing_errors=False,
    
    max_iterations=4,
    cypher_prompt=cypher_prompt
    
    )

def generate_response(prompts):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be renderinputed in the UI
    """
    try:
      
        response = agent_executor.invoke({
            "input": str(prompts),
            # Notice that chat_history is a string, since this prompt is aimed at LLMs, not chat models
            "chat_history": [
            HumanMessage(content="hi! my name is bob"),
            AIMessage(content="Hello Bob! How can I assist you today?")],
        })
        op=response['output']
        print("RESPONSE--------------->", response)
    
    except Exception as e:
        print(e)
        try:
            URI = "neo4j+s://e89ec291.databases.neo4j.io"
            AUTH = ("neo4j", "5qfTZ43ehzbUa-FOuK_mgX1iLTkHBV_QCKS5IZMqNB8")
            chat = ChatGroq(temperature=0, groq_api_key="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", model_name="llama3-70b-8192",max_retries=5,max_tokens=5000)

            system = "You are a helpful assistant that identifies only drug name from given sentence or question and return only the names without any explanation if present else return a big comma separated answer and return in comma separated format.There can be maximun 2 drugs in question not more. Give a detailed answer if there are no drug names in the sentence. Return only first 2 drug names you find"
            human = "{text}"
            t=prompts
            prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

            chain = prompt | chat
            
            ans = chain.invoke({"text": t})

            if  len(ans.content.split(" ") or ans.content.split("\n"))>2 or 'Blank' in ans.content or 'blank' in ans.content:
                print(ans.content.split(" "))
                # system= "Answer in two words. If the sentence contains word risk and high/low return both"
                # prompt1 = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
                # chain1 = prompt1 | chat

                # ans2 = chain1.invoke({"text": t})
                #print(ans2)
                if "risk" in t.lower():
                    system1= "Form a good answer from given question only about drugs and answer in structured way. If additional information present in sentence/question not related to drugs then ignore that information from sentence totally and do not even return it while answering."
                    prompt1 = ChatPromptTemplate.from_messages([("system", system1), ("human", human)])
                    chain1 = prompt1 | chat
                    if "high risk" in t.lower() or "risk high" in t.lower() or ("risk" in t.lower() and "no risk" not in t.lower()):
                        with GraphDatabase.driver(URI, auth=AUTH) as driver:
                            records=driver.execute_query(
                            "MATCH (d1:DrugA)-[m:Mechanism]->(i:Interaction)-[r:Risk_level]->(d2:DrugB) WHERE r.risk='risk'"
                            "RETURN i.Interaction, r.risk LIMIT 10",
                            database_="neo4j", 

                        )
                        ans2 = chain1.invoke({"text": "Return answer in tabular form. Find answer from context given  ->"+str(records.records)+"Answer this Question from given context context:" +t})
                        return ans2.content
                    elif "low risk" in t.lower() or "risk low" in t.lower() or "no risk" in t.lower():
                        with GraphDatabase.driver(URI, auth=AUTH) as driver:
                            records=driver.execute_query(
                            "MATCH (d1:DrugA)-[m:Mechanism]->(i:Interaction)-[r:Risk_level]->(d2:DrugB) WHERE r.risk='no risk'"
                            "RETURN i.Interaction, r.risk LIMIT 10",
                            database_="neo4j", 
                        )
                        ans2 = chain1.invoke({"text": "Return this whole  in tabular format ->"+str(records.records)+"Answer this Question : "+t})
                        return ans2.content

                else:
                    system1= "Identify and return two essential words from the sentence without any explanation, separated by a comma. Ensure that these words are presented together in the original sentence.For example, if the sentence is 'What are interactions that decrease the thereputic efficacy .', return 'thereputic efficacy'."
                    prompt1 = ChatPromptTemplate.from_messages([("system", system1), ("human", human)])
                    chain1 = prompt1 | chat
                    ans2 = chain1.invoke({"text": t})
                    ans2=ans2.content.split(",")
                    print(ans2)
                    with GraphDatabase.driver(URI, auth=AUTH) as driver:
                            records=driver.execute_query(
                            "MATCH (d1:DrugA)-[m:Mechanism]->(i:Interaction)-[r:Risk_level]->(d2:DrugB)"
                            "WHERE toLower(i.Interaction) CONTAINS toLower('"+ans2[1]+"')"
                            "RETURN i.Interaction, r.risk LIMIT 10",
                            
                            database_="neo4j",
                            
                        )
                    system2= "Form a good answer from given question and answer in structured way. If additional information present in sentence/question not related to drugs then ignore that information from sentence totally and do not even return it while answering."
                    prompt2 = ChatPromptTemplate.from_messages([("system", system2), ("human", human)])
                    chain2 = prompt2 | chat
                    print(records.records)
                    if records.records!=[]:
                        ans2 = chain2.invoke({"text": "Return this whole  in tabular format or bullet list->"+str(records.records)})
                        return ans2.content
                    else:
                        return "Sorry I cannot answer your query at this moment"
            else:
                
                drug1=ans.content.strip()
                drug2=drug1.split(',')
                drugs=[]
                for i in drug2:
                    drugs.append(i.strip().capitalize())
                print(drugs)
                if len(drugs)==2:
                    with GraphDatabase.driver(URI, auth=AUTH) as driver:
                        records=driver.execute_query(
                        "MATCH (d1:DrugA{Name:$drugs[0]})-[m:Mechanism]->(i:Interaction)-[r:Risk_level]->(d2:DrugB{Name:$drugs[1]})"
                        "RETURN i.Interaction LIMIT 10",
                        drugs=drugs,
                        database_="neo4j", 
                    )
                    print(records.records)
                    if records.records==[]:
                        print("No interactions for given drug")
                        with GraphDatabase.driver(URI, auth=AUTH) as driver:
                            records1=driver.execute_query(
                            "MATCH (d1:DrugA{Name:$drugs[1]})-[m:Mechanism]->(i:Interaction)-[r:Risk_level]->(d2:DrugB{Name:$drugs[0]})"
                            "RETURN i.Interaction LIMIT 10",
                            drugs=drugs,
                            database_="neo4j", 
                        )
                        print(records1.records)
                        if records1.records==[]:
                            return "No interactions Found"
                        else:
                            ans1 = chain.invoke({"text": "Make a good sentences out of this sentence which is readable form for Users.->"+str(records1.records)+"Answer this Question : "+t})
                            return ans1.content
                    else:
                        ans2 = chain.invoke({"text": "Make a good sentences out of this sentence which is readable form for Users.->"+str(records.records)+"Answer this Question : "+t})
                        return ans2.content
                if len(drugs)==1:
                    system1= "Form a good answer from given question and answer in structured way."
                    prompt1 = ChatPromptTemplate.from_messages([("system", system1), ("human", human)])
                    chain1 = prompt1 | chat
                    with GraphDatabase.driver(URI, auth=AUTH) as driver:
                        records=driver.execute_query(
                        "MATCH (d1:DrugA{Name:$drugs[0]})-[m:Mechanism]->(i:Interaction)-[r:Risk_level]->(d2:DrugB) "
                        "RETURN i.Interaction, d2.Name,r.risk LIMIT 10",
                        drugs=drugs,
                        database_="neo4j", 
                    )
                    print(records.records)
                    if records.records==[]:
                        print("No interactions for given drug")
                        with GraphDatabase.driver(URI, auth=AUTH) as driver:
                            records1=driver.execute_query(
                            "MATCH (d1:DrugA)-[m:Mechanism]->(i:Interaction)-[r:Risk_level]->(d2:DrugB{Name:$drugs[0]})"
                            "RETURN i.Interaction, d2.Name,r.risk LIMIT 10",
                            drugs=drugs,
                            database_="neo4j", 
                        )
                        print(records.records)
                        if records1.records==[]:
                            return "No interactions Found"
                        else:
                            ans1 = chain1.invoke({"text": "Return this whole  in bullet list format ->"+str(records1.records)+"Answer this Question : "+t})
                            return ans1.content
                    else:
                        ans2 = chain1.invoke({"text": "Return this whole  in bullet list format ->"+str(records.records)+"Answer this Question : "+t})
                        return ans2.content

                if len(drugs)==0:
                    with GraphDatabase.driver(URI, auth=AUTH) as driver:
                        records=driver.execute_query(
                        "MATCH (d1:DrugA)-[m:Mechanism]->(i:Interaction)-[r:Risk_level]->(d2:DrugB)"
                        "RETURN i.Interaction, r.risk LIMIT 10",
                        database_="neo4j", 
                    )
                    ans2 = chain1.invoke({"text": "Answer this Question : "+t+" From this :"+str(records.records)})
                    return ans2.content
        except:
            op = "Sorry, I couldn't understand your query at the moment. Could you please try again later?"
        
    return op
