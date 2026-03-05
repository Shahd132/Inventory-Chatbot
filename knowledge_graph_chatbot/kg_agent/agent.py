import os
import json
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI
from kg_agent.state import KGAgentState
from kg_agent.tools import Neo4jTool
from kg_agent.prompts import (
    INTENT_PROMPT, ENTITY_PROMPT, CYPHER_PROMPT,
    RESPONSE_PROMPT, CHITCHAT_PROMPT
)

load_dotenv()
llm = OpenAI(model="gpt-4o-mini", temperature=0, max_tokens=300)
db   = Neo4jTool()
MAX_RETRIES = 2

def _call_llm(prompt: str)->str:
    response=llm.complete(prompt)
    return response.text.strip()

def classify_intent(state: KGAgentState)->KGAgentState:
    prompt=INTENT_PROMPT.format(user_input=state["user_input"])
    intent=_call_llm(prompt).lower().strip()
    valid={"add","inquire","edit","delete","chitchat"}
    intent=intent if intent in valid else "inquire"
    return {**state,"intent":intent}

def handle_chitchat(state:KGAgentState) -> KGAgentState:
    prompt   = CHITCHAT_PROMPT.format(user_input=state["user_input"])
    response = _call_llm(prompt)
    return {**state,"final_response":response}

def extract_entities(state:KGAgentState)->KGAgentState:
    prompt=ENTITY_PROMPT.format(user_input=state["user_input"])
    raw=_call_llm(prompt)

    if raw.startswith("```"):
        raw = "\n".join(
            line for line in raw.splitlines()
            if not line.strip().startswith("```")
        ).strip()
    try:
        entities = json.loads(raw)
    except json.JSONDecodeError:
        entities = {"raw": raw}

    return {**state,"entities":entities}

def get_existing_schema() -> str:
    try:
        labels = db.run_query("CALL db.labels() YIELD label RETURN label")
        rel_types = db.run_query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
        nodes = db.run_query("MATCH (n) RETURN DISTINCT labels(n) AS labels, n.name AS name LIMIT 50")

        label_list = [r['label'] for r in labels]
        rel_list   = [r['relationshipType'] for r in rel_types]
        node_list  = [f"{r['name']} {r['labels']}" for r in nodes if r['name']]

        return f"""
            Existing relationship types  : {rel_list}
            Existing node labels in graph: {label_list}
            Existing nodes               : {node_list}
            """
    except:
        return "No existing schema found."

def generate_cypher(state:KGAgentState)->KGAgentState:
    schema = get_existing_schema()
    
    prompt = CYPHER_PROMPT.format(
        intent=state["intent"],
        entities=json.dumps(state["entities"], indent=2),
        schema=schema   
    )
    cypher=_call_llm(prompt)

    if cypher.startswith("```"):
        cypher = "\n".join(
            line for line in cypher.splitlines()
            if not line.strip().startswith("```")
        ).strip()

    return {**state,"cypher_query":cypher,"error":None}

def execute_cypher(state: KGAgentState)->KGAgentState:
    try:
        result=db.run_query(state["cypher_query"])
        return {**state, "db_result": result, "error": None}
    except Exception as e:
        return {
            **state,
            "db_result": None,
            "error": str(e)
        }


def correct_cypher(state: KGAgentState) -> KGAgentState:
    correction_prompt = f"""
    You are a Neo4j Cypher expert. Fix the following broken Cypher query.
    Original intent : {state['intent']}
    Entities        : {json.dumps(state['entities'], indent=2)}
    Broken query    : {state['cypher_query']}
    Error message   : {state['error']}

    Return ONLY the corrected raw Cypher query, no explanation, no markdown.
    """
    corrected = _call_llm(correction_prompt)

    if corrected.startswith("```"):
        corrected = "\n".join(
            line for line in corrected.splitlines()
            if not line.strip().startswith("```")
        ).strip()

    return {**state,"cypher_query":corrected,"error":None}

def synthesize_response(state: KGAgentState)->KGAgentState:
    if state.get("error"):
        response = (
            f"I'm sorry, I couldn't complete that action. "
            f"Technical detail: {state['error']}"
        )
        return {**state, "final_response": response}

    prompt = RESPONSE_PROMPT.format(
        user_input=state["user_input"],
        intent=state["intent"],
        db_result=state["db_result"]
    )
    response = _call_llm(prompt)
    return {**state,"final_response":response}

def run_agent(user_input:str,history: list)->tuple[str, list]:
    state: KGAgentState = {
        "user_input":     user_input,
        "intent":         None,
        "entities":       None,
        "cypher_query":   None,
        "db_result":      None,
        "error":          None,
        "final_response": None,
        "history":        history
    }

    state = classify_intent(state)

    if state["intent"] == "chitchat":
        state = handle_chitchat(state)
        history.append({"role": "user","content": user_input})
        history.append({"role": "assistant","content": state["final_response"]})
        return state["final_response"], history

    state = extract_entities(state)
    state = generate_cypher(state)
    for attempt in range(MAX_RETRIES):
        state = execute_cypher(state)
        if not state.get("error"):
            break
        if attempt < MAX_RETRIES - 1:
            state = correct_cypher(state)

    state = synthesize_response(state)
    history.append({"role": "user",      "content": user_input})
    history.append({"role": "assistant", "content": state["final_response"]})

    return state["final_response"], history