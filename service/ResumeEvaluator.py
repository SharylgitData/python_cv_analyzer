import io
import base64
import pdf2image
import google.generativeai as genai
from collections import Counter
import PyPDF2
import json
import re
import os
import pdb;
#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
# genai.configure(api_key="AIzaSyBguHoVHGD7YngrnoYONC7yDqP8DvIEzho")
genai.configure(api_key="AIzaSyA854D-V_vJNIgeuqd88Z8HdS776jAk5dU")
class ResumeEvaluator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def input_pdf_setup(self, uploaded_file):
        if uploaded_file is not None:
            images = pdf2image.convert_from_bytes(uploaded_file.read())
            first_page = images[0]

            img_byte_arr = io.BytesIO()
            first_page.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()

            pdf_parts = [{
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }]
            
            return pdf_parts
        else:
            raise FileNotFoundError("No file uploaded")


    
    def evaluate_resume(self,  pdf_content, prompt,job_description=None):     
        # print("the zerothe pdf content is ",pdf_content[0]) 
        # response = self.model.generate_content([job_description, pdf_content[0], prompt])
        response = self.model.generate_content([prompt, pdf_content])
        print("the response from gemini is ",response.text)
        return response.text
        



        # and then keywords missing and last final thoughts.
    def getPrompt(self, prompt_type, personality, resumePersonality, jobdescription, job_title):
        prompts = {
                # "rank": """
                # You are an skilled ATS (Applicant Tracking System) scanner with a 
                # deep understanding of any one job role of data science or Full stack web development or Big data engineering or 
                # Devops or Data Analyst or Scrum Master or Project Manager and ATS functionality, 
                # your task is to evaluate the resume against the provided job 
                # description, the user personality- {personality}, and the personality retrieved from the resume- {resumePersonality}. 
                # Just ignore any external link or url and rank only based on the content of the resume.
                # give me the rank from 0 to 10 based on the resume match with the job description, user personality and retrieved personality from the resume,
                # where 0 is no match and 10 is 100% match
                # if the resume matches the job description. I want you to output the rank  
                # out of 10 and reason of why you have given the following rank to the resume(make sure to keep the reason of upto 3 lines).
                # In the output give only the rank and reason separated by the ampersand '&'.
                # """
                # 
                # "rank": """
                #         You are an skilled ATS (Applicant Tracking System) scanner with deep knowledge of 
                #         any one job role of data science or Full stack web development or Big data engineering or Devops or Data Analyst or 
                #         Scrum Master or Project Manager and and ATS functionality,

                #         Your task is to evaluate resume against the provided job description for job role- {job_title}, user personality-{personality},
                #          and the personality extracted from the resume-{resumePersonality}. In response you strictly gives the rank and reason of 
                #         based on what factors you have given the rank(should be of max 4 lines).
                #         If rank is 100 percent then Job Description holds 40% weight, User Personality Alignment holds 30% weight, 
                #             and Resume Retrieved Personality holds 30% weight
                #         - Check for required technical skills, experience level, and relevant projects using the given job description.
                #         - make sure to focus on the matching skill of the resume with the job description. 
                #         - Give 30%  out of 40% of job description weightage 
                #         only if 80 percent of the skills matches, education is higher or equal to the required position,
                #         and  job description needs experience in particular field. 

                #         - Reduce rank if skills, education or experiences are missing from the resume. 
                #         - Evaluate if the resume reflects traits align with the provided user personality.
                #         - Reduce rank for traits that conflict with the desired personality required for the job.
                      
                #         - Compare the personality extracted from the resume to the personality expected from the job description.
                #         - Reduce rank if the resume personality conflict with the desired personality significantly.
                #         - When resume doesn't has any of the skills then rank it 0. If it matches 10% of the skills, education, and
                #         experience (if needed) then rank it as 1, if 20% then rank it as 2 and so on
                #         Output the rank from 0 to 10 where 0 is no match and 10 is 100% match along with the reason, with the format: 
                #         rank and reason separated by the ampersand(&) symbol 


                #         Remember:
                #         - Focus solely on the content of the resume.
                #         - Ignore any external links or URLs.
                #         - Penalize irrelevant or excessive non-relevant details.
                #         - Make sure to give only the rank and reason separated by the ampersand symbol format i.e rank&reason where rank is the integer and reason is string
                #          as the output and no other content
                #         - Also, ensure that you donot put up any content before the rank you will be giving of the aforementioned  format
                #         """,

               
                "rank": """
                You are an expert ATS (Applicant Tracking System) evaluator with deep understanding of any one job role of data science 
                or Full stack web development or Big data engineering or Devops or Data Analyst or Scrum Master or Project Manager and ATS functionality, 
                Your role is to assess a resume against the provided job description: '{jobdescription}' for the role: '{job_title}', 
                factoring in the user's personality: '{personality}' and the personality derived from the resume: '{resumePersonality}'.

                IN THE RESPONSE ONLY GIVE THE rank AND reason in the format : rank&reason
                You must output only the final match score from 0 to 10, followed by a reason. STRICTLY USE THIS FORMAT : rank&reason (e.g., 7&reason of the score given).

                Scoring:
                - Total: 100% split into:
                - 40%: Job Description Match (skills, education, experience)
                - 30%: User Personality Alignment with role
                - 30%: Resume Personality Match with role

                Job Description Matching Rules (40%)
                - Focus ONLY on skills explicitly listed in the job description.
                - Do NOT penalize for skills missing in the resume if they are NOT in the job description.
                - Give full 30% (of 40%) only if:
                - 80%+ of required skills match
                - Education matches or exceeds the JD
                - Experience in field is present if requested in JD
                - Reduce score proportionally if any of the above are missing.

                Personality Alignment
                - Subtract score if user personality contradicts role traits (e.g., low conscientiousness for Project Manager).
                - Subtract if resume personality conflicts with expected job behavior.
                - Reward alignment of traits with role (e.g., analytical for data science, extraverted for PMs).

               

                Additional Notes:
                - If resume has 0 matching skills: rank = 0.
                - If ~10% of the overall resume matches with the job description, and both user and resume personality matches then rank = 1, If 20%  then rank=2, if 30% then rank=3  and so on up to 10.
                - Ignore URLs and external links.
                - Do not include irrelevant or unrelated experience in reasoning.
                - Do not penalize for missing skills not mentioned in job description.
                - Return output strictly as: rank&reason

                """

                
                }
        return prompts.get(prompt_type)

                # you should return only rank and reason and no other content, containing 
                # the rank as integer, the reason based on what given the rank as the string value each of them separated by ampersand '&'


    def extract_text_from_file(self, file):

        reader = PyPDF2.PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        text = text.strip()
        return text


    # Function to analyze personality based on word usage
    def analyze_personality(self, text):
        
        words = text.lower().split()
        word_counts = Counter(words)
        
        # Expanded mapping of word categories to Big Five traits
        personality_traits = {
            "Openness": ["creative", "curious", "imaginative", "abstract", "intellectual", "artistic", "inventive", "philosophical", "experimental", "visionary", "research", "analysis", "design", "strategy", "learning", "explore", "innovation", "conceptual", "problem-solving"],
            "Conscientiousness": ["organized", "efficient", "goal", "planning", "disciplined", "responsible", "systematic", "methodical", "dependable", "hardworking", "deadline", "accuracy", "execution", "management", "detail-oriented", "structured", "documentation", "consistency", "workflow"],
            "Extraversion": ["outgoing", "energetic", "talkative", "social", "assertive", "expressive", "enthusiastic", "bold", "lively", "cheerful", "networking", "collaboration", "leadership", "presentation", "public speaking", "team player", "client-facing", "relationship-building"],
            "Agreeableness": ["kind", "trustworthy", "helpful", "friendly", "compassionate", "considerate", "cooperative", "generous", "empathetic", "nurturing", "mentorship", "teamwork", "support", "customer service", "listening", "collaborate", "partnership", "engagement"],
            "Neuroticism": ["anxious", "stressed", "worried", "emotional", "insecure", "self-conscious", "moody", "irritable", "nervous", "tense", "pressure", "deadline stress", "overwhelmed", "workload", "uncertain", "burnout", "frustration", "demanding"]
        }
        
        results = {}
        for trait, keywords in personality_traits.items():
            score = sum(word_counts[word] for word in keywords if word in word_counts)
            results[trait] = score

        max_trait = max(results, key=results.get)
                    
        return max_trait
    


    def prompt_content(self,prompt_type, personality, resumePersonality, jobdescription, job_title ):
        prompt = self.getPrompt(prompt_type,personality, resumePersonality, jobdescription, job_title)
        if not prompt:
            raise ValueError("Invalid prompt type. Choose from: skills, rank")

        prompt = prompt.format(
        jobdescription=jobdescription,
        job_title=job_title,
        personality=personality,
        resumePersonality=resumePersonality
    )
        print("the prompt is ",prompt)
        return prompt
        


    def extract_resume_info(self, uploaded_file, job_description, personality, job_title, prompt_type="rank"):


        extract_text = self.extract_text_from_file(uploaded_file)
        # 
        pdf_content = self.input_pdf_setup(uploaded_file)
        # print("the pdf_content is ::",pdf_content)

        resumePersonality = self.analyze_personality(extract_text)
        # print("the personality from resume is", resumePersonality)

        entities = self.extractEntities(extract_text)
        # print("the enities of the use is", entities)

        prompt = self.prompt_content(prompt_type, personality, resumePersonality, job_description, job_title)

        # resumeData = self.evaluate_resume(job_description, pdf_content, prompt)
        # print("the resumeData of the user is", resumeData)

        resumeData = self.evaluate_resume(entities, prompt)
        
        # resume = self.evaluate_the_resume(entities, prompt)

        resumeInfo = resumeData.split("&",1)
        print("the rank of the user is", resumeInfo)

       
      
        clean_json_string = re.sub(r"```json|```", "", entities).strip()

        entity_dict = json.loads(clean_json_string)
        
        # print("the entity type is ",entity_dict)

        entity_dict['resume_personality'] = resumePersonality
        # print("the resume personality attached ",entity_dict)
        entity_dict['rank'] = int(float(resumeInfo[0].strip()))
        # print("the rank attached ",entity_dict)
        entity_dict['reason'] = resumeInfo[1]
        # print("the reason attached ",entity_dict)

        
    
        
        return entity_dict


    def extractEntities(self, extract_text):
        prompt = """
        Extract the following from the resume doing semantic search:
        1. Name
        2. Email
        3. Phone
        4. Education (degree, field, and institution)
        5. Skills
        6. Work experience (role, company, dates, key responsibilities)
        Return the result in this JSON format:
        {{
        "name": "",
        "email":"",
        "phone":"",
        "education": [],
        "skills": [],
        "experience": []
        }}
        """

        response = self.model.generate_content([prompt, extract_text])
        #   print(response.text)
        return response.text
    
   
    # def evaluate_the_resume(self, extracted_text, prompt):
    
    
    # # Create a chat completion using gpt-3.5-turbo
    #     response = openai.ChatCompletion.create(
    #         model="gpt-3.5-turbo",
    #         messages=[
    #             {"role": "system", "content": prompt},
    #             {"role": "system", "content": extracted_text}
    #         ],
    #         max_tokens=500 
           
    #     )
    #     res = response['choices'][0]['message']['content']
    #     print("the evaluated resume respones using openai is ", res)
    #     # Extract and return the assistant's reply
    #     return res

