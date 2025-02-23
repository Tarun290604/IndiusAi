from smolagents import CodeAgent, LiteLLMModel
import pandas as pd
import json
import plotly.graph_objs as go
import streamlit as st  # Assuming you're using Streamlit

def response_code(question, file_name, data_info):
    model = LiteLLMModel(
        model_id="together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo",
    #    api_base="https://api.together.xyz/v1",
        api_key="87c346e5ef2b9263ffb1777069b0b5ac0b85778631522cbac6272b08da62f506"
    )
    model.flatten_messages_as_text=True

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
    3. Return the code to run the above question.
    """

    try:
        result = agent.run(query)
        return result
    except Exception as e:
        return e

def response_fig(question, file_name, data_info):
    model = LiteLLMModel(
        model_id="together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo",
    #    api_base="https://api.together.xyz/v1",
        api_key="87c346e5ef2b9263ffb1777069b0b5ac0b85778631522cbac6272b08da62f506",
    )
    model.flatten_messages_as_text = True

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

def
