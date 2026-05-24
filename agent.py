from typing import TypedDict
from langgraph.graph import StateGraph
from ingest import get_activities

class AgentState(TypedDict, total=False):
    user_input: str
    intent: str
    result: str

def detect_intent(state: AgentState) -> AgentState:
    text = state["user_input"]
    if "ספורט" in text:
        state["intent"] = "sport"
    elif "נוער" in text:
        state["intent"] = "youth"
    elif "סדנה" in text:
        state["intent"] = "workshop"
    else:
        state["intent"] = "other"

    return state

def fetch_activities(state: AgentState) -> AgentState:
    activities = get_activities()
    intent = state.get("intent", "other")
    results = []

    if intent == "sport":
        results = [
            a.get("title")
            for a in activities
            if "ספורט" in a.get("category", "")
        ]
    elif intent == "youth":
        results = [
            a.get("title")
            for a in activities
            if "נוער" in a.get("title", "")
        ]
    elif intent == "workshop":
        results = [
            a.get("title")
            for a in activities
            if "חוג עיון" in a.get("category", "")
        ]
    else:
        results = [
            a.get("title")
            for a in activities
        ]
    unique_results = list(set(results))
    if not unique_results:
        state["result"] = "לא נמצאו פעילויות מתאימות"
    else:
        state["result"] = "להלן הפעילויות שנמצאו:\n\n- " + "\n- ".join(unique_results)

    return state




graph = StateGraph(AgentState)
graph.add_node("detect_intent", detect_intent)
graph.add_node("fetch_activities", fetch_activities)

graph.set_entry_point("detect_intent")
graph.add_edge("detect_intent", "fetch_activities")
graph.set_finish_point("fetch_activities")
app = graph.compile()

