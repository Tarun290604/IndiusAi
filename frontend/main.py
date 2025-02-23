import streamlit as st
import os
import pandas as pd
import ast
import json
from plot import generate_plot
from backend.agent import response_fig, response_code, response_code_run
from backend.model import get_response
import plotly.graph_objs as go

# Page config
st.set_page_config("Indius Ai", layout="wide")

# Add logo
st.logo("logo.png")

def files_exist():
    """Check if files exist in the 'files' folder."""
    if not os.path.exists("files"):
        os.makedirs("files")
    return bool(os.listdir("files") if os.path.exists("files") else False)

def load_data(file_path):
    """Load data from a file."""
    if file_path.endswith("csv"):
        return pd.read_csv(file_path)
    else:
        return pd.read_excel(file_path)

def display_data_summary(df):
    """Display a summary of the dataset."""
    st.subheader("📊 Detailed Summary Report")

    # Section 1: Basic Information
    st.markdown("### 📄 Basic Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Number of Rows", df.shape[0])
    with col2:
        st.metric("Number of Columns", df.shape[1])
    with col3:
        st.metric("Total Cells", df.size)

    st.markdown("**Column Names:**")
    st.write(", ".join(df.columns))

    # Section 2: Data Types
    st.markdown("### 🧾 Data Types")
    st.write(df.dtypes.to_frame(name="Data Type"))

    # Section 3: Missing Values
    st.markdown("### 🚨 Missing Values")
    missing_values = df.isnull().sum()
    if missing_values.sum() > 0:
        st.warning("Your dataset contains missing values. Consider handling them for better analysis.")
        st.write(missing_values[missing_values > 0].to_frame(name="Missing Values"))
    else:
        st.success("No missing values found in the dataset! 🎉")

    # Section 4: Unique Values
    st.markdown("### 🔍 Unique Values per Column")
    unique_values = df.nunique()
    st.write(unique_values.to_frame(name="Unique Values"))

    # Section 5: Descriptive Statistics
    st.markdown("### 📈 Descriptive Statistics")
    with st.expander("View Descriptive Statistics"):
        st.write(df.describe(include='all'))

    # Section 6: Data Cleanliness Assessment
    st.markdown("### 🧹 Data Cleanliness Assessment")
    total_cells = df.size
    missing_cells = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    cleanliness_score = ((total_cells - missing_cells) / total_cells) * 100

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Missing Cells", missing_cells)
        st.metric("Duplicate Rows", duplicate_rows)
    with col2:
        st.metric("Cleanliness Score", f"{cleanliness_score:.2f}%")
        st.progress(cleanliness_score / 100)

    if missing_cells > 0:
        st.warning("⚠️ Your dataset contains missing values. Consider handling them for better analysis.")
    if duplicate_rows > 0:
        st.warning("⚠️ Your dataset contains duplicate rows. Consider removing them for better analysis.")

    # Section 7: Sample Data
    st.markdown("### 📋 Sample Data")
    with st.expander("View Sample Data"):
        st.write(df.head())

def handle_hypothesis_testing(df, selected_file, dataset_head, dataset_info):
    """Handle hypothesis testing and guide me functionality."""
    st.subheader("Welcome to Hypothesis Testing!")
    st.write("""
    Explore patterns, relationships, or differences in the dataset. \n
    Have a hypothesis? Ask here! \n
    Don’t worry—we’ll handle the math! \n
    """)

    with st.expander("View Dataset Information"):
        st.text("Dataset Info:")
        st.write(df.head())

    hypothesis = st.text_input("Enter your hypothesis:", placeholder="e.g., Is there a relationship between X and Y?")
    run_hypothesis = st.button("Run Hypothesis!")
    guide_me = st.button("Guide Me!")

    # Handle hypothesis testing
    if run_hypothesis:
        if not hypothesis.strip():
            st.warning("Please enter a hypothesis before running.")
        else:
            with st.spinner("Testing your hypothesis..."):
                try:
                    # Get results from the agent
                    results = response_code_run(hypothesis, selected_file, dataset_head)
                    st.success("Hypothesis test completed!")

                    # Generate an explanation of the results
                    prompt = f"""
                    The following are the results from a statistical test run on the dataset with columns {list(df.columns)} and data info {dataset_info} to test the hypothesis '{hypothesis}'.
                    Test results:\n{results}
                    Your output should have only one point talking about whether the hypothesis is true or false and why.
                    NOTE: The output should not have any other text other than what is required.
                    """
                    explanation = get_response(prompt)
                    st.subheader("Explanation:")
                    st.write(explanation)
                except Exception as e:
                    st.error(f"An error occurred while testing the hypothesis: {e}")

    # Handle "Guide Me" button
    if guide_me:
        with st.spinner("Generating suggestions..."):
            try:
                # Generate hypotheses or analysis suggestions
                prompt = f"""
                Given the following dataset information and sample data, suggest 3 hypotheses or statistical analyses that could provide insights into the data.
                The user has no background in statistics or coding, so include a simple explanation for each suggestion.

                Sample data:\n{dataset_head}

                List the suggestions in a numbered format, e.g., '1. [Hypothesis/Analysis] - [Simple explanation with suitable statistical tests]'.
                NOTE: Your output should not contain any text other than the numbered hypothesis and explanation.
                """
                suggestions = get_response(prompt).strip().split("\n")
                st.subheader("Suggested Hypotheses/Analyses:")
                for suggestion in suggestions:
                    st.write(suggestion)
            except Exception as e:
                st.error(f"An error occurred while generating suggestions: {e}")

