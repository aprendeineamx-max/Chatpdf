
import os

repo_path = r"data\shared_repos\crawlbase-mcp"
print(f"Listing: {repo_path}")
try:
    items = os.listdir(repo_path)
    for item in items:
        print(f" - {item} (Dir: {os.path.isdir(os.path.join(repo_path, item))})")
        
    src_path = os.path.join(repo_path, "src")
    if os.path.exists(src_path):
        print("\nListing src:")
        print(os.listdir(src_path))
    else:
        print("\nsrc folder NOT FOUND")

except Exception as e:
    print(e)
