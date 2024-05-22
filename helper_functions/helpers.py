import re

import humanize

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
        (name, image, exit_status) = process.split(",")
        match = re.search(regex_pattern, exit_status)
        # Check if a match exists with a non-zero exit code
        if match and int(match.group(0)) != 0:
            result.append((name, image, exit_status))

    return result
