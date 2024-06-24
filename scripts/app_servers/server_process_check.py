import json

from fabric import Connection
from termcolor import colored

from helper_functions.helpers import get_non_zero_exit_status_container_processes


def server_process_check():
    with open("file_structure/app_servers/servers.json", "r") as file:
        servers = json.load(file)

    for server in servers:
        c = Connection(
            host=servers[server]["host"],
            user=servers[server]["user"],
            forward_agent=True,
        )

        server_apps = servers[server]["applications"]
        for app in server_apps:
            # Set hide to true to not print the output of .run()
            docker_ps = c.run(
                f'docker ps -a -f "label=com.docker.compose.project={app}" -f "status=exited" --format "{{{{.Names}}}},{{{{.Image}}}},{{{{.Command}}}},{{{{.Status}}}}"',
                hide=True,
            )

            docker_ps = docker_ps.stdout.strip().split("\n")

            # In case running the above "docker ps" command yields no results (no non-zero
            # and no zero exit code processes), we will get a non-empty list (i.e., docker_ps = [''])
            # and will need to filter on '' before proceeding.
            if docker_ps[0] != "":
                docker_ps_non_zero = get_non_zero_exit_status_container_processes(
                    docker_ps
                )
            else:
                docker_ps_non_zero = get_non_zero_exit_status_container_processes([])

            print("\n#")
            print(f"# Checking docker container statuses for {colored(app, "cyan")} on {colored(server, "magenta")}")
            print("#\n")

            if len(docker_ps_non_zero) > 0:
                for ps in docker_ps_non_zero:
                    print(f"{colored("*", "red")} {ps}")
            else:
                print(
                    f"{colored(app, "cyan")} has no processes that have exited with a non-zero exit code."
                )


def main():
    server_process_check()


if __name__ == "__main__":
    main()
