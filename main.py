from test.repos_fetch import get_all_public_repos
from test.repo_project_description import process_repo_with_gemini

if __name__ == "__main__":
    print("This module is intended to be imported and used in other scripts.")
    user_input = input("Enter repo (e.g., langchain-ai/langchain): ").strip()
    try:
        # Handle full URL input
        if "github.com" in user_input:
            # Extract part after github.com/
            parts = user_input.split("github.com/")[-1].split("/")
            # Must have at least owner and repo
            if len(parts) >= 2:
                owner = parts[0]
                repo = parts[1]
            else:
                 raise ValueError("Invalid URL format")
        elif "/" in user_input:
            owner, repo = user_input.split("/")[:2] # Handle trailing slash or extra parts gracefully
        else:
            raise ValueError("Invalid format. Please use 'owner/repo' or full GitHub URL")

        process_repo_with_gemini(owner.strip(), repo.strip())
            
    except Exception as e:
        print(f"An error occurred: {e}")