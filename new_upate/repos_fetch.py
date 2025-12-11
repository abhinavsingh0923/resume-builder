import requests

def get_all_public_repos(username):
    """
    Fetches all public repository names for a given GitHub user.
    """
    repos_list = []
    page = 1
    # GitHub limits unauthenticated requests to 60 per hour.
    # We fetch 100 repos per page to minimize requests.
    url = f"https://api.github.com/users/{username}/repos"
    
    print(f"Fetching repositories for user: {username}...")

    while True:
        params = {
            "page": page,
            "per_page": 100  
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            print(f"Error: Unable to fetch data (Status Code: {response.status_code})")
            print("Check if the username is correct or if you hit the rate limit.")
            break
            
        data = response.json()
        
        if not data:
            break
            

        for repo in data:
            repos_list.append(repo['name'])
            
        page += 1

    return repos_list

if __name__ == "__main__":
    target_user = input("Enter GitHub username: ")
    
    public_repos = get_all_public_repos(target_user)
    
    if public_repos:
        print(f"\nFound {len(public_repos)} public repositories:")
        for idx, repo_name in enumerate(public_repos, 1):
            print(f"{idx}. https://github.com/{target_user}/{repo_name}")
    else:
        print("No public repositories found or user does not exist.")