import sqlite3
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from .state import AgentState
from .prompts import SYSTEM_PROMPT, REPLAN_PROMPT, RESPONSE_PROMPT, get_schema_string


load_dotenv() 
llm = ChatOpenAI(model='gpt-4o-mini', temperature=0,max_tokens=300)
DB_PATH = 'inventory_chatbot.db'


def sql_generator_node(state: AgentState) -> dict:
    question = state["question"]
    messages = state.get("messages", [])

    intent_messages = [
        SystemMessage(content=(
            "You are an intent classifier for an inventory chatbot.\n"
            "Reply with exactly one word:\n"
            "  'chitchat'   greetings, small-talk, or anything unrelated to inventory\n"
            "  'db_query'   questions about assets, vendors, locations, orders, bills, stock"
        )),
        HumanMessage(content=question)
    ]
    intent = llm.invoke(intent_messages).content.strip().lower()

    if "chitchat" in intent:
        chitchat_messages = [
            SystemMessage(content=(
                "You are a friendly inventory management assistant"
                "Respond naturally and briefly, then offer to help with inventory questions"
            )),
            HumanMessage(content=question)
        ]
        reply = llm.invoke(chitchat_messages).content.strip()
        return {
            "intent":         "chitchat",
            "sql_query":      None,
            "sql_result":     reply,         
            "error":          None,
            "revision_count": 0,
            "messages":       messages + [HumanMessage(content=question), AIMessage(content=reply)]
        }

    schema = get_schema_string()
    generation_messages = [
        SystemMessage(content=SYSTEM_PROMPT.format(schema=schema)),
        HumanMessage(content=question)
    ]
    sql = llm.invoke(generation_messages).content.strip()
    if sql.startswith("```"):
        sql = "\n".join(
            line for line in sql.splitlines()
            if not line.strip().startswith("```")
        ).strip()

    return {
        "intent":         "db_query",
        "sql_query":      sql,
        "sql_result":     None,
        "error":          None,
        "revision_count": 0,
        "messages":       messages + [HumanMessage(content=question)]
    }



def sql_executor_node(state: AgentState) -> dict:
    if state.get("intent") == "chitchat" or state.get("sql_query") is None:
        return {}

    sql = state["sql_query"]

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row          
        cursor  = conn.cursor()
        cursor.execute(sql)
        rows   = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.close()

        return {
            "sql_result":     result,
            "error":          None,
        }

    except Exception as exc:
        return {
            "sql_result":     None,
            "error":          str(exc),
            "revision_count": state.get("revision_count", 0) + 1
        }


def sql_corrector_node(state: AgentState) -> dict:
    schema       = get_schema_string()
    broken_sql   = state["sql_query"]
    error_msg    = state["error"]
    question     = state["question"]

    correction_messages = [
        SystemMessage(content=REPLAN_PROMPT.format(schema=schema)),
        HumanMessage(content=(
            f"Original question : {question}\n"
            f"Broken SQL        :\n{broken_sql}\n"
            f"Error message     : {error_msg}\n\n"
            "Return ONLY the corrected SQL query, nothing else."
        ))
    ]
    corrected_sql = llm.invoke(correction_messages).content.strip()
    if corrected_sql.startswith("```"):
        corrected_sql = "\n".join(
            line for line in corrected_sql.splitlines()
            if not line.strip().startswith("```")
        ).strip()

    return {
        "sql_query": corrected_sql,
        "error":     None           
    }


def responder_node(state: AgentState) -> dict:
    question   = state["question"]
    sql_result = state.get("sql_result")
    error      = state.get("error")
    messages   = state.get("messages", [])

    if state.get("intent") == "chitchat":
        final_response = sql_result
        print(f"\nBot: {final_response}\n")
        return {"messages": messages + [AIMessage(content=final_response)]}

    if error:
        final_response = (
            f"I'm sorry, I wasn't able to retrieve that information. "
            f"Technical detail: {error}"
        )
        print(f"\nBot: {final_response}\n")
        return {"messages": messages + [AIMessage(content=final_response)]}

    if not sql_result:
        final_response = "I found no records matching your query. Could you rephrase or be more specific?"
        print(f"\nBot: {final_response}\n")
        return {"messages": messages + [AIMessage(content=final_response)]}


    response_messages = [
        SystemMessage(content=RESPONSE_PROMPT),
        HumanMessage(content=(
            f"User question : {question}\n"
            f"Database rows : {sql_result}\n\n"
            "Answer in clear, friendly natural language. "
            "Be concise but complete. If there are many rows, summarise."
        ))
    ]
    final_response = llm.invoke(response_messages).content.strip()

    print(f"\nBot: {final_response}\n")
    return {
        "sql_result": sql_result,
        "messages":   messages + [AIMessage(content=final_response)]
    }