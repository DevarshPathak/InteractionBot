from langchain.agents import AgentExecutor, create_react_agent, initialize_agent
from langchain import hub
from langchain.tools import Tool
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_core.messages import AIMessage, HumanMessage
from tools.cypher import cypher_qa
from tools.cypher import llm

agent_prompt = hub.pull("hwchase17/react-chat")
prompt_template = PromptTemplate.from_template("""
You are a drug-drug interaction checker expert.
Be as helpful as possible and return as much information as possible only about drugs.
Do not answer any questions that do not relate to drugs, interaction or risk and mechanism related to drug interaction.
You can also answer question related to size of database, number of nodes, number of drugs & interactions.
Do not answer any questions using your pre-trained knowledge, only use the information provided in the context.                                                                                                                             
    
TOOLS:
------

You have access to the following tools:

{tools}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes.
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
Output: A well defined sentence in bullet points

```
When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action                                
Final Answer: [your response here]
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
    Tool.from_function(
        name="Greeting",
        description="For greeting user and nothing more than that",
        func=greet_user,
        return_direct=True,
    ),
    Tool.from_function(
        name="Graph Cypher QA Chain",
        description="Provides information about drug-drug interactions, names of drugs, risk & mechanism associated with drug interaction", # (2)
        func = cypher_qa,
        return_direct=False
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
    handle_parsing_errors=True,
    # max_iterations=3,
    # cypher_prompt=cypher_prompt
    )

def generate_response(prompt):
    """
    Create a handler that calls the Conversational agent
    and returns a response to be renderinputed in the UI
    """
    try:
        response = agent_executor.invoke({
            "input": str(prompt),
            # Notice that chat_history is a string, since this prompt is aimed at LLMs, not chat models
            # "chat_history": "Human: Hi! My name is Bob\nAI: Hello Bob! Nice to meet you",
        })
        op=response['output']
        print("RESPONSE--------------->", response)
    
    except Exception as e:
        print(e)
        op = "Sorry, I couldn't understand your query at the moment. Could you please try again later?"
        
    return op