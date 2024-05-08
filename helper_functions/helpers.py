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
    # We first split on '_', get the last element, split again on
    # 'T' and get the YYYYMMDD timestamp.
    latest_abb_charlie_backup_timestamp = (
        latest_abb_charlie_backup[0].split("_")[-1].split("T")[0]
    )

    return latest_abb_charlie_backup[0], latest_abb_charlie_backup_timestamp
