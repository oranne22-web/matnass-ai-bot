Matnass AI Assistant

This project is an AI assistant for a community center.
The system allows users to ask questions about activities, classes, event and receive automatic responses.

The project uses:
Google Calendar as a data source
LangGraph for AI workflow management 
Streamlit as a chatbot interface 
Python

System Architecture:
Google Calendar -> Ingestion Pipeline -> Parser -> LangGraph AI Agent -> Streamlit Interface

AI Agent Features:
intent detection (sport/ youth/ workshops/ general)
activity filtering based on user query
structured parsing of event descriptions
real-time responses in hebrew

Example questions:
יש חוגי ספורט?
מה יש לנוער?
מה יש במתנ"ס?


Project Files:
ingest.py - reads data from Google Calendar
parser.py - parses event descriptions 
agent.py - AI agent logic using LangGraph
streamlit_code.py - chatbot user interface 

Link to the google calendar
https://calendar.google.com/calendar/u/0?cid=OWJhMjU5OWZjYmNmN2E1YzJmMWM2YTgzZWE3YTk0NDk4ZDJmODFkMTE4NWU0NDgwNmEyMjFjMjZlODNlNGRiN0Bncm91cC5jYWxlbmRhci5nb29nbGUuY29t

How to run the project:
 pip install -r requirements.txt
 python ingest.py
 streamlit run streamlit.py