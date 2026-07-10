from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langgraph.graph import MessagesState, StateGraph, END
from typing import List, Union, Optional
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
import os
from langgraph.types import Command
from langchain.messages import HumanMessage, AIMessage
from langchain_core.tools import create_retriever_tool
from langgraph.prebuilt import ToolNode
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import json
from fastapi.responses import StreamingResponse
from uuid import uuid4
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

load_dotenv()

memory=MemorySaver()

current_dir=os.getcwd()
persistant_dir=os.path.join(current_dir,"database","Chroma_db")

embedding=GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
    )
index_name = os.getenv("PINECONE_INDEX_NAME")

db= PineconeVectorStore(
    index_name=index_name, 
    embedding=embedding
)

retriver=db.as_retriever(search_type='mmr',
                search_kwargs={
                    "k":3,
                    "fetch_k":10,
                    "lambda_multi":0.5
                })

retriver_tool=create_retriever_tool(
    retriever=retriver,
    name="retriver",
    description="Retrives the infromation from the documents"
)

tools=[retriver_tool]

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
llm_with_tool=llm.bind_tools(tools=tools)

off_topic_prompt=ChatPromptTemplate([
    ("system","You are a chatbot, specifically Mizhavu Chatbot which is an educational chatbot. "
    "You were created to educate people about the endangered Mizhavu instrument. "
    "You are the agent who responds to questions the user asks, that are unrelated to the purpose "
    "of the chat bot. \n"
    "Your duty is to manage this type of situation with appropriate response. "
    "If the user asks something about you do respond. \n"),
    MessagesPlaceholder(variable_name="messages"),
    ("system","You'r name is Mizhavu Ashan. 'Ashan' is a malayalam word meaning 'master'"
    "Your duty is to talk friendly to the user based on the chat history")
])

rephrase_prompt=ChatPromptTemplate([
    ("system","You are a question rephraser, You do not answer the question. Your only duty is to rephrase the question entered by the uses into a "
    "meaningful stand alone question, preserving its meaning and context. \n"
    "Based on the given chat history reframe the the given user query into a stand alone question.\n"
    "CHAT HISTORY:"),
    MessagesPlaceholder(variable_name="messages"),
    ('system',"Your only duty is to rephrase the question entered by the uses into a meaningful stand alone question, preserving its meaning and context.")
])

bouncer_llm_prompt=ChatPromptTemplate([
    ("system","You are a decision maker AI assistant for a chatbot. The chatbot is called Mizhavu Chatbot. Your duty is to identify if the users question is "
    "about one of the following topics. \n\n"
    "1. Kudiyattam Theatre and the Mizhavu Drum\n"
    ""
    "If the users question is about one of this topic respond with 'Yes' otherwise repond 'No'."),
    MessagesPlaceholder(variable_name="messages")
])

answer_generator_llm_prompt=ChatPromptTemplate([
    ("system","You are a chatbot, specifically Mizhavu Chatbot which is an educational chatbot. "
    "You were created to educate people about the endangered Mizhavu instrument. "
    "Your duty is to provide answer to the user query by "
    "calling tools to retrive information from the your knowledge base and by analyzing the chat "
    "history."),
    MessagesPlaceholder(variable_name="messages"),
    ("system","Do not use tools if the users question can be answered using the chat history. " \
    "If the information is not sufficient use tools to " \
    "retrive necessary infomation")
])

class AgentState(MessagesState):
    on_topic:Union[str,None]

rephrase_chain=rephrase_prompt | llm
answer_generator_chain=answer_generator_llm_prompt | llm_with_tool
bouncer_chain=bouncer_llm_prompt | llm
off_topic_chain=off_topic_prompt | llm


async def rephrase_node(state:MessagesState):

    if len(state["messages"])==1:

        rephrased_question=state["messages"][-1]
    
    else:

        rephrased_question=await rephrase_chain.ainvoke(state)
        rephrased_question=rephrased_question

    return {"messages":rephrased_question}

async def bouncer_node(state:AgentState):
    decision=bouncer_chain.invoke(state)
    decision=decision.content.lower()
    if "yes" in decision:
        return Command(
            goto="answer_generator",
            update={"on_topic":"Yes"}
        )
    else:
        return Command(
            goto="off_topic_node",
            update={"on_topic":"No"}
        )
    
async def generate_answer_node(state:AgentState):
    answer= await answer_generator_chain.ainvoke(state)
    return {"messages":answer}

async def router_node(state:AgentState):
    last_message=state["messages"][-1]
    if isinstance(last_message,AIMessage) and hasattr(last_message,"tool_calls") and len(last_message.tool_calls)>0:
        return "tools"
    else:
        return END
    
async def off_topic_node(state:AgentState):
    # print("ENTERED")
    result=await off_topic_chain.ainvoke(state)
    return Command(
        goto=END,
        update={
            "messages":result
        }
    )

