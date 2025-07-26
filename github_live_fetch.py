import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# ✅ Load GitHub token
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
print("✅ TOKEN LOADED:", GITHUB_TOKEN[:6], "...")

headers = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}

def get_github_trending_languages():
    languages = ['Python', 'JavaScript', 'Java', 'C++', 'C#', 'TypeScript', 'Go', 'Rust', 'Kotlin', 'PHP',
                 'Swift', 'Ruby', 'R', 'Dart', 'Scala', 'Perl', 'Haskell', 'Lua', 'Shell', 'Objective-C',
                 'MATLAB', 'PowerShell', 'Visual Basic', 'Assembly', 'Elixir', 'COBOL', 'Groovy', 'SQL', 'Julia', 'Fortran']

    today = datetime.now()
    last_month = today - timedelta(days=30)
    date_str = last_month.strftime('%Y-%m-%d')

    lang_counts = []
    print(f"\n📦 Fetching GitHub repos created since {date_str}...\n")

    for lang in languages:
        query = f"language:{lang} created:>{date_str}"
        url = f"https://api.github.com/search/repositories?q={query}&per_page=1"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            count = response.json().get('total_count', 0)
            print(f"✅ {lang}: {count}")
            lang_counts.append({'language': lang, 'repo_count': count})
        else:
            print(f"❌ {lang} - Failed (Status {response.status_code})")
            lang_counts.append({'language': lang, 'repo_count': 0})

    lang_counts.sort(key=lambda x: x['repo_count'], reverse=True)
    return lang_counts

# Test run
if __name__ == "__main__":
    print("🔄 Running GitHub Live Fetch...\n")
    results = get_github_trending_languages()
    print("\n📊 Final Trending Languages:\n")
    for entry in results:
        print(f"{entry['language']}: {entry['repo_count']}")
