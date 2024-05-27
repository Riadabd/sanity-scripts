import json

from sshfs import SSHFileSystem
from termcolor import colored

from helper_functions.helpers import server_app_folder_content_check


def server_file_and_folder_check():
    with open("file_structure/app_servers/app_server_content.json", "r") as file:
        app_server_content = json.load(file)

    for server in app_server_content:
        fs = SSHFileSystem(
            app_server_content[server]["host"],
            username=app_server_content[server]["user"],
        )

        server_apps = app_server_content[server]["applications"]
        for app in server_apps:
            print("\n#")
            print(f"# Checking app folder content for {colored(app, "cyan")} in {colored(server, "magenta")}")
            print("#\n")

            if server_app_folder_content_check(fs, app_server_content, server, app):
                print("File and folder content check was successful. ✅")
            else:
                print("File and folder content check was unsuccessful. ❌")
                # return False

    return True


def main():
    server_file_and_folder_check()


if __name__ == "__main__":
    main()
