import json
import os
import shutil

import yaml

from sshfs import SSHFileSystem
from termcolor import colored


def merge_dicts(dict1, dict2):
    """
    Merge two nested dictionaries and update values for duplicate keys.
    """
    merged_dict = dict1.copy()  # Create a copy of the first dictionary

    stack = [(merged_dict, dict2)]
    while stack:
        current_dict, other_dict = stack.pop()
        for key, value in other_dict.items():
            if key in current_dict:
                if isinstance(current_dict[key], dict) and isinstance(value, dict):
                    # Merge nested dictionaries
                    stack.append((current_dict[key], value))
                else:
                    # Update value for duplicate key
                    current_dict[key] = value
            else:
                # Add new key-value pair
                current_dict[key] = value

    return merged_dict


def get_services_with_missing_keys(config_object):
    """
    Filter the incoming dictionary by checking for the absence of the
    specific keys provided.
    """
    filtered_dict = {}
    service_keys = ["restart", "labels", "logging"]

    for service_key in service_keys:
        filtered_dict[service_key] = []

    for service in config_object["services"].keys():
        try:
            _ = config_object["services"][service].keys()
        except AttributeError:
            print(f"⚠️ {service} is part of the docker compose file but does not have any attached keys to it.\n")
            continue

        # Check if a service does not contain the listed keys above
        for k in service_keys:
            if k not in config_object["services"][service].keys():
                filtered_dict[k].append(service)

    return filtered_dict


def server_docker_compose_config_check():
    with open(
        "file_structure/app_servers/app_server_docker_config_keys.json", "r"
    ) as file:
        app_server_docker_config_keys = json.load(file)

    os.mkdir("tmp/")

    for server in app_server_docker_config_keys:
        os.mkdir(f"tmp/{server}")

        fs = SSHFileSystem(
            app_server_docker_config_keys[server]["host"],
            username=app_server_docker_config_keys[server]["user"],
        )

        server_apps = app_server_docker_config_keys[server]["applications"]
        for app in server_apps:
            os.mkdir(f"tmp/{server}/{app}")

            print("\n#")
            print(
                f"# Checking missing docker compose config keys for {colored(app, "cyan")} in {colored(server, "magenta")}"
            )
            print("#\n")

            current_dict = {}
            for docker_compose_file_path in app_server_docker_config_keys[server][
                "applications"
            ][app]["docker-compose-configs"]:
                fs.get(
                    rpath=docker_compose_file_path,
                    lpath=f"tmp/{server}/{app}/",
                )

                docker_compose_file_name = docker_compose_file_path.split("/")[-1]

                with open(
                    f"tmp/{server}/{app}/{docker_compose_file_name}", "r"
                ) as config_file:
                    config_object = yaml.safe_load(config_file)
                    current_dict = merge_dicts(current_dict, config_object)

            filtered_config_data = get_services_with_missing_keys(current_dict)
            print(f"{colored("Services with missing keys:", "red")}")
            for key in filtered_config_data:
                print(f"{colored(f"{key}:", "red", attrs=["reverse"])} {filtered_config_data[key]}")

    shutil.rmtree("tmp/")

    return True


def main():
    server_docker_compose_config_check()


if __name__ == "__main__":
    main()
