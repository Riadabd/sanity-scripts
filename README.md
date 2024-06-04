# Sanity Scripts

This repo houses a set of scripts to perform various sanity checks on servers, which can help provide detailed info targeted towards improving maintainability.

## Backup Checks

The script(s) for backup checks is(are) housed inside `scripts/backups`.

### Credentials

To be able to connect to the backup server and perform checks, the user needs to specify the server's credentials. These credentials must be placed inside `.env/.env.sftp`; `.env.sftp` must contain:

* **address**
* **username**
* **password**

### backup_check.py

This is the main backup check script and performs the following tasks:

* **Checks if a server has today's backup**
* **Checks if a server has a top-level folder for each app belonging to said server**
* **Performs file and folder content checks to make sure no unexpected files/folders are backed up**
* **Runs backup size diagnostics from yesterday and today and compare numbers**

In order to specify what servers and apps to consider, the user can write this information in *json* files inside `file_structure/`.

#### app_backup_server_content.json

The structure of this file is as follows:

```json
{
  "server-1": {
    "applications": {
      "sample-app-1": {
        "path": "sample-app-1",
        "expected-files": ["file-a.ext-a", "file-b.ext-b", "file-c.ext-a"],
        "folder-1": {
          "path": "sample-app-1/folder-1",
          "folder-1-1": {
            "path": "sample-app-1/folder-1/folder-1-1"
          }
        },
        "folder-2": {
          "path": "sample-app-1/folder-2",
          "folder-2-1": {
            "path": "sample-app-1/folder-2/folder-2-1",
            "expected-files": ["file-1.ext-1", "file-2.ext-1", "file-3.ext-2"],
            "folder-2-1-1": {
              "path": "sample-app-1/folder-2/folder-2-1/folder-2-1-1",
              "expected-file-extensions": [".ext-x"]
            },
            "folder-2-1-2": {
              "path": "sample-app-1/folder-2/folder-2-1/folder-2-1-2"
            },
            "folder-2-1-3": {
              "path": "sample-app-1/folder-2/dfolder-2-1/folder-2-1-3"
            }
          },
          "folder-2-2": {
            "path": "sample-app-1/folder-2/folder-2-2",
            "expected-files": ["file-1.ext-1", "file-2.ext-1", "file-3.ext-2"],
            "folder-2-2-1": {
              "path": "sample-app-1/folder-2/folder-2-2/folder-2-2-1",
              "expected-file-extensions": [".ext-y"]
            },
            "folder-2-2-2": {
              "path": "sample-app-1/folder-2/folder-2-2/folder-2-2-2"
            }
          }
        }
      }
    }
  },
  "server-2": {
    "applications": {
      "sample-app-2": {
        "path": "sample-app-2",
        "expected-files": ["file-a.ext-a", "file-b.ext-b", "file-c.ext-a"],
        "folder-1": {
          "path": "sample-app-2/folder-1",
          "folder-1-1": {
            "path": "sample-app-2/folder-1-1/folder-2",
            "expected-files": ["file-1.ext-1", "file-2.ext-1", "file-3.ext-2"],
            "folder-1-1-1": {
              "path": "sample-app-2/folder-1/folder-1-1/folder-1-1-1",
              "expected-file-extensions": [".ext-z"]
            }
          }
        }
      }
    }
  }
}
```

This file can be expanded/contracted as the user sees fit.

Some quick notes on the keys used in the file:
* **path**: This helps the script easily know which path it is currently operating on.
* **expected-files**: The script will compare the actual files obtained from the server with the list of files under this json key and output the result.
* **expected-file-extensions**: When the script sees this key, it means the user wants a particular folder checked for files but does not have an exact list of files to check against. The script will use this key to make sure the folder contains the specified file extension(s); it will also output the number of files containing each extension.

#### app_backups.json

The structure of this file is as follows:

