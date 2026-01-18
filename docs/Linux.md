# Linux installation guide

## :whale: Docker

You need to have Docker installed in order to execute PROTzilla. On Linux, you have the choice of downloading [Docker Desktop](https://docs.docker.com/desktop/setup/install/linux/) which comes with a GUI or just the [Docker Engine](https://docs.docker.com/engine/install/) CLI tool. Follow the installation steps before continuing here.

## Download PROTzilla

You can either use `git` (if available) to clone the repository (this makes retrieving updates much easier), or download an archive of the current state of the codebase.

### Using `git`

#### Prerequisite: Installing `git`

Most non-minimal linux distros already have git installed. You can check if it's installed by running `git --version` in your terminal emulator. If it can't be found, follow the instructions [here](https://git-scm.com/install/linux)

#### Cloning the repository

1. Open your terminal emulator and `cd` into your desired destination directory for PROTzilla (cloning will create a new directory)
2. Enter `git clone https://github.com/cschlaffner/PROTzilla.git`

Voila! There should be a new directory named PROTzilla.

### Downloading the zip

If you only wish to download the current state of the repository, you don't need to have `git` installed. You can just navigate to [the repo page](https://github.com/cschlaffner/PROTzilla) and click on the green "<> Code" button. Here, select "Download ZIP" from the bottom of the dropdown and unpack the archive to a location of your choosing.

## Configuring PROTzilla (optional)

If you'd like to tweak some settings, you can edit the [compose file](compose.yml). For instance, by default the workflow and run data isn't saved outside of the Docker container. You can still export/import them, but after stopping the service and removing the container, all user uploads would be gone.
They can be persisted by editing this section (find the `prod` section of `services`, should be the first):

```yaml
    # volumes:
    # Use this if you want to persistently store user data
    # - '/home/www/.protzilla/user_data:./home/prot/zilla/backend/user_data'
```

Uncomment the relevant parts and set the directory at which to save the user data (for instance at `./backend/user_data`, which would be inside the repo directory) and insert it before the colon to look like this:

```yaml
    volumes:
    # Use this if you want to persistently store user data
    - './backend/user_data:./home/prot/zilla/backend/user_data'
```

This specifies that the local directory `./backend/user_data` should be mounted at `./home/prot/zilla/backend/user_data` inside the docker container (where the software expects them to be).

## Running PROTzilla

Once you have completed the installation steps, you can open a command shell in the PROTzilla directory (or use the one from the cloning step if you didn't close it) and run `docker compose up -d prod`. This will prepare everything and start the service. Once the command has finished, you can navigate to [localhost:8000](http://localhost:8000) and use PROTzilla!
Note that on Linux, Docker Desktop and Docker Engine use separate contexts by default, so you won't see containers started from the CLI in Docker Desktop in case you installed it. This is explained in the "Docker Desktop vs. Docker Engine: What's the difference?" section on the installation page.

## Stopping PROTzilla

If you're done with the service, you can click on the stop symbol (:stop-button:) next to the PROTzilla service in Docker Desktop (if installed) or run `docker compose down` from a terminal emulator in the code directory.
Note that all runs will be gone, should you remove the container (the trash can button in Docker Desktop)