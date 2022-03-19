# Carla Starter Project for version 0.9.13

This project contains a multi-container Carla project template for educational purposes.

## Setup the environment

- Ubuntu 20.04 environment (Ubuntu on WSL may work, not recommended)
- Docker (first [install Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) and then follow [Docker post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/))
- Docker Compose ([install docker-compose](https://docs.docker.com/compose/install/))
- Python 3.8 (comes by default in Ubuntu 20.04)
- Upgrade `pip` to the latest version using `pip install --upgrade pip`
- Install `pygame` and `carla` package using `pip install pygame carla==0.9.13`

## Test drive the container

Once your environment set up, click "Use this template" button to transfer this repo onto your github account and then clone it on your local computer.

Change to the project directory and you will be able to run the (no-3d-rendering) Carla server by executing the command there
```
docker-compose up -d
```
Then run the client script (wait some time if server is still initializing)

```
python3 client/run.py
```

This client code mostly handles the 2D drawing of Carla world and instatiate a Carla agent with the autopilot enabled. 

Then check the code in `client/app/hero.py` where you can modify this behavior. 

Use the following command to stop the server:

```
docker-compose down
```

## Check the documentation of Carla Simulator 

- [Carla Simulator Documentation](https://carla.readthedocs.io/en/0.9.13/)
- [Carla Simulator PythonAPI Reference](https://carla.readthedocs.io/en/0.9.13/python_api/)

## Notes

- This project is configured for 2D rendering of Carla world to allow to work on computers without dedicated graphics cards (still requiring at least 8GB RAM). If you have a decent Nvidia graphics card, then it is possible to use 3D rendering capabilities of the simulator.