```json
{
  "server-1": {
    "sample-app-1": {
      "backup-folders": [
        "location/to/backup/folder",
        "location-1/to-1/backup-1/folder-1"
      ]
    }
  },
  "server-2": {
    "sample-app-2": {
      "backup-folders": [
        "location/to/backup/folder"
      ]
    }
  }
}
```

The script will go over the backup locations for each specified application and display the size of today's and yesterday's backup sizes.

The size output is: (bytes, normalized_size). For example, a file/folder size of 1024 bytes will be displayed as (1024, 1.0K).

## App Server Checks

The script(s) for backup checks is(are) housed inside `scripts/app_servers`.

### Credentials

For the script to establish a SSH connection, we forward the host system's SSH agent to the docker container. The only needed parameters to pass are the following:
* **host**
* **user**

### server_process_check.py

This script is responsible for logging docker containers which have quit unexpectedly (i.e., those with a non-zero exit code). An example output is:
```
* (container-name-1, image-name-1, command-1, status-1)
* (container-name-2, image-name-2, command-2, status-2)
```

In order to specify what servers and apps to consider, the user can write this information in *json* files inside `file_structure/app_servers`.

#### servers.json

The structure of this file is as follows:

```json
{
  "server-1": {
    "host": "server-1.abc.xyz",
    "user": "user",
    "applications": {
      "app-1": {
        "path": "/data/app-1/"
      },
      "app-2": {
        "path": "/data/app-2/"
      },
      "app-3": {
        "path": "/data/app-3/"
      },
      "app-4": {
        "path": "/data/app-4/"
      },
      "app-5": {
        "path": "/data/app-5/"
      }
    }
  },
  "server-2": {
    "host": "server-2.abc.xyz",
    "user": "user",
    "applications": {
      "app-1": {
        "path": "/data/app-1/"
      }
    }
  },
  "server-3": {
    "host": "server-3.abc.xyz",
    "user": "user",
    "applications": {
      "app-1": {
        "path": "/data/app-1/"
      }
    }
  }
}
```

Some quick notes on the keys used in the file:
* **host**: The host name of the remove server.
* **user**: The username used to log into the server.
* **path**: This helps the script easily know which path it is currently operating on.

### server_file_and_folder_check.py

Similar to `backup_check.py`, this script will compare the live list of files/folders on a remote server with a list of expected files/folders, and report mismatches (if any exist).

In order to specify what servers and apps to consider, the user can write this information in `app_server_content.json` inside `file_structure/app_servers`.

#### app_server_content.json

The config structure here is similar to the one from `app_backup_server_content.json` with the added **"host** and **"user"** keys used to establish the SSH connection.

```json
{
  "server-1": {
    "host": "server-1.abc.xyz",
    "user": "user",
    "applications": {
      "sample-app-1": {
        "path": "sample-app-1",
        "expected-files": ["file-a.ext-a", "file-b.ext-b", "file-c.ext-a"],
        "folder-1": {
          "path": "sample-app-1/folder-1",
          "folder-1-1": {
            "path": "sample-app-1/folder-1/folder-1-1"
          }
        },
        "folder-2": {
          "path": "sample-app-1/folder-2",
          "folder-2-1": {
            "path": "sample-app-1/folder-2/folder-2-1",
            "expected-files": ["file-1.ext-1", "file-2.ext-1", "file-3.ext-2"],
            "folder-2-1-1": {
              "path": "sample-app-1/folder-2/folder-2-1/folder-2-1-1",
              "expected-file-extensions": [".ext-x"]
            },
            "folder-2-1-2": {
              "path": "sample-app-1/folder-2/folder-2-1/folder-2-1-2"
            },
            "folder-2-1-3": {
              "path": "sample-app-1/folder-2/dfolder-2-1/folder-2-1-3"
            }
          },
          "folder-2-2": {
            "path": "sample-app-1/folder-2/folder-2-2",
            "expected-files": ["file-1.ext-1", "file-2.ext-1", "file-3.ext-2"],
            "folder-2-2-1": {
              "path": "sample-app-1/folder-2/folder-2-2/folder-2-2-1",
              "expected-file-extensions": [".ext-y"]
            },
            "folder-2-2-2": {
              "path": "sample-app-1/folder-2/folder-2-2/folder-2-2-2"
            }
          }
        }
      }
    }
  },
  "server-2": {
    "host": "server-2.abc.xyz",
    "user": "user",
    "applications": {
      "sample-app-2": {
        "path": "sample-app-2",
        "expected-files": ["file-a.ext-a", "file-b.ext-b", "file-c.ext-a"],
        "folder-1": {
          "path": "sample-app-2/folder-1",
          "folder-1-1": {
            "path": "sample-app-2/folder-1-1/folder-2",
            "expected-files": ["file-1.ext-1", "file-2.ext-1", "file-3.ext-2"],
            "folder-1-1-1": {
              "path": "sample-app-2/folder-1/folder-1-1/folder-1-1-1",
              "expected-file-extensions": [".ext-z"]
            }
          }
        }
      }
    }
  }
}
```

### server_docker_compose_config_check.py

This script checks for the absence of the following: [**"restart”**, **“logging”**, **“label”**]. This list can be modified in the future as the user sees fit.

In order to specify what servers and apps to consider, the user can write this information in `app_server_docker_config_keys.json` inside `file_structure/app_servers`.

####

The structure of this file is as follows:

```json
{
  "server-1": {
    "host": "server-1.abc.xyz",
    "user": "user",
    "applications": {
      "app-1": {
        "docker-compose-configs": [
          "/path/to/docker-compose.yml",
          "/path/to/docker-compose.override.yml"
        ]
      },
      "app-2": {
        "docker-compose-configs": [
          "/path/to/docker-compose.yml"
        ]
      }
    }
  },
  "server-2": {
    "host": "server-2.abc.xyz",
    "user": "user",
    "applications": {
      "app-1": {
        "docker-compose-configs": [
          "/path/to/docker-compose.yml"
        ]
      }
    }
  }
}
```

Some quick notes on the keys used in the file:
* **host**: The host name of the remove server.
* **user**: The username used to log into the server.
* **docker-compose-configs**: This contains the path(s) to the docker compose config file(s) the script needs to parse.

## How to run

### Using Docker

The base image used for this project at the moment is `python:3.12`.

#### Build the image

Run this command inside the repo folder (`sanity-scripts/`).

```sh
docker build --no-cache -t sanity-scripts .
```

#### Run the container

Run this command inside the repo folder (`sanity-scripts/`).

```sh
docker run -it --rm -v $SSH_AUTH_SOCK:/ssh-agent -e SSH_AUTH_SOCK=/ssh-agent -v ./.env/:/app/.env/ -v ./file_structure:/app/file_structure/ sanity-scripts:latest
```

> NOTE: `$SSH_AUTH_SOCK:/ssh-agent` is mounted as a volume to pass the SSH agent from the host system to the docker container to allow for connections to remote servers.

> NOTE: `./.env/:/app/.env/` and `./file_structure:/app/file_structure/` are passed as volumes to the container as they contain sensitive data and must not be part of the docker build step.

### Using a virtual environment

Running the code through a virtual environment allows for a faster develop-test-debug route. There are multiple tools for this job:
* [venv](https://docs.python.org/3/library/venv.html)
* [pipenv](https://pipenv.pypa.io/en/latest/)
* [uv](https://github.com/astral-sh/uv)

After installing your virtual environment tool, make sure to create and activate the virtual environment (according to your tool's docs). Once the environment is activated, run the following command to install the needed packages:
* `pip install -r requirements.txt`

In case you are using [uv](https://github.com/astral-sh/uv), you need to run the following:
* `uv pip install -r requirements.txt`
