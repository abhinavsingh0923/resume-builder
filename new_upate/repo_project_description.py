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
from langchain_huggingface import HuggingFaceEmbeddings # <--- NEW IMPORT
from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

# --- CONFIGURATION ---
# Ensure your .env file has GOOGLE_API_KEY=your_key_here
os.environ["GOOGLE_API_KEY"] = config("GOOGLE_API_KEY", default="")

if not os.environ["GOOGLE_API_KEY"]:
    # Fallback if python-decouple isn't set up
    os.environ["GOOGLE_API_KEY"] = input("Enter your Google API Key: ")

# No headers needed for public public access (limited to 60 reqs/hour)
headers = {
    "Accept": "application/vnd.github.v3+json"
}

def get_repo_file_structure(owner, repo):
    """Fetches the file tree of the repository without authentication."""
    print(f"Fetching file list for {owner}/{repo}...")
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    response = requests.get(url, headers=headers)
    
    # Fallback to 'master' if 'main' doesn't exist
    if response.status_code == 404:
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
        response = requests.get(url, headers=headers)

    if response.status_code != 200:
        if response.status_code == 403:
            print("Error: GitHub API rate limit exceeded. Try again in an hour or use a token.")
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
                return "" # Skip binary files
    return ""

def process_repo_with_gemini(owner, repo_name):
    # --- 1. Fetching Files ---
    print(f"\n--- 1. Downloading Files from {owner}/{repo_name} ---")
    
    file_tree = get_repo_file_structure(owner, repo_name)
    documents = []
    
    # Extensions to analyze
    target_extensions = ('.py', '.js', '.ts', '.md', '.txt', '.java', '.cpp')
    
    count = 0
    max_files = 10 

    for item in file_tree:
        if count >= max_files:
            print(f"Reached limit of {max_files} files.")
            break
            
        path = item['path']
        if item['type'] == 'blob' and path.endswith(target_extensions):
            if "lock" in path or "config" in path:
                continue

            print(f"Downloading: {path}")
            content = get_file_content(item['url'])
            
            if content:
                doc = Document(page_content=content, metadata={"source": path})
                documents.append(doc)
                count += 1

    if not documents:
        print("No valid code files found.")
        return

    # --- 2. Splitting Code ---
    print(f"\n--- 2. Splitting Code ({len(documents)} files) ---")
    
    text_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, 
        chunk_size=2000, 
        chunk_overlap=200
    )
    texts = text_splitter.split_documents(documents)
    print(f"Generated {len(texts)} code chunks.")

    # --- 3. Embedding (Hugging Face) ---
    print("\n--- 3. Embedding & Storing (Hugging Face) ---")
    
    # Using 'all-MiniLM-L6-v2', a small, fast, and effective model that runs locally
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Initialize Vector DB
    db = Chroma.from_documents(texts, embeddings)
    retriever = db.as_retriever(search_kwargs={"k": 10}) 

    # --- 4. Summarization (Gemini 2.5 Flash) ---
    print("\n--- 4. Analyzing Codebase (Gemini 2.5 Flash) ---")
    
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.3)

    # Create Tool
    def search_codebase_func(query: str):
        docs = retriever.invoke(query)
        return "\n\n".join([d.page_content for d in docs])

    tool = Tool(
        name="search_codebase",
        func=search_codebase_func,
        description="Searches and returns code snippets from the repository."
    )
    tools = [tool]

    # Setup LLM with Tools
    llm_with_tools = llm.bind_tools(tools)

    # Execute
    query = (
        "Analyze the retrieved code and provide a summary report containing:\n"
        "1. MAIN PURPOSE: What does this repo do?\n"
        "2. ARCHITECTURE: Key classes/functions and their roles.\n"
        "3. TECH STACK: Libraries and tools used."
    )
    
    # Run Agent Loop (Manual)
    system_message = (
        "You are a senior software architect. Use the search_codebase tool to find relevant code. "
        "Answer the user's question about the repository based on the code found. "
        "If you don't know the answer, say that you don't know."
    )
    
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=query)
    ]
    
    # 1. First Call (LLM decides to use tool)
    ai_msg = llm_with_tools.invoke(messages)
    messages.append(ai_msg)
    
    if ai_msg.tool_calls:
        print(f"Agent chose to use tools: {len(ai_msg.tool_calls)}")
        for tool_call in ai_msg.tool_calls:
            if tool_call["name"] == "search_codebase":
                print(f"Calling Tool: search_codebase...")
                # Execute tool
                tool_output = tool.invoke(tool_call["args"])
                messages.append(ToolMessage(tool_call_id=tool_call["id"], content=str(tool_output)))
        
        # 2. Final Call (LLM generates answer)
        final_response = llm_with_tools.invoke(messages)
        print(f"\n=== GEMINI ANALYSIS REPORT FOR {repo_name} ===\n")
        print(final_response.content)
    else:
        # LLM handled it directly
        print(f"\n=== GEMINI ANALYSIS REPORT FOR {repo_name} ===\n")
        print(ai_msg.content)
    
    # Cleanup Vector DB 
    db.delete_collection()

if __name__ == "__main__":
    user_input = input("Enter repo (e.g., langchain-ai/langchain): ").strip()
    try:
         # Handle full URL input
        if "github.com" in user_input:
            parts = user_input.split("github.com/")[-1].split("/")
            if len(parts) >= 2:
                owner, repo = parts[0], parts[1]
            else:
                 raise ValueError("Invalid URL format")
        elif "/" in user_input:
            owner, repo = user_input.split("/")[:2]
        else:
             raise ValueError("Invalid format. Please use 'owner/repo' or full GitHub URL")

        process_repo_with_gemini(owner.strip(), repo.strip())
    except Exception as e:
        print(f"An error occurred: {e}")