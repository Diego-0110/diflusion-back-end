# DiFLUsion Back-End

## Introduction

## Local deployment (for development)

### Environment Variables

Create a file with name `.env` in the root of the project folder and set the next variables (change `<...>` with the value):
```ini
# control
CONTROL_LOG_PATH=<path-to-folder>
# Input and output files (formatter) paths
INPUT_PATH=<path-to-folder>
OUTPUT_PATH=<path-to-folder>
# formatter
FORMATTER_HOST=127.0.0.1
FORMATTER_CTRL_PORT=60001
FORMATTER_LOG_PORT=60002
FORMATTER_LOG_PATH=<path-to-folder>
# daemon
DAEMON_HOST=127.0.0.1
DAEMON_CTRL_PORT=60011
DAEMON_LOG_PORT=60012
DAEMON_LOG_PATH=<path-to-folder>
# model
MODEL_HOST=127.0.0.1
MODEL_CTRL_PORT=60021
MODEL_LOG_PORT=60022
MODEL_LOG_PATH=<path-to-folder>
MODEL_PREDS_PATH=<path-to-folder>
# databases
MODEL_DB_URL=mongodb://localhost:27017
MODEL_DB_NAME=diflusionMDB
WEB_DB_URL=mongodb://localhost:27017
WEB_DB_NAME=diflusionWDB
HISTORY_DB_URL=mongodb://localhost:27017
HISTORY_DB_NAME=diflusionHDB
# TuTiempo API
WEATHER_API_KEY=<API-key>
```
> Note: in the file above some variables has defined values (likes the hosts and ports), but this also can be modified

### Dependecies

The next libraries are required to be installed:
- pandas
- python-dotenv
- loguru
- openpyxl
- pymongo
- requests
- schema

### Installation for development

```
pip install pandas
pip install python-dotenv
pip install loguru
pip install openpyxl
pip install pymongo
pip install requests
pip install schema
```
or
```
pip install -r requirements.txt
```

### Run

```
python ./control/main.py
python ./formatter/main.py
python ./daemon/main.py
python ./model/main.py
```
Note: run each command in a different terminal

## Deployment with Docker Compose

### Images

```
docker pull python:3.12.3-alpine3.18
docker pull mongodb/mongodb-community-server:6.0-ubi8
```

### Deployment

```
docker compose --env-file .\compose.env up -d
```

To undo the delployment:
```
docker compose down
```

### Common tasks

Access to 'control' terminal:
```
docker attach <control-container-name>
# Exit with Ctrl+P and Ctrl+Q
```
> Note: use `docker ps` to obtain the name
> Note: do the same if you want to access to 'model', 'formatter' or 'daemon'

Consult mongo database:
```
docker exec -it <mongodb-container-name> bash
mongosh -u <username> -p <password>
```

Dump whole database:
```
docker exec -i <mongodb-container-name> /usr/bin/mongodump --uri mongodb://<username>:<password>@mongodb --gzip --archive > <path>/mongodb.tar.gz
```

Restore whole database:
```
docker exec -i <mongodb-container-name> /usr/bin/mongorestore --uri mongodb://<username>:<password>@mongodb --gzip --archive < <path>/mongodb.tar.gz
```

Restore specific collection:
```
mongorestore --db=diflusionMDB --collection=weather --uri=mongodb://user:pass@mongodb /data/db/dumpm/diflusionMDB/weather.bson
```

Restore from JSON:
```
docker cp ~/Downloads/dump <container_name>:/dump
```
```
docker exec -i diflusion-back-end-mongodb-1 /usr/bin/mongoimport --authenticationDatabase=admin --db=diflusionMDB --collection=weather --uri=mongodb://user:pass@mongodb --jsonArray --file=/data/db/dumpm/diflusionMDB/diflusionMDB.weather.json
```
> Note: `--authenticationDatabase=admin` is required to avoid errors (`mongodump` and `mongorestore` by default set this to `admin`, but `mongoimport` may not set it)

## Usage guide

### Shared commands

- `conn`:
- `log-mode`:
- `quit`:

### Control's commands

- `send`:
- `cron`:
- `log`:

### Formatter's commands

- `format`:

### Daemon's commands

- `update`:

### Model's commands

- `predict`:
