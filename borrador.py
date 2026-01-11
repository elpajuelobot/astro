from pathlib import Path

file_path = Path('screenshot.png')
print(file_path)

if file_path.exists():
    print("ok")
else:
    print("No")
