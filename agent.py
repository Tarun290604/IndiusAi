from smolagents import CodeAgent, LiteLLMModel
import pandas as pd
import json, os
import plotly.graph_objs as go
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

def response_code(question, file_name, data_info):
    model = LiteLLMModel(
        model_id="gemini/gemini-2.0-flash",
        api_key=os.getenv("GEMINI_API_KEY")
    )

    agent = CodeAgent(
        tools=[],
        model=model,
        additional_authorized_imports=["pandas"]
    )

    query = f"""
    Consider this dataset example: {data_info}
    Create a Python script that does the following steps:
    1. Read the CSV file located at 'files/{file_name}' using pandas and store it in a variable called 'df'.
    2. Analyze the data to answer the user's question: "{question}".
    3. Return the answers for the above question as string not json.
    """

    try:
        result = agent.run(query)
        return result
    except Exception as e:
        return e

def response_fig(question, file_name, data_info):
    model = LiteLLMModel(
        model_id="gemini/gemini-2.0-flash",
        api_key=os.getenv("GEMINI_API_KEY")
    )

    agent = CodeAgent(
        tools=[],
        model=model,
        additional_authorized_imports=["pandas", "plotly.express", "plotly.graph_objects", "json"]
    )

    # Improved query with stricter instructions
    query = f"""
    Consider this dataset example: {data_info}
    Create a Python script that does the following steps:
    1. Read the CSV file located at 'files/{file_name}' using pandas and store it in a variable called 'df'.
    2. Analyze the data to answer the user's question: "{question}".
    3. Create a Plotly graph using plotly.graph_objects (go.Figure) to visualize the answer.
    4. Ensure the plot is visually appealing for a dark background:
       - Use a dark template (e.g., 'plotly_dark').
       - Use distinct, bright colors for data elements (e.g., '#00CC96', '#EF553B', '#FFA15A').
    5. Explicitly assign the figure to a variable named 'fig' and ensure it is a plotly.graph_objs.Figure object.
    6. Return only the 'fig' object at the end of the script (do not print or return anything else).
    """

    try:
        result = agent.run(query)

        # Stricter validation
        if isinstance(result, go.Figure):
            return result
        else:
            error_msg = f"Generated result is not a Plotly Figure: got {type(result)} instead"
            return None

    except Exception as e:
        error_msg = f"Code execution failed: {str(e)}"
        return None

def response_code_run(hypothesis, file_name, data_info):
    model = LiteLLMModel(
        model_id="gemini/gemini-2.0-flash",
        api_key=os.getenv("GEMINI_API_KEY")
    )

    agent = CodeAgent(
        tools=[],
        model=model,
        additional_authorized_imports=["pandas", "numpy", "sklearn", "math", "statistics"]
    )

    query = f"""
    Consider this dataset example: {data_info}
    Create a Python script that does the following steps:
    1. Read the CSV file located at 'files/{file_name}' using pandas.
    2. Analyze the data to answer user's hypothesis: {hypothesis}.
    3. Return the result of the hypothesis with the statistical test you used as a string.
    4. Ensure the returned result has the used statistical test being run to test the hypothesis, followed by the key results (e.g., p-value, coefficients, etc.).
    """

    try:
        result = agent.run(query)
        return result
    except Exception as e:
        return e
