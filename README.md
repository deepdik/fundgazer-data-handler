# Strategy Manager 



## Getting started

To make it easy for you to get started with this project, here's a list of recommended next steps.

## Clone repository in your local system


```
cd your_folder_where_you_want_to_clone_it
git clone <>
git checkout main
```

## Install python 3.x (3.8.10 or above is recommended)

## Create Virtual environment
```
cd datahandler
virtualenv venv
source env/bin/activate
```


## Install dependency
```
pip install -r /path/to/requirements.txt
```

## Create logs directory
```
 - Go to your project root directory and create a "logs" folder for e.g. if you root directory is "goldcircular" then create a folder within this.
```

## Setup .env file

```
 - Go to Console and copy ".env_copy" to ".env" in the same folder
 - cp /path/to/.localenv /path/to/.env
 - Change the value as per your local setup
 - To run the Swagger Document, please change the value of ENV i.e "ENV=DEV"
```

## Start Server
```
 - Go to Console and type below command
 - uvicorn main:app --reload
```

## Open URL in Browser
```
http://localhost:8000/docs
```

## Sample API URL
```
http://localhost:8000/api/v1/hello
```


# Run via Docker

Create a rabbitmq broker
* create via docker
```bash
docker run rabbitmq
```
* create on rabbitmq website
 <br>
 
 ## In any case update the variable `CELERY_BROKER_URL` in file:./config/environ/.env.

To build the docker compose file
```bash
docker compose build
```

Create a docker network
```bash
docker network create <network-name-from-the-docker-compose-file>
```

Run the comtainers
```bash
docker compose up
```

