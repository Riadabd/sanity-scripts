import json
import collections

from sshfs import SSHFileSystem
from dotenv import dotenv_values
from datetime import datetime, date

from helper_functions.helpers import (
    get_latest_folder_and_timestamp,
    get_nth_folder_and_timestamp,
    get_folder_size,
)


def server_latest_backup_checks(latest_server_backup_timestamp: str) -> bool:
    # Parse the latest backup datetime string
    latest_timestamp = datetime.strptime(
        latest_server_backup_timestamp, "%Y%m%dT%H%M%S"
    ).strftime("%Y%m%d")

    # Format today's timestamp as YYYYMMDD to compare it with the
    # latest backup timestamp.
    current_timestamp = date.today().strftime("%Y%m%d")

    return latest_timestamp == current_timestamp


# Checks whether the top-level backup folder is present for all backed up apps
# running on a particular.
def server_app_folder_check(fs, latest_timestamp_folder, app_list) -> bool:
    server_apps = [
        detail["name"].split("/")[-1]
        for detail in fs.ls(f"{latest_timestamp_folder}/data", detail=True)
    ]

    return sorted(app_list) == sorted(server_apps)


# Check the content of each app folder
def server_app_folder_content_check(
    fs, latest_timestamp_folder, server_filesystem_structure, server, app
) -> bool:
    root_folder = f"{latest_timestamp_folder}/data"

    queue = collections.deque([server_filesystem_structure[server][app]])

    while queue:
        node_file_structure = queue.popleft()

        current_folder = f"{root_folder}/{node_file_structure["path"]}"

        # Perform file check for current level
        if "expected-files" in node_file_structure.keys():
            item = "expected-files"

            actual_files = [
                detail["name"].split("/")[-1]
                for detail in fs.ls(
                    f"{current_folder}",
                    detail=True,
                )
                if detail["type"] == "file"
            ]

            if sorted(node_file_structure[item]) != sorted(actual_files):
                print(
                    f"Found {actual_files} in {current_folder} for {app} instead of {sorted(node_file_structure[item])}. ❌\n"
                )
                # return False
            else:
                print(
                    f"Expected files and actual files match up in {current_folder} for {app}. ✅\n"
                )

        if "expected-file-extensions" in node_file_structure.keys():
            actual_backup_files = [
                (detail["name"].split("/")[-1], detail["size"])
                for detail in fs.ls(
                    f"{current_folder}",
                    detail=True,
                )
                if detail["type"] == "file"
            ]

            extension_file_count = dict()
            for extension in node_file_structure["expected-file-extensions"]:
                extension_file_count[extension] = len(
                    [
                        name
                        for name, size in actual_backup_files
                        if name.split(".", 1)[-1] == extension
                    ]
                )

            if sorted(extension_file_count.keys()) == sorted(
                node_file_structure["expected-file-extensions"]
            ):
                for key in extension_file_count.keys():
                    print(
                        f"* Found {extension_file_count[key]} .{key} files in {current_folder} for {app}.\n"
                    )
            else:
                print("There was an extension mismatch!\n")

        # Perform folder check for current level
        expected_folders = [
            item
            for item in node_file_structure.keys()
            if isinstance(node_file_structure[item], dict)
        ]

        actual_folders = [
            detail["name"].split("/")[-1]
            for detail in fs.ls(f"{current_folder}", detail=True)
            if detail["type"] == "directory"
        ]

        if expected_folders and actual_folders:
            if sorted(expected_folders) != sorted(actual_folders):
                print(
                    f"Found {sorted(actual_folders)} folders in {current_folder} for {app} instead of {sorted(expected_folders)}. ❌\n"
                )
                # return False
            else:
                print(
                    f"Expected folders and actual folders match up in {current_folder} for {app}. ✅\n"
                )

        # Append folders (e.g., json dictionary keys) to a queue
        # for processing.
        for item in node_file_structure.keys():
            if isinstance(node_file_structure[item], dict):
                queue.append(node_file_structure[item])

    return True


#
# Compare today's backup folder size with the one from yesterday. In all cases almost
# (except when: virtuoso size optimization is performed, delete queries are run removing
# large amounts of data), today's backup must be greater than or equal to that from yesterday.
#
def check_backup_size(
    fs,
    latest_folder_timestamp,
    second_latest_folder_timestamp,
    full_backup_locations,
    server,
    app,
) -> bool:
    app_backup_locations = full_backup_locations[server][app]["backup-folders"]

    for backup_folder in app_backup_locations:
        full_backup_path = f"{latest_folder_timestamp[0]}/data/{app}/{backup_folder}"
        full_backup_path_1 = (
            f"{second_latest_folder_timestamp[0]}/data/{app}/{backup_folder}"
        )
        backup_files = [
            (detail["name"], detail["size"])
            for detail in fs.ls(f"{full_backup_path}", detail=True)
            if detail["type"] == "file"
        ]

        backup_files_1 = [
            (detail["name"], detail["size"])
            for detail in fs.ls(f"{full_backup_path_1}", detail=True)
            if detail["type"] == "file"
        ]

        today_date = (
            datetime.strptime(latest_folder_timestamp[1], "%Y%m%dT%H%M%S")
            .date()
            .isoformat()
        )
        yesterday_date = (
            datetime.strptime(second_latest_folder_timestamp[1], "%Y%m%dT%H%M%S")
            .date()
            .isoformat()
        )

        print(
            f"Backup size for {full_backup_path_1} on {yesterday_date} is {get_folder_size(backup_files_1)}"
        )

        print(
            f"Backup size for {full_backup_path} on {today_date} is {get_folder_size(backup_files)}\n"
        )

    return True


# Runs all backup checks
def server_backup_checks(fs) -> bool:
    with open("file_structure/app_server_content.json", "r") as file:
        server_apps = json.load(file)

    for server in server_apps:
        server_backups = [
            (detail["name"], detail["type"])
            for detail in fs.ls(f"/{server}", detail=True)
        ]

        latest_server_backup_folder_name, latest_server_backup_timestamp = (
            get_latest_folder_and_timestamp(server_backups)
        )

        # Fetch the second latest top-level backup folder and its timestamp.
        # The index is 2 (instead of 1) since the zeroth entry is occupied by a non-timestamped folder.
        (
            second_latest_server_backup_folder_name,
            second_latest_server_backup_timestamp,
        ) = get_nth_folder_and_timestamp(server_backups, 2)

        print("\n#")
        print(f"# Checking if {server} has today's backup")
        print("#\n")

        if server_latest_backup_checks(latest_server_backup_timestamp):
            print(f"{server} has a backup folder with today's timestamp. ✅")
        else:
            print(f"{server} does not have a backup folder with today's timestamp. ❌")
            # return False

        print("\n#")
        print(
            f"# Checking if {server} has a top-level folder for each app ({list(server_apps[server].keys())})"
        )
        print("#\n")

        if server_app_folder_check(
            fs, latest_server_backup_folder_name, server_apps[server]
        ):
            print(f"{server} has a top-level folder for each application. ✅")
        else:
            print(f"{server} does not have a top-level folder for each application. ❌")
            # return False

        for app in server_apps[server]:
            print("\n#")
            print(f"# Checking app folder content for {app} in {server}")
            print("#\n")

            if server_app_folder_content_check(
                fs, latest_server_backup_folder_name, server_apps, server, app
            ):
                print("File and folder content check was successful. ✅")
            else:
                print("File and folder content check was unsuccessful. ❌")
                # return False

    # Check and compare backup folder sizes
    with open("file_structure/app_backups.json", "r") as file:
        full_backup_locations = json.load(file)

    print("\n#")
    print("# Checking Backups")
    print("#\n")

    for server in full_backup_locations:
        # NOTE: Duplicate snippet from the for-loop above. However, we cannot know whether
        # a user specifies the same servers and apps to have their backups checked, so it is
        # safer to fetch the latest folders and timestamps again.
        server_backups = [
            (detail["name"], detail["type"])
            for detail in fs.ls(f"/{server}", detail=True)
        ]

        latest_server_backup_folder_name, latest_server_backup_timestamp = (
            get_latest_folder_and_timestamp(server_backups)
        )

        # Fetch the second latest top-level backup folder and its timestamp.
        # The index is 2 (instead of 1) since the zeroth entry is occupied by a non-timestamped folder.
        (
            second_latest_server_backup_folder_name,
            second_latest_server_backup_timestamp,
        ) = get_nth_folder_and_timestamp(server_backups, 2)

        for app in full_backup_locations[server]:
            print("\n#")
            print(f"# Checking Backups for {app} on {server}")
            print("#\n")

            check_backup_size(
                fs,
                (
                    latest_server_backup_folder_name,
                    latest_server_backup_timestamp,
                ),
                (
                    second_latest_server_backup_folder_name,
                    second_latest_server_backup_timestamp,
                ),
                full_backup_locations,
                server,
                app,
            )


def backup_server_checks() -> None:
    config = dotenv_values(".env/.env.sftp")

    # Connect with a password
    fs = SSHFileSystem(
        config["address"], username=config["username"], password=config["password"]
    )

    server_backup_checks(fs)


def main():
    backup_server_checks()


if __name__ == "__main__":
    main()
