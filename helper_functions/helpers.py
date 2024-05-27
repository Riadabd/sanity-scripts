import re
import collections

import humanize
from termcolor import colored

#
# Helper Functions
#


def get_latest_folder_and_timestamp(backup_folder_list) -> tuple[str, str]:
    # Get the directory with the latest timestamp.
    # We take the second entry in the list since the first
    # one is occupied by a non-timestamped folder.
    latest_abb_charlie_backup = sorted(
        backup_folder_list, key=lambda backup: backup[0], reverse=True
    )[1]

    # An example backup time is: data_backup_20240117T054501.
    # We first split on '_' and get the last element to return 20240117T054501.
    latest_abb_charlie_backup_timestamp = latest_abb_charlie_backup[0].split("_")[-1]

    return latest_abb_charlie_backup[0], latest_abb_charlie_backup_timestamp


def get_nth_folder_and_timestamp(backup_folder_list, index) -> tuple[str, str]:
    # Get the directory with the latest timestamp.
    # We take the second entry in the list since the first
    # one in the list is "data_incremental_backup".
    latest_abb_charlie_backup = sorted(
        backup_folder_list, key=lambda backup: backup[0], reverse=True
    )[index]

    # An example backup time is: data_backup_20240117T054501.
    # We first split on '_' and return the last element to get
    # 20240117T054501.
    latest_abb_charlie_backup_timestamp = latest_abb_charlie_backup[0].split("_")[-1]

    return latest_abb_charlie_backup[0], latest_abb_charlie_backup_timestamp


# Check the content of each app folder
def server_app_folder_content_check(
    fs, server_filesystem_structure, server, app, latest_timestamp_folder=""
) -> bool:
    root_folder = f"{latest_timestamp_folder}"

    queue = collections.deque(
        [server_filesystem_structure[server]["applications"][app]]
    )

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
                    f"❌ Mismatch between actual and expected files in {colored(current_folder, "blue")} for {colored(app, "cyan")}:\n"
                )
                print(f"* {colored("Actual files:", "red")} {sorted(actual_files)}")
                print(
                    f"* {colored("Expected files:", "green")} {sorted(node_file_structure[item])}\n"
                )
                # return False
            else:
                print(
                    f"✅ Actual files and expected files match up in {colored(current_folder, "blue")} for {colored(app, "cyan")}.\n"
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
                        f"* Found {extension_file_count[key]} .{key} files in {colored(current_folder, "blue")} for {colored(app, "cyan")}.\n"
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
                    f"❌ Mismatch between actual and expected folders in {colored(current_folder, "blue")} for {colored(app, "cyan")}:\n"
                )
                print(f"* {colored("Actual folders:", "red")} {sorted(actual_folders)}")
                print(
                    f"* {colored("Expected folders:", "green")} {sorted(expected_folders)}\n"
                )
                # return False
            else:
                print(
                    f"✅ Actual folders and expected folders match up in {colored(current_folder, "blue")} for {colored(app, "cyan")}.\n"
                )

        # Append folders (e.g., json dictionary keys) to a queue
        # for processing.
        for item in node_file_structure.keys():
            if isinstance(node_file_structure[item], dict):
                queue.append(node_file_structure[item])

    return True


#
# Returns a tuple containing the file size in bytes and a humanized represenation
# of the file size (for visual purposes).
#
def get_folder_size(input_list):
    total_size_in_bytes = sum(size for _, size in input_list)

    return (total_size_in_bytes, humanize.naturalsize(total_size_in_bytes, gnu=True))


#
# Returns container processes that have a non-zero exit status code (i.e., they
# did not exit gracefully).
#
def get_non_zero_exit_status_container_processes(container_process_list):
    result = []
    regex_pattern = r"(\d+)"

    for process in container_process_list:
        (name, image, command, exit_status) = process.split(",")
        match = re.search(regex_pattern, exit_status)
        # Check if a match exists with a non-zero exit code
        if match and int(match.group(0)) != 0:
            result.append((name, image, command, exit_status))

    return result