async def answer_agent_node(state:MessagesState):
    graph_input={
        "messages": [HumanMessage(content=state["messages"][-1].content)],
        "on_topic":None
    }

    graph_result = await answer_agent.ainvoke(graph_input)
    return {"messages": graph_result['messages'][-1]}


graph = StateGraph(MessagesState)
graph.add_node("rephraser", rephrase_node)
graph.add_node("answer_generator",answer_agent_node)

graph.set_entry_point("rephraser")
graph.add_edge("rephraser","answer_generator")

rephrase_agent = graph.compile(checkpointer=memory)



tool_node = ToolNode(tools)

subgraph=StateGraph(AgentState)
subgraph.add_node("bouncer",bouncer_node)
subgraph.add_node("answer_generator",generate_answer_node)

subgraph.add_node("off_topic_node",off_topic_node)
subgraph.add_node("tools",tool_node)

subgraph.add_edge("tools", "answer_generator")
subgraph.add_conditional_edges(
    "answer_generator",
    router_node,
)
subgraph.set_entry_point("bouncer")

answer_agent=subgraph.compile()

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
out_dir = os.path.join(BASE_DIR, "client", "out")
next_assets_dir = os.path.join(out_dir, "_next")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], 
    expose_headers=["Content-Type"], 
)


async def generate_respose(message:str,checkpoint_id:Optional[str]=None):
    if not checkpoint_id:
        new_checkpoint_id=str(uuid4())

        config={
            "configurable":{
                "thread_id":new_checkpoint_id
            }
        }

        events=rephrase_agent.astream_events({
            "messages":[HumanMessage(content=message)]
        },version="v2",config=config)

        yield f"data: {{\"type\": \"checkpoint\", \"checkpoint_id\": \"{new_checkpoint_id}\"}}\n\n"
    
    else:
        config={
            "configurable":{
                "thread_id":checkpoint_id
            }
        }

        events=rephrase_agent.astream_events({
            "messages":[HumanMessage(content=message)]
        },version="v2",config=config)
    

    async for event in events:
        event_type=event["event"]
        
        if event_type=="on_chat_model_stream":
            node_name = event.get("metadata", {}).get("langgraph_node")

            if node_name == "answer_generator" or node_name == "off_topic_node":
                content = event["data"]["chunk"].content
                if isinstance(content, list) and len(content) > 0:
                    content = content[0]["text"]

                if content:
                    safe_content = content.replace('"', '\\"').replace("\n", "\\n")
                    yield f"data: {{\"type\":\"content\",\"content\":\"{safe_content}\"}}\n\n"

            # content=event["data"]["chunk"].content
            # if isinstance(content,list)and len(content)>0:
            #     content=content[0]["text"]

            # if content:
            #     safe_content=content.replace('"','\\"').replace("\n","\\n")
            #     yield f"data: {{\"type\":\"content\",\"content\":\"{safe_content}\"}}\n\n"

        elif event_type=="on_chat_model_end":
            if hasattr(event["data"]["output"],"tool_calls"):
                # print("**********************************")
                tool_calls=event["data"]["output"].tool_calls
            else:
                tool_calls=[]
            
            search_calls = [call for call in tool_calls if call["name"] == "retriver"]

            if search_calls:
                # print("**********************************")
                search_query = search_calls[0]["args"].get("query", "")
                safe_query = search_query.replace('"', '\\"').replace("'", "\\'").replace("\n", "\\n")
                yield f"data: {{\"type\":\"search_start\",\"query\":\"{safe_query}\"}}\n\n"        


        elif event_type=="on_tool_end":
            output = event["data"]["output"].content
            
            try:
                output = json.loads(output)
                print(output)
                if isinstance(output, list):
                    for out in output:
                        url = [item["url"] for item in out if isinstance(item, dict) and "url" in item['results']]
                        urls_json = json.dumps(url)
                        yield f"data: {{\"type\": \"search_results\", \"urls\": {urls_json}}}\n\n"
                else:
                    url = [item['url'] for item in output['results'] if isinstance(item, dict) and "url" in item]
                    urls_json = json.dumps(url)
                    yield f"data: {{\"type\": \"search_results\", \"urls\": {urls_json}}}\n\n"
            except json.JSONDecodeError:
                pass


        print(f"{event}\n\n\n")
    yield f"data: {{\"type\": \"end\"}}\n\n"

@app.get("/chat/{message}", include_in_schema=True)
async def chat_stream(message: str, checkpoint_id: Optional[str] = Query(None)):
    return StreamingResponse(
        generate_respose(message, checkpoint_id), 
        media_type="text/event-stream"
    )

FRONTEND_BUILD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "client", "out"))

@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):

    file_path = os.path.join(FRONTEND_BUILD_DIR, full_path)
    

    if os.path.isfile(file_path):
        return FileResponse(file_path)
    

    index_path = os.path.join(FRONTEND_BUILD_DIR, "index.html")
    return FileResponse(index_path)