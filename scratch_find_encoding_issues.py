import os

def find_encoding_issues(directory):
    for root, dirs, files in os.walk(directory):
        if 'venv' in dirs:
            dirs.remove('venv')
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in files:
            if file.endswith(('.py', '.html', '.css', '.js', '.md', '.env', '.txt')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        f.read()
                except UnicodeDecodeError as e:
                    print(f"Error in {path}: {e}")

if __name__ == "__main__":
    find_encoding_issues('.')
