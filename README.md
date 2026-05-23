Matnass AI Assistant

This project is an AI assistant for a community center.
The system allows users to ask questions about activities, classes, envent and receive automatic responses.

The project uses:
Google Calendar as a data source
LangGraph for AI workflow management 
Streamlit as a chatbot interface 

System Architecture:
Google Calendar -> Ingestion Pipeline -> Parser -> LangGraph AI Agent -> Streamlit Interface

Project Files:
ingest.py - reads data from Google Calendar
parser.py - parses event descriptions 
agent.py - AI agent logic using LangGraph
streamlit.py - chatbot user interface 

How to run the project:
run ingestion pipeline- 
 python ingest.py
run streamlit chatbot
 streamlit run streamlit.py