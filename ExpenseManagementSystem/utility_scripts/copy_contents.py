import pyperclip
import os

def read_file_content(file_path):
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return f"File not found: {file_path}\n"

def main():
    base_path = 'C:\\Users\\Dan\'s PC\\Desktop\\Expense Management System\\expensemanagementsystem\\'  # Corrected the path
    content = ""
    files_to_copy = {
        "models.py": os.path.join(base_path, "expenses", "models.py"),
        "forms.py": os.path.join(base_path, "expenses", "forms.py"),
        "views.py": os.path.join(base_path, "expenses", "views.py"),
        "urls.py": os.path.join(base_path, "expensemanagementsystem", "urls.py")
    }

    for file_name, file_path in files_to_copy.items():
        content += f"--- {file_name} ---\n"
        content += read_file_content(file_path) + "\n\n"

    pyperclip.copy(content)
    print("Contents copied to clipboard.")

if __name__ == "__main__":
    main()
