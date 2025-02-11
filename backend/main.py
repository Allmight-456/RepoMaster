from typing import Any
from pydantic import BaseModel, HttpUrl
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from prompts import prompt_00, prompt_04, prompt_05  # (Include other prompts as needed)
import re
import os
import uvicorn
import logging
import subprocess
import tempfile

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain  # Explicit chain class

# Initialize FastAPI application with metadata
app = FastAPI(
    title="RepoMaster Documentation API",
    description="API for generating structured documentation from codebase using Gemini and Langchain",
    version="1.0.0"
)

# Allow CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load environment variables and initialize the Gemini LLM
load_dotenv()
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1,
    max_output_tokens=4096
)

# Define the API input model
class RepoURL(BaseModel):
    url: HttpUrl
    
def is_valid_github_url(url: str) -> bool:
    pattern = r"^https?://(www\.)?github\.com/[\w\-\.]+/[\w\-\.]+(\.git)?/?$"
    return re.match(pattern, url) is not None


async def run_repomix(repo_url: str) -> str:
    """
    Run Repomix on a remote GitHub repository to generate a .txt file 
    containing the codebase content.
    """
    try:
        repo_url = str(repo_url)
        temp_dir = tempfile.mkdtemp()
        packed_file_path = os.path.join(temp_dir, "packed_codebase.txt")
        result = subprocess.run(
            ["repomix", "--remote", repo_url, "--output", packed_file_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            raise RuntimeError(f"Repomix failed: {result.stderr.decode()}")
        return packed_file_path

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error during Repomix execution: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Error in processing remote repository: {str(e)}")

@app.post("/generate-docs-from-url")
async def generate_docs_from_url(repo_url: RepoURL):
    """
    Generate README/documentation from a remote GitHub repository.
    (Uses prompt_00)
    """
    try:
        normalized_url = str(repo_url.url).rstrip("/")
        if not is_valid_github_url(normalized_url):
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")

        # Run repomix and read the resulting file
        packed_file = await run_repomix(normalized_url)
        with open(packed_file, "r", encoding="utf-8") as f:
            codebase_content = f.read()

        # Create an LLMChain using the README prompt (prompt_00)
        prompt_template = PromptTemplate(input_variables=["codebase"], template=prompt_00)
        chain = LLMChain(llm=llm, prompt=prompt_template)
        result = await chain.arun({"codebase": codebase_content})
        
        # Clean the result by removing any markdown indicators at the start
        cleaned_result = result.replace('```markdown\n', '').replace('```\n', '').strip()
        
        # Return the cleaned README as a JSON object
        return {"readme": cleaned_result}

    except Exception as e:
        logging.exception("Error generating documentation")
        raise HTTPException(status_code=500, detail=f"Documentation generation failed: {str(e)}")

@app.post("/generate-dockerfile")
async def generate_dockerfile(repo_url: RepoURL):
    """
    Generate a Dockerfile from a remote GitHub repository.
    (Uses prompt_04)
    """
    try:
        normalized_url = str(repo_url.url).rstrip("/")
        if not is_valid_github_url(normalized_url):
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")

        packed_file = await run_repomix(normalized_url)
        with open(packed_file, "r", encoding="utf-8") as f:
            codebase_content = f.read()

        prompt_template = PromptTemplate(input_variables=["codebase"], template=prompt_04)
        chain = LLMChain(llm=llm, prompt=prompt_template)
        result = await chain.arun({"codebase": codebase_content})
        return result

    except Exception as e:
        logging.exception("Error generating Dockerfile")
        raise HTTPException(status_code=500, detail=f"Dockerfile generation failed: {str(e)}")

@app.post("/generate-docker-compose")
async def generate_docker_compose(repo_url: RepoURL):
    """
    Generate a Docker Compose configuration from a remote GitHub repository.
    (Uses prompt_05)
    """
    try:
        normalized_url = str(repo_url.url).rstrip("/")
        if not is_valid_github_url(normalized_url):
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")

        packed_file = await run_repomix(normalized_url)
        with open(packed_file, "r", encoding="utf-8") as f:
            codebase_content = f.read()

        prompt_template = PromptTemplate(input_variables=["codebase"], template=prompt_05)
        chain = LLMChain(llm=llm, prompt=prompt_template)
        result = await chain.arun({"codebase": codebase_content})
        return result

    except Exception as e:
        logging.exception("Error generating Docker Compose")
        raise HTTPException(status_code=500, detail=f"Docker Compose generation failed: {str(e)}")

@app.get("/ping")
async def ping():
    """A lightweight route to confirm the server is running."""
    return {"message": "Pong!"}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
