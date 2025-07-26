import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

def fetch_github_trends():
    print("🔄 Fetching GitHub trending repos...")
    base_url = "https://github.com/trending"
    languages = [
    "python", "javascript", "java", "c", "c++", "c#", "go", "typescript", "ruby", "php",
    "swift", "kotlin", "rust", "dart", "scala", "perl", "lua", "haskell", "elixir", "clojure",
    "shell", "powershell", "r", "matlab", "julia", "groovy", "objective-c", "visual-basic", "assembly", "f#"
]

    all_data = []

    for lang in languages:
        url = f"{base_url}/{lang}?since=daily"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        repos = soup.find_all("article", class_="Box-row")

        for repo in repos[:5]:  # top 5 repos per language
            try:
                repo_name = repo.h2.a.text.strip().replace("\n", "").replace(" ", "")
                description_tag = repo.find("p", class_="col-9 color-fg-muted my-1 pr-4")
                description = description_tag.text.strip() if description_tag else "No description"
                stars_tag = repo.find("a", class_="Link--muted d-inline-block mr-3")
                stars = stars_tag.text.strip().replace(",", "") if stars_tag else "0"
                stars = int(float(stars.replace("K", "000").replace(".", ""))) if "K" in stars else int(stars)

                all_data.append({
                    "Language": lang.title(),
                    "Repository": repo_name,
                    "Stars": stars,
                    "Description": description,
                    "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
            except Exception as e:
                print(f"⚠️ Skipped one repo due to error: {e}")

    df = pd.DataFrame(all_data)
    df.to_csv("github_trends.csv", index=False)
    print(f"✅ Saved {len(df)} repos to github_trends.csv")

if __name__ == "__main__":
    fetch_github_trends()
