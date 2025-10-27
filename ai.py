# General Imports
from decouple import Config, RepositoryEnv
import os
from pathlib import Path
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List

# App Imports
import common as common

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent

# Get my environment variables from .env file
DOTENV_FILE = os.path.join(BASE_DIR, '.env')
env_config = Config(RepositoryEnv(DOTENV_FILE))
openai_organization_id = env_config.get('ORGANIZATION_ID')
openai_project_id = env_config.get('PROJECT_ID')
openai_api_key = env_config.get('OPENAI_API_KEY')

# OpenAI Client Initialization
OPENAI_API_KEY = openai_api_key
OPENAI_ORGANIZATION_ID = openai_organization_id
OPENAI_PROJECT_ID = openai_project_id

client = OpenAI(
        organization=OPENAI_ORGANIZATION_ID,
        project=OPENAI_PROJECT_ID,
        api_key=OPENAI_API_KEY)

# AI Related Functions
def get_listed_jobs_from_content(html_content: str) -> List[str]:
    """
    Extracts a list of jobs from the given HTML content of a job board page.
    ARGS:
        html_content (str): The HTML content of the job board web page.
    RETURNS:
        List[str]: A list of job titles extracted from the page.
    """
    instructions = """
        You are an expert web content analyzer.
        Given the HTML content of a job board web page, you will extract
        a list of jobs posted on that page with the following JSON format:
        Here is the wanted JSON format
        {
            "jobs": [
                {
                    "job_title": "...",
                    "job_location": "...",
                    "job_link": "...",
                    "company": "..."
                }
            ]
        }
        For the job_link, search in the provided html content, the href tag of the job, which eventually takes to the job description page.
        For the job company, look in the provided html content a span or text that might be the company of the job.
        Important, make sure to include all the jobs provided in the HTML. Do not cut the list. I want all the jobs present in the HTML I provide to you.
    """

    class Job(BaseModel):
        job_title: str = Field(..., description="Title of the job as extracted from the job board page")
        job_location: str = Field(..., description="Location of the job as extracted from the job board page")
        job_link: str = Field(..., description="Link to the job posting as extracted from the job board page")
        company: str = Field(..., description="Company offering the job as extracted from the job board page")

    class JobList(BaseModel):
        jobs: List[Job]

    query = f"""
        Here is the HTML content of the job board web page:
        {html_content}
        Make sure your output includes all the jobs in the HTML page.
        """
    response = client.responses.parse(
        model="gpt-4o-mini",
        instructions=instructions,
        input=query,
        text_format=JobList,
    )

    jobs = response.output_parsed

    return jobs
