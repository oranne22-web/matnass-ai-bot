from typing import TypedDict
from langgraph.graph import StateGraph
from ingest import get_activities

class AgentState(TypedDict):
    user_input: str
    result: str

def activity_agent(state: AgentState) -> AgentState:
    user_message = state["user_input"]

    activities = get_activities()

    results = []
    if "ספורט" in user_message:
        for activity in activities:
            if "ספורט" in activity.get("category", "") :
                results.append(activity.get("title"))
    elif "נוער" in user_message or "נערים" in user_message:
        for activity in activities:
            if "נערים" in activity.get("title", "") or "נוער" in activity.get("title", ""):
                results.append(activity.get("title"))
    elif "חוג עיון" in user_message or "סדנאות" in user_message or "סדנה" in user_message:
        for activity in activities:
            if "חוג עיון" in activity.get("category"):
                results.append(activity.get("title"))
    else:
        results.append("לא נמצאו פעילויות מתאימות")

    state["result"] = ", ".join(results)
    return state

graph = StateGraph(AgentState)
graph.add_node("activity_agent", activity_agent)
graph.set_entry_point("activity_agent")
graph.set_finish_point("activity_agent")
app = graph.compile()

