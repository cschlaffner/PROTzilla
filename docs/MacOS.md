# Mac installation guide

## :whale: Docker

You need to have Docker installed in order to execute PROTzilla. On MacOS, this means downloading [Docker Desktop](https://docs.docker.com/desktop/setup/install/mac-install/) and running it before executing the next steps.

## Download PROTzilla

You can either use `git` (if available) to clone the repository (this makes retrieving updates much easier), or download an archive of the current state of the codebase.

### Using `git`

#### Prerequisite: Installing `git`

If you don't have `git` installed, you can find the instructions [here](https://git-scm.com/install/mac).

#### Cloning the repository

1. Navigate to the directory you would like to download PROTzilla to in the Finder
2. Open a terminal by right-clicking the directory name while holding down control (compare [here](https://discussions.apple.com/thread/256112405?sortBy=rank)) and selecting "Open in Terminal here"
3. Enter `git clone https://github.com/cschlaffner/PROTzilla.git`

After the last command has finished, you should see a new directory named "PROTzilla" in the Finder.

### Downloading the zip

If you only wish to download the current state of the repository, you don't need to have `git` installed. You can just navigate to [the repo page](https://github.com/cschlaffner/PROTzilla) and click on the green "<> Code" button. Here, select "Download ZIP" from the bottom of the dropdown and unpack the archive to a location of your choosing.

## Configuring PROTzilla (optional)

If you'd like to tweak some settings, you can edit the [compose file](compose.yml). For instance, by default the workflow and run data isn't saved outside of the Docker container. You can still export/import them, but after stopping the service and removing the container, all user uploads would be gone.
They can be made persistent by editing this section (find the `prod` section of `services`, should be the first):

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

Before executing Docker commands on Mac, you need to start Docker Desktop (otherwise, Docker commands will fail) (@mac users, is this true?).
Afterwards, you can open the Terminal app in the PROTzilla directory (or use the one from the cloning step if you didn't close it) and run `docker compose up -d prod`. This will prepare everything and start the service. Once the command has finished, you can navigate to [localhost:8000](http://localhost:8000) and use PROTzilla!
You should also see the container in Docker Desktop, where you can access logs or attach to a shell inside the container.

## Stopping PROTzilla

If you're done with the service, you can either click on the stop symbol (:stop-button:) next to the PROTzilla service in Docker Desktop or run `docker compose down` from a command prompt in the code directory.
Note that all runs will be gone, should you remove the container (the trash can button in Docker Desktop)