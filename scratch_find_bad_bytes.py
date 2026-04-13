import os

def find_bad_bytes(directory):
    for root, dirs, files in os.walk(directory):
        if 'venv' in dirs:
            dirs.remove('venv')
        if '.git' in dirs:
            dirs.remove('.git')
        
        for file in sorted(files):
            if file.endswith(('.py', '.env', '.txt', '.md', '.html', '.css', '.js')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                        content.decode('utf-8')
                except UnicodeDecodeError as e:
                    print(f"File: {path}")
                    print(f"Error: {e}")
                    # Show the context around the error
                    start = max(0, e.start - 20)
                    end = min(len(content), e.end + 20)
                    print(f"Problematic sequence (hex): {content[e.start:e.end].hex()}")
                    print(f"Context (raw): {content[start:end]}")
                    print("-" * 20)

if __name__ == "__main__":
    find_bad_bytes('.')
