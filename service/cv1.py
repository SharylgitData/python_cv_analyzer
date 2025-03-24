from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
from PIL import Image
import pdf2image
import google.generativeai as genai
import io
import base64
import pdb

#got the api key from the following website https://aistudio.google.com/app/apikey
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    #convert pdf into image
    model=genai.GenerativeModel('gemini-1.5-flash')
    response=model.generate_content([input, pdf_content[0], prompt])
    return response.text

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        #convert the pdf to image
        images=pdf2image.convert_from_bytes(uploaded_file.read())
        first_page=images[0]

        #convert to bytes
        img_byte_arr=io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr=img_byte_arr.getvalue()

        pdf_parts=[
            {
                "mime_type" : "image/jpeg",
                "data":base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")
    


#streamlit Api
st.set_page_config(page_title="Shabana's ATS Resume Analyser")
st.header("Resume Evaluator")
input_text=st.text_area("Job description: ", key="input")
uploaded_file = st.file_uploader("Upload your resume in pdf format", type=["pdf",])

print(f"uploaded_file:: {uploaded_file}")

if uploaded_file is not None:
    st.write("PDF uploaded successfully")


submit1 = st.button("Tell me about the resume")
submit2 = st.button("How can I improvise my skills")
submit3= st.button("Percentage match")

input_prompt1= """
You are an experienced HR with Tech experience in the field of any one of the job roles from
data science or Full stack web development or Big data engineering or 
Devops or Data Analyst. 
your task is to review the provided resume against the job description
for these profiles.
Please share your professional evaluation on whether the candidate's 
profile aligns with the role.
Highlight the stregths and weaknesses of the applicant in relation to the specified job requirement.
""" 

input_prompt2="""
You are an skilled professional who has deep understanding of any one job role of 
data science or Java developer or Web developer or Fullstack developer or Big data engineer 
or devops or data analyst or ML engineer.
your task is to evaluate the resume against the provided job 
description. give me the skills which can increase the chances of getting the job as per the given job description.
. First the output should come as the skills that are needed and are missing in the resume for the desired job 
and then give the skills which are present in the resume with some insightful thoughts.
"""

input_prompt3="""
You are an skilled ATS (Applicant Tracking System) scanner with a 
deep understanding of any one job role of data science  or Full stack web development or Big data engineering or 
Devops or Data Analyst and ATS functionality, 
your task is to evaluate the resume against the provided job 
description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage 
and then keywords missing and last final thoughts.
"""


if submit1:
    if uploaded_file is not None:
        pdf_content= input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_prompt1,pdf_content, input_text)
        st.subheader("Here's the information about you ::")
        st.write(response)


    else:
        st.write("please upload the resume")

elif submit2:
    if uploaded_file is not None:
        pdf_content= input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_prompt2,pdf_content, input_text)
        st.subheader("Points to improvise your skills  :: ")
        st.write(response)
    else:
        st.write("please upload the resume")

elif submit3:
    if uploaded_file is not None:
        pdf_content= input_pdf_setup(uploaded_file)
        response=get_gemini_response(input_prompt3,pdf_content, input_text)
        st.subheader("Percentage match score :: ")
        st.write(response)

    else:
        st.write("please upload the resume")



