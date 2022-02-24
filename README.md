# Carla Starter Project for version 0.9.13

This project contains a multi-container Carla project template for educational purposes.

## Setup the environment

- Ubuntu 20.04 environment (Ubuntu on WSL may work, not recommended)
- Docker (first [install Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) and then follow [Docker post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/))
- Docker Compose ([install docker-compose](https://docs.docker.com/compose/install/))
- Python 3.8 (comes by default in Ubuntu 20.04)

## Test drive the container

Once your environment set up, you will be able to run the (no-3d-rendering) Carla server by executing the command in the project directory
```
docker-compose up -d
```
Then run the client script (wait some time if server still initializing)

```
python3 client/run.py
```

This client code mostly handles the 2D drawing of Carla world and instatiate a Carla agent with the autopilot enabled. 

Then check the code in `app/hero.py` where you can modify this behavior. 
