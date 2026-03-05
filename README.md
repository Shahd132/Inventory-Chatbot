1. Project Overview
This project consists of two AI agents:
    1. Inventory Chatbot (SQL)
    2. Knowledge Graph Agent (Neo4j)
both built using LanGgraph, LlamaIndex and OpenAI


2. Prerequisites
1. Neo4j Desktop or AuraDB account.
2. SQLite 
3. An OpenAI API Key.
4. Instruction to run pip install -r requirements.txt


3. Inventory Chatbot
it is a chatbot sends a message to the llm and gets a response
1st classify the intent of the user (chitchat or DB query).
2nd generate SQL if the intent was DB query.
3rd execute the SQL query.
4th if the query has an error the agent will try to fix it at most 2 times.
5th if there is no error the agent will return a response.

I used LanGgraph since it solve 2 main requirements
first one Conditional Routing after each node runs, a routing function reads the state and decides which node to go to next executor -> corrector or executor -> responder.
second one Self-Correction Loop "if the SQL fails, fix it and try again automatically" corrector-> executor .



4. Knowledge Graph Chatbot
1st understand what the user wants to do (add, search, edit, delete or chitchat).
2nd extract the entities from the sentence (who, what,relationship).
3rd generate a Cypher query that operates on Neo4j.
4th execute it and handle failures.
5th explain the result in natural language.

I used LlamaIndex provides a clean, minimal interface to call OpenAI models without boilerplate. Instead of manually constructing API requests



5. Run these commands to run the chatbot
Inventory Chatbot:
1. cd inventory_chatbot   
2. python setup_database.py
3. python main.py

Knowledge Graph Chatbot:
1. cd knowledge_graph_chatbot 
2. python main.py
