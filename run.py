from glob import glob

import os
import importlib
import argparse

parser = argparse.ArgumentParser(add_help=False)

# Pass the python script you want to run (optional)
parser.add_argument("-f", "--file", nargs="?", default=None, type=str)
args = parser.parse_args()

if args.file:
    script_name = os.path.splitext(args.file)[0]
else:
    # If a user does not specify the specific script to run, enumerate the
    # existing scripts inside `scripts/` for the user to choose one of them.
    script_files = [f for f in glob("scripts/**/*.py", recursive=True)]

    print("Available scripts:")
    for i, script_file in enumerate(script_files):
        script_name = os.path.splitext(script_file)[0]
        print(f"{i+1}. {script_name}")

    # Prompt the user to choose a script
    choice = int(input("Enter the number of the script you want to run: "))

    # Import and run the selected script
    script_name = os.path.splitext(script_files[choice - 1])[0]

# Transform the file path to a module path
script_name = script_name.replace("/", ".")
script_module = importlib.import_module(f"{script_name}")
script_module.main()
