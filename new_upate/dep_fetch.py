import os
import requests
import base64
from decouple import config

# --- LANGCHAIN IMPORTS ---
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_core.messages import SystemMessage, HumanMessage

# --- CONFIGURATION ---
os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY", default="")

if not os.environ["GOOGLE_API_KEY"]:
    os.environ["GOOGLE_API_KEY"] = input("Enter your Google API Key: ")

headers = {
    "Accept": "application/vnd.github.v3+json"
}

# Key files that define project dependencies
DEPENDENCY_FILES = {
    'requirements.txt', 'Pipfile', 'pyproject.toml', 'setup.py', # Python
    'package.json', # Node/JS
    'go.mod', # Go
    'pom.xml', 'build.gradle', # Java
    'Cargo.toml', # Rust
    'Gemfile', # Ruby
    'composer.json' # PHP
}

DEVOPS_FILES = {
    'Dockerfile', 'Containerfile', 'docker-compose.yml', 'docker-compose.yaml',
    'Procfile', 'fly.toml', 'vercel.json', 'netlify.toml',
    'Makefile'
}

def get_repo_file_structure(owner, repo):
    """Fetches the file tree of the repository."""
    print(f"Fetching file list for {owner}/{repo}...")
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    response = requests.get(url, headers=headers)
    
    if response.status_code == 404:
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
        response = requests.get(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 403:
            print("Error: GitHub API rate limit exceeded.")
        else:
            print(f"Error fetching tree: {response.status_code}")
        return []
    
    return response.json().get("tree", [])

def get_file_content(url):
    """Fetches and decodes raw content from GitHub."""
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        if "content" in content and content["encoding"] == "base64":
            try:
                return base64.b64decode(content["content"]).decode('utf-8')
            except UnicodeDecodeError:
                return "" 
    return ""

def process_repo_with_gemini(owner, repo_name):
    print(f"\n--- 1. Scanning for Dependency Files in {owner}/{repo_name} ---")
    
    file_tree = get_repo_file_structure(owner, repo_name)
    documents = []
    
    # Extensions for general code analysis
    # code_extensions = ('.py', '.js', '.ts', '.md', '.java', '.go', '.rs')
    
    count = 0
    max_files = 12 
    dependency_file_found = False

    # Sort tree to prioritize dependency and DevOps files
    def get_priority(item):
        filename = item['path'].split('/')[-1]
        path = item['path']
        if filename in DEPENDENCY_FILES or filename in DEVOPS_FILES or path.startswith(".github/workflows"):
            return 0
        return 1
    
    sorted_tree = sorted(file_tree, key=get_priority)

    for item in sorted_tree:
        if count >= max_files:
            break
            
        path = item['path']
        filename = path.split('/')[-1]
        
        is_dependency = filename in DEPENDENCY_FILES
        is_devops = (
            filename in DEVOPS_FILES or 
            path.startswith(".github/workflows") or
            path.endswith((".tf", ".yaml", ".yml")) # Be broader for K8s/Actions
        )

        # Only process if it's a dependency or DevOps file
        if item['type'] == 'blob' and (is_dependency or is_devops):
            
            # Skip lock files (too verbose) or weird configs
            if "lock" in filename: 
                continue

            print(f"Downloading: {path} {'[DEVOPS]' if is_devops else '[DEPENDENCY]'}")
            content = get_file_content(item['url'])
            
            if content:
                # Add metadata tag specifically for dependency files
                doc_type = "dependency_file" if is_dependency else "devops_config"
                if is_dependency: 
                    dependency_file_found = True

                doc = Document(page_content=content, metadata={"source": path, "type": doc_type})
                documents.append(doc)
                count += 1

    print(f"DEBUG: Found {len(documents)} matching documents.")
    for d in documents:
        print(f"DEBUG: Keeping {d.metadata['source']}")

    if not documents:
        print("No valid files found.")
        return
        
    if not dependency_file_found:
        print("⚠️ Warning: No explicit dependency file (e.g., requirements.txt, package.json) found. Analysis might be less accurate.")

    # --- 2. Splitting Code ---
    print(f"\n--- 2. Splitting Documents ({len(documents)} files) ---")
    
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, 
        chunk_size=2000, 
        chunk_overlap=200
    )
    texts = text_splitter.split_documents(documents)

    # --- 3. Embedding (Hugging Face) ---
    print("\n--- 3. Embedding & Storing (Hugging Face) ---")
    

# [Image of neural network embedding layer]

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    db = Chroma.from_documents(texts, embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 10}) 

    # --- 4. Classification & Summary (Gemini) ---
    print("\n--- 4. Classifying Project Type (Gemini 2.5 Flash) ---")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.1) # Lower temp for factual classification

    system_prompt = (
        "You are a Senior Technical Analyst. Your goal is to inspect the provided dependency files "
        "(like requirements.txt, package.json, etc.) to determine the project type. "
        "Ignore any other file types if present.\n\n"
        "Context:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # Manual RAG implementation because langchain.chains is missing
    query = (
        "Analyze the retrieved files to classify this project and assess its DevOps maturity.\n"
        "1. **DETECTED DEPENDENCIES**: List the key libraries found.\n"
        "2. **PROJECT CLASSIFICATION**: (Gen AI, Web Dev, etc.)\n"
        "3. **DEVOPS & INFRASTRUCTURE ANALYSIS**:\n"
        "   - **Containerization**: Is there a Dockerfile? Any multi-stage builds? Suggest improvements.\n"
        "   - **CI/CD**: Are there GitHub Actions flows? What do they do (test, deploy)?\n"
        "   - **Infrastructure**: Is there Terraform or Kubernetes config?\n"
        "   - **Rating**: Rate DevOps maturity from Low to High.\n"
        "4. **JUSTIFICATION**: Brief explanation."
    )

    # 1. Retrieve
    relevant_docs = retriever.invoke(query)
    context_text = "\n\n".join([d.page_content for d in relevant_docs])

    # 2. Augment
    final_prompt = [
        SystemMessage(content=system_prompt.format(context=context_text)),
        HumanMessage(content="Classify this project and analyze its DevOps configuration.")
    ]

    # 3. Generate
    response = llm.invoke(final_prompt)
    
    print(f"\n=== PROJECT TYPE ANALYSIS: {repo_name} ===\n")
    print(response.content)
    
    db.delete_collection()

if __name__ == "__main__":
    user_input = input("Enter repo (e.g., langchain-ai/langchain): ").strip()
    try:
        if "github.com" in user_input:
            parts = user_input.split("github.com/")[-1].split("/")
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
            else:
                 raise ValueError("Invalid URL")
        elif "/" in user_input:
            owner, repo = user_input.split("/")[:2]
        else:
             raise ValueError("Invalid format")

        process_repo_with_gemini(owner.strip(), repo.strip())
    except Exception as e:
        print(f"An error occurred: {e}")