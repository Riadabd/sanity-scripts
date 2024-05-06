from glob import glob

import os
import importlib

script_files = [f for f in glob("scripts/**/*.py", recursive=True)]

print("Available scripts:")
for i, script_file in enumerate(script_files):
    script_name = os.path.splitext(script_file)[0]
    print(f"{i+1}. {script_name}")

# Prompt the user to choose a script
choice = int(input("Enter the number of the script you want to run: "))

# Import and run the selected script
script_name = os.path.splitext(script_files[choice - 1])[0]
# Transform file path to module path
script_name = script_name.replace("/", ".")
script_module = importlib.import_module(f"{script_name}")
script_module.main()
