import io
import base64
import pdf2image
import google.generativeai as genai
from collections import Counter
import PyPDF2
import json
import re


#genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key="AIzaSyBguHoVHGD7YngrnoYONC7yDqP8DvIEzho")
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

    def get_gemini_response(self, input_text, pdf_content, prompt):



        response = self.model.generate_content([input_text, pdf_content[0], prompt])
        return response.text
    
    def evaluate_resume(self, job_description, pdf_content, prompt):
        return self.get_gemini_response(job_description, pdf_content, prompt)    



        # and then keywords missing and last final thoughts.
    def getPrompt(self, prompt_type="rank", personality=None, resumePersonality=None):
        prompts = {
                "rank": """
                You are an skilled ATS (Applicant Tracking System) scanner with a 
                deep understanding of any one job role of data science or Full stack web development or Big data engineering or 
                Devops or Data Analyst or Scrum Master or Project Manager and ATS functionality, 
                your task is to evaluate the resume against the provided job 
                description, the user personality- {personality}, and the personality retrieved from the resume- {resumePersonality}. 
                Just ignore any external link or url and rank only based on the content of the resume.
                give me the rank from 0 to 10 based on the resume match with the job description, user personality and retrieved personality from the resume,
                where 0 is no match and 10 is 100% match
                if the resume matches the job description. I want you to output the rank  
                out of 10 and reason of why you have given the following rank to the resume(make sure to keep the reason of upto 3 lines).
                In the output give only the rank and reason separated by the ampersand '&'.
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
    


    def prompt_content(self,prompt_type, personality=None, resumePersonality=None ):
        prompt = self.getPrompt(prompt_type,personality, resumePersonality)
        if not prompt:
            raise ValueError("Invalid prompt type. Choose from:  skills, rank")
        print("the prompt is ", prompt)
        return prompt
        


    def extract_resume_info(self, uploaded_file, job_description, personality,  prompt_type):


        extract_text = self.extract_text_from_file(uploaded_file)
        # 
        pdf_content = self.input_pdf_setup(uploaded_file)
        print("the pdf_content is ::",pdf_content)

        resumePersonality = self.analyze_personality(extract_text)
        print("the personality from resume is", resumePersonality)

       

        prompt = self.prompt_content(prompt_type, personality, resumePersonality)

        resumeData = self.evaluate_resume(job_description, pdf_content, prompt)
        print("the resumeData of the user is", resumeData)

        resumeInfo = resumeData.split("&",1)
        print("the rank of the user is", resumeInfo)

        entities = self.extractEntities(extract_text)
        print("the enities of the use is", entities)
      
        clean_json_string = re.sub(r"```json|```", "", entities).strip()

        entity_dict = json.loads(clean_json_string)
        
        print("the entity type is ",entity_dict)

        entity_dict['resume_personality'] = resumePersonality
        print("the resume personality attached ",entity_dict)
        entity_dict['rank'] = int(resumeInfo[0])
        print("the rank attached ",entity_dict)
        entity_dict['reason'] = resumeInfo[1]
        print("the reason attached ",entity_dict)

        
    
        
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
        print(response.text)
        return response.text
    