# Sidebar for file upload
with st.sidebar:
    st.subheader("Files", divider="gray")
    upload_files = st.file_uploader("", accept_multiple_files=True, type=["csv", "xlsx"])

    if upload_files:
        for upload_file in upload_files:
            bytes_data = upload_file.getvalue()
            filename = upload_file.name
            with open(f"files/{filename}", mode="wb") as w:
                w.write(bytes_data)

# Main content
if files_exist():
    # File selection
    files = os.listdir("files")
    selected_file = st.selectbox("Select a file to analyze", files)

    if selected_file:
        # Navigation tabs
        tab1, tab2, tab3, tab4 = st.tabs(["Table", "Plots", "Summary", "Hypothesis"])

        with tab1:
            # Load data
            with st.spinner("Loading data..."):
                df = load_data(f"files/{selected_file}")
                st.write(df.head())
                data_info = df.head()

            # Generate and cache questions
            if ('stored_file' not in st.session_state or
                st.session_state.stored_file != selected_file):
                with st.spinner("Generating questions..."):
                    query = f"""
                    Consider this dataset: {data_info}
                    Give me three interesting questions from this dataset.
                    Return the output as a list [question1, question2, question3] without backticks.
                    """
                    questions = get_response(query).strip()
                    questions = ast.literal_eval(questions)
                    st.session_state.questions = questions
                    st.session_state.stored_file = selected_file

            questions = st.session_state.questions
            question1, question2, question3 = questions
            st.text("Suggested Questions: ")

            # Display question buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                question_element1 = st.button(question1)
            with col2:
                question_element2 = st.button(question2)
            with col3:
                question_element3 = st.button(question3)

            if question_element1:
                with st.spinner("Generating response..."):
                    resp_fig = response_fig(question1, selected_file, data_info)
                    resp_code = response_code(question1, selected_file, data_info)
                    st.write(resp_code)
                    if isinstance(resp_fig, go.Figure):
                        st.plotly_chart(resp_fig)
                    else:
                        st.error(f"Error generating visualization...")

            if question_element2:
                with st.spinner("Generating response..."):
                    resp_fig = response_fig(question2, selected_file, data_info)
                    resp_code = response_code(question2, selected_file, data_info)
                    st.write(resp_code)
                    if isinstance(resp_fig, go.Figure):
                        st.plotly_chart(resp_fig)
                    else:
                        st.error(f"Error generating visualization...")

            if question_element3:
                with st.spinner("Generating response..."):
                    resp_fig = response_fig(question3, selected_file, data_info)
                    resp_code = response_code(question3, selected_file, data_info)
                    st.write(resp_code)
                    if isinstance(resp_fig, go.Figure):
                        st.plotly_chart(resp_fig)
                    else:
                        st.error(f"Error generating visualization...")

            # Query container with button-driven interaction
            with st.container(border=True):
                st.write(f"File name: {selected_file}")
                query = st.text_input("", placeholder="Ask anything...", key="tab1_input")
                ask_button = st.button("Ask", key="ask_button")

                if ask_button and query:
                    with st.spinner("Generating response..."):
                        resp_fig = response_fig(query, selected_file, data_info)
                        resp_code = response_code(query, selected_file, data_info)
                        st.write(resp_code)
                        if isinstance(resp_fig, go.Figure):
                            st.plotly_chart(resp_fig)
                        else:
                            st.error(f"Error generating visualization...")

        with tab2:
            # Load data
            with st.spinner("Loading data..."):
                df = load_data(f"files/{selected_file}")
                st.write(df.head())

            # Plot controls
            plot_type = st.selectbox(
                "Plot Type",
                ("Scatter Plot", "Line Chart", "Bar Chart", "Histogram",
                 "Box Plot", "Violin Plot", "Heatmap", "Contour Plot",
                 "3D Scatter Plot", "3D Surface Plot"),
                key="plot_type"
            )

            columns = df.columns.tolist()
            X_axis = st.selectbox("X-Axis", columns, key="x_axis")
            Y_axis = st.selectbox("Y-Axis", columns, key="y_axis")

            if st.button("Plot", key="plot_button"):
                with st.spinner("Generating plot..."):
                    st.plotly_chart(generate_plot(df.head(), selected_file, plot_type, X_axis, Y_axis))

        with tab3:
            with st.spinner("Loading data..."):
                df = load_data(f"files/{selected_file}")
                display_data_summary(df)

        with tab4:
            with st.spinner("Loading data..."):
                df = load_data(f"files/{selected_file}")
                dataset_head = df.head()
                dataset_info = df.info()
                handle_hypothesis_testing(df, selected_file, dataset_head, dataset_info)

else:
    with st.container(border=True):
        st.subheader("Add a dataset...!!!")
