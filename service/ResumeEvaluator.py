import io
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai
from collections import Counter
import logging
import re
import spacy
import PyPDF2

# Load Spacy NLP model
nlp = spacy.load("en_core_web_sm")


# load_dotenv()
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
    

        # and then keywords missing and last final thoughts.
    def evaluate_resume(self, uploaded_file, job_description, personality, resumePersonality,  prompt_type="rank"):
        prompts = {
            "summary": """
            You are an experienced HR with Tech experience like  data science or Full stack web development or Big data engineering or  
            Devops or Data Analyst or Scrum Master or Project Manager
            """,
            "rank": """
            You are an skilled ATS (Applicant Tracking System) scanner with a 
            deep understanding of any one job role of data science or Full stack web development or Big data engineering or 
            Devops or Data Analyst or Scrum Master or Project Manager and ATS functionality, 
            your task is to evaluate the resume against the provided job 
            description, the user personality- {personality}, and the personality retrieved from the resume- {resumePersonality}. give me the rank from 0 to 10 based on the resume match with the job description, where 0 is no match and 10 is 100% match
            if the resume matches the job description. I want you to only output the rank out of 10 and donot show any other content apart from rank.
           
            """,
            "entity":"""
                From the given resume, extract the Name, Contact/Mobile Number, Skills, Qualification/Education details, 
                Work experience of the candidate and give it in Key Value form. If any of the entity is missing then just give then Key and keep the value as blank.
            """,
             "personality":"""
                From the given resume, extract the personality of the user. Give the top personality
            """
        }

        prompt = prompts.get(prompt_type)
        if not prompt:
            raise ValueError("Invalid prompt type. Choose from:  skills, rank")
        print("the prompt is ", prompt)

        pdf_content = self.input_pdf_setup(uploaded_file)
        return self.get_gemini_response(job_description, pdf_content, prompt)




    # Function to extract entities (name, email, phone, skills, previous jobs) from text
    def extract_entities(self, text, rank, resume_personality):
        doc = nlp(text)
        name = None
        email = None
        phone = None
        skills = set()
        previous_jobs = set()
        education = set()
        print("the doc holds::", doc)

        # Extract name
        for ent in doc.ents:
            if ent.label_ == "PERSON" and not name:
                name = ent.text
        
        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        if email_match:
            email = email_match.group(0)
        
        # Extract phone number
        phone_match = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        if phone_match:
            phone = phone_match.group(0)
        
        # Extract skills (based on common tech and business-related keywords)
        skill_keywords = {"Python", "Java", "SQL", "Machine Learning", "AI", "Data Analysis", "Excel", "Cloud", 
                          "Project Management", "Marketing","JavaScript", "C++", "C#", "R", "Swift", "TypeScript", 
                          "Ruby", "Kotlin", "Go", "PHP", "Data Engineering", "Data Visualization", "Predictive Analytics",
                            "Big Data", "ETL", "Statistical Analysis", "Deep Learning", "Natural Language Processing", 
                            "Neural Networks", "Time Series Analysis", "AWS", "Google Cloud Platform", "Microsoft Azure", 
                            "Docker", "Kubernetes", "CI/CD Pipelines", "Terraform", "Serverless Computing", "Site Reliability Engineering", 
                            "Jenkins", "NoSQL", "MongoDB", "PostgreSQL", "Firebase", "Redis", "GraphQL", "Cassandra", "Hadoop", 
                            "Apache Spark", "Elasticsearch", "Ethical Hacking", "Penetration Testing", "Cryptography", "Network Security", 
                            "Firewall Management", "Intrusion Detection", "Secure Coding", "Identity & Access Management", 
                            "Cyber Threat Intelligence", "Blockchain Security", "Agile Methodologies", "Scrum", "Test-Driven Development",
                              "Microservices", "RESTful APIs", "Software Architecture", "Full Stack Development", "Backend Development", 
                              "Frontend Development", "Version Control", "Business Intelligence", "Agile Project Management", "Risk Management", 
                              "Scrum Master", "Product Management", "Business Strategy", "Lean Methodology", "Digital Transformation", "Six Sigma",
                                "Financial Modeling", "SEO", "SEM", "Google Ads", "Social Media Marketing", "Email Marketing", "Growth Hacking", 
                                "Copywriting", "Content Strategy", "A/B Testing", "Influencer Marketing","web services (SOAP/REST)","Spring Cloud","Spring Boot",
                                "Angular","Node","MVC","AWS Cloud platform"}
        for token in doc:
            if token.text in skill_keywords:
                skills.add(token.text)
        
        # Extract previous job titles (based on common job roles)
        job_titles = {"Software Engineer", "Data Analyst", "Project Manager", 
                    "Marketing Manager", "Consultant", "Researcher","Data Scientist", 
                    "Machine Learning Engineer", "AI Engineer", "Cloud Engineer", "DevOps Engineer", 
                    "Full Stack Developer", "Backend Developer", "Frontend Developer", "Cybersecurity Analyst", 
                    "Penetration Tester", "Database Administrator", "Systems Architect", "Business Intelligence Analyst", 
                    "Product Manager", "UX/UI Designer", "Financial Analyst", "IT Support Specialist", "Network Engineer", 
                    "Site Reliability Engineer", "Business Analyst", "Quality Assurance Engineer", "Scrum Master", "Blockchain Developer", 
                    "Software Architect", "Embedded Systems Engineer", "Technical Writer", "Digital Marketing Specialist", "SEO Specialist", 
                    "Social Media Manager", "Content Strategist", "Growth Hacker", "Data Engineer", "AI Research Scientist", 
                    "Cloud Solutions Architect", "Security Engineer", "IoT Engineer", "Automation Engineer", "Ethical Hacker", 
                    "Game Developer", "Computer Vision Engineer", "NLP Engineer", "Robotics Engineer", "Supply Chain Analyst", 
                    "Operations Manager", "Risk Analyst", "Sales Engineer", "E-commerce Manager", "Financial Risk Manager", 
                    "Actuary", "Economist", "Healthcare Data Analyst", "Environmental Analyst", "Policy Analyst", "CRM Manager", 
                    "HR Analyst", "Technical Recruiter", "IT Consultant", "Software Development Manager", "IT Auditor", 
                    "Biomedical Engineer", "GIS Analyst", "Energy Analyst", "Legal Analyst", "Cybersecurity Consultant",
                    "Technology Consultant", "Senior Technology Consultant", "System Engineer"}
        
        job_titles_lower = {title.lower() for title in job_titles}


        for ent in doc.ents:
            if ent.label_ == "ORG" or ent.label_ == "WORK_OF_ART":
                if ent.text.lower() in job_titles_lower:
                    previous_jobs.add(ent.text)

                # Extract education (based on degree keywords and institutions)
        education_keywords = {
            "Bachelor", "B.Sc", "B.A", "B.Tech", "BS", "BA","Bachelor's",
            "Master", "M.Sc", "M.A", "M.Tech", "MS", "MA", "MBA","Master's",
            "Ph.D", "High School", "Diploma", "Certificate", "Associate","Computer Science"
        }
        

        lines = text.split("\n")
        for line in lines:
            for keyword in education_keywords:
                if keyword.lower() in line.lower():
                    education.add(line.strip())

        # Additional check for named entities as possible institutions
        for ent in doc.ents:
            if ent.label_ == "ORG":
                for keyword in education_keywords:
                    if keyword.lower() in ent.text.lower():
                        education.add(ent.text)

        
        return {
            "name": name,
            "email": email,
            "phone": phone,
            "skills": list(skills),
            "education": list(education),
            "previous_jobs": list(previous_jobs),
            "rank": rank,
            "resume_personality":resume_personality
        }

    def extract_text_from_file(self, file):
        reader = PyPDF2.PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text.replace('o ', '').replace('|', '')


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
    

    def extract_resume_info(self, uploaded_file, job_description, personality,  prompt_type):

        extract_text = self.extract_text_from_file(uploaded_file)

        resumePersonality = self.analyze_personality(extract_text)
        print("the personality from resume is", resumePersonality)
        rank = self.evaluate_resume(uploaded_file, job_description, personality, resumePersonality,  prompt_type)
        print("the rank of the user is", rank)
        entities = self.extract_entities(extract_text, rank, resumePersonality)
        print("the entites of the user is", entities)
        return entities
