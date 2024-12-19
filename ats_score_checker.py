import streamlit as st
import google.generativeai as genai
from PyPDF2 import PdfReader
import plotly.graph_objects as go
import os

# Directly set your API key here
GOOGLE_API_KEY = "AIzaSyAKih8hHjOfJJVkvVcXtC1EAF_P7ye7N1E"

# Configure Google API key for Gemini
genai.configure(api_key=GOOGLE_API_KEY)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    try:
        pdf_reader = PdfReader(pdf_file)
        text = "".join(page.extract_text() for page in pdf_reader.pages)
        return text
    except Exception as e:
        return f"An error occurred while reading the PDF: {str(e)}"

# Function to generate ATS score and feedback
def generate_ats_score(resume_text, job_description):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Compare the following resume with the job description provided below and generate an ATS score out of 100. Provide detailed feedback on how the resume aligns with the job description and suggest improvements.

        Resume:
        {resume_text}

        Job Description:
        {job_description}

        Output the score and feedback in a structured format.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred while generating the ATS score and feedback: {str(e)}"

# Function to extract ATS score from response
def extract_score_from_feedback(feedback):
    try:
        # Assuming the feedback contains "Score: X/100"
        score_line = [line for line in feedback.splitlines() if "Score:" in line]
        if score_line:
            return int(score_line[0].split(":")[-1].strip().split("/")[0])
        return None
    except Exception as e:
        return None

# Function to create a speedometer chart
def create_speedometer(score):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        gauge={
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0, 50], "color": "red"},
                {"range": [50, 75], "color": "yellow"},
                {"range": [75, 100], "color": "green"}
            ],
            "threshold": {
                "line": {"color": "black", "width": 4},
                "thickness": 0.75,
                "value": score
            }
        }
    ))
    return fig

# Function to suggest courses based on feedback
def suggest_courses(feedback):
    # Example suggestions based on keywords in feedback
    suggestions = {
        "Python": {
            "Free": [
                {"name": "Python for Everybody", "link": "https://www.coursera.org/specializations/python", "thumbnail": "https://d3njjcbhbojbot.cloudfront.net/web/images/favicons/apple-touch-icon-76x76.png"},
                {"name": "Automate the Boring Stuff with Python", "link": "https://automatetheboringstuff.com/", "thumbnail": "https://automatetheboringstuff.com/images/logo.png"}
            ],
            "Paid": [
                {"name": "Complete Python Bootcamp", "link": "https://www.udemy.com/course/complete-python-bootcamp/", "thumbnail": "https://www.udemy.com/staticx/udemy/images/v7/logo-udemy-inverted.svg"},
                {"name": "Python Programming Masterclass", "link": "https://www.udemy.com/course/python-the-complete-python-developer-course/", "thumbnail": "https://www.udemy.com/staticx/udemy/images/v7/logo-udemy-inverted.svg"}
            ]
        },
        "Data Analysis": {
            "Free": [
                {"name": "Introduction to Data Analysis", "link": "https://www.edx.org/course/introduction-to-data-analysis", "thumbnail": "https://www.edx.org/favicon.ico"},
                {"name": "Data Analysis with Python", "link": "https://www.freecodecamp.org/learn/", "thumbnail": "https://www.freecodecamp.org/icons/icon-96x96.png"}
            ],
            "Paid": [
                {"name": "Data Analyst Nanodegree", "link": "https://www.udacity.com/course/data-analyst-nanodegree--nd002", "thumbnail": "https://www.udacity.com/favicon.ico"},
                {"name": "Excel to MySQL: Data Analysis", "link": "https://www.coursera.org/specializations/excel-mysql", "thumbnail": "https://d3njjcbhbojbot.cloudfront.net/web/images/favicons/apple-touch-icon-76x76.png"}
            ]
        }
    }

    # Extract relevant suggestions based on feedback content
    matched_suggestions = {}
    for skill, courses in suggestions.items():
        if skill.lower() in feedback.lower():
            matched_suggestions[skill] = courses

    return matched_suggestions

# Streamlit UI
st.title("Resumate")

# Job description input
job_description = st.text_area("Job Description", "Paste the job description here")

# Resume upload
uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type=["pdf"])

if st.button("Check ATS Score"):
    if job_description and uploaded_file:
        with st.spinner("Processing your resume..."):
            # Extract text from the uploaded PDF
            resume_text = extract_text_from_pdf(uploaded_file)

            if "An error occurred" not in resume_text:
                # Generate ATS score and feedback
                ats_feedback = generate_ats_score(resume_text, job_description)

                # Extract score from feedback
                ats_score = extract_score_from_feedback(ats_feedback)

                if ats_score is not None:
                    # Display speedometer chart
                    st.subheader("ATS Score")
                    speedometer_chart = create_speedometer(ats_score)
                    st.plotly_chart(speedometer_chart)

                    # Display feedback
                    st.subheader("Feedback")
                    st.write(ats_feedback)

                    # Suggest courses based on feedback
                    st.subheader("Suggested Courses")
                    course_suggestions = suggest_courses(ats_feedback)

                    if course_suggestions:
                        for skill, courses in course_suggestions.items():
                            st.markdown(f"### {skill}")

                            st.markdown("#### Free Courses")
                            for course in courses["Free"]:
                                st.markdown(f"![{course['name']}]({course['thumbnail']})")
                                st.markdown(f"- [{course['name']}]({course['link']})")

                            st.markdown("#### Paid Courses")
                            for course in courses["Paid"]:
                                st.markdown(f"![{course['name']}]({course['thumbnail']})")
                                st.markdown(f"- [{course['name']}]({course['link']})")
                    else:
                        st.write("No specific courses found. Consider improving general skills like communication and teamwork.")
                else:
                    st.error("Unable to extract ATS score from the feedback.")
            else:
                st.error(resume_text)
    else:
        st.error("Please upload your resume and provide the job description to check the ATS score.")
