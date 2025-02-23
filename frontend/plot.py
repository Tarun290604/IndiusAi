from smolagents import CodeAgent, LiteLLMModel
import os
from dotenv import load_dotenv

load_dotenv()

def generate_plot(data_info, file_name, chart_type, x_axis, y_axis):
    # Initialize Gemini model
    model = LiteLLMModel(
        model_id="gemini/gemini-2.0-flash",
        api_key=os.getenv("GEMINI_API_KEY")
    )

    # Create CodeAgent with necessary permissions
    agent = CodeAgent(
        tools=[],
        model=model,
        additional_authorized_imports=["pandas", "plotly.express", "plotly.graph_objects"]
    )

    # Define the query to generate the plot
    query = f"""
    Consider this dataset: {data_info}
    Create a function named generate_plot() that:
    1. Reads data from 'files/{file_name}'
    2. Creates a Plotly {chart_type} with {x_axis} on x-axis and {y_axis} on y-axis
    3. The plot should be visually appealing for dark background
    4. Returns the fig object
    """

    # Generate and execute the code
    fig = agent.run(query)

    return fig
