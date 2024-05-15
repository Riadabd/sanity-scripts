#
# Helper Functions
#


def getLatestFolderAndTimestamp(backup_folder_list) -> tuple[str, str]:
    # Get the directory with the latest timestamp.
    # We take the second entry in the list since the first
    # one in the list is "data_incremental_backup".
    latest_abb_charlie_backup = sorted(
        backup_folder_list, key=lambda backup: backup[0], reverse=True
    )[1]

    # An example backup time is: data_backup_20240117T054501.
    # We first split on '_' and get the last element to return 20240117T054501.
    latest_abb_charlie_backup_timestamp = latest_abb_charlie_backup[0].split("_")[-1]

    return latest_abb_charlie_backup[0], latest_abb_charlie_backup_timestamp
