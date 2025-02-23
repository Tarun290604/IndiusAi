import streamlit as st
import os
import pandas as pd
from model import get_response
import ast, json
from plot import generate_plot
from agent import response_fig, response_code
import plotly.graph_objs as go

# Page config
st.set_page_config("Indius Ai", layout="wide")

# Add logo
st.logo("logo.png")

def files_exist():
    """Used to check files in 'files' folder"""
    if not os.path.exists("files"):
        os.makedirs("files")
    return bool(os.listdir("files") if os.path.exists("files") else False)

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
        tab1, tab2, tab3 = st.tabs(["Table", "Plots", "Summary"])

        with tab1:
            # Load data
            if selected_file.endswith("csv"):
                df = pd.read_csv(f"files/{selected_file}")
            else:
                df = pd.read_excel(f"files/{selected_file}")

            st.write(df.head())
            data_info = df.head()

            # Generate and cache questions
            if ('stored_file' not in st.session_state or
                st.session_state.stored_file != selected_file):
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

            # Display question buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                st.button(question1, key="q1")
            with col2:
                st.button(question2, key="q2")
            with col3:
                st.button(question3, key="q3")

            # Query container with button-driven interaction
            with st.container(border=True):
                st.write(f"File name: {selected_file}")
                query = st.text_input("", placeholder="Ask anything...", key="tab1_input")
                ask_button = st.button("Ask", key="ask_button")

                if ask_button and query:
                    resp_fig = response_fig(query, selected_file, data_info)
                    resp_code = response_code(query, selected_file, data_info)
                    st.write(resp_code)
                    if isinstance(resp_fig, go.Figure):
                        st.plotly_chart(resp_fig)
                    else:
                        st.error(f"Error generating visualization...")

        with tab2:
            # Load data
            if selected_file.endswith("csv"):
                df = pd.read_csv(f"files/{selected_file}")
            else:
                df = pd.read_excel(f"files/{selected_file}")

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
                st.plotly_chart(generate_plot(df, plot_type, X_axis, Y_axis))

else:
    with st.container(border=True):
        st.subheader("What do you want to do?")
        query = st.text_input("", placeholder="Ask anything...", key="home_input")
