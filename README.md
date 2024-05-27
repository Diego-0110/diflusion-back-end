# DiFLUsion Back-End

## Introduction

This is the 'back-end' part of the DiFlusion application for predicting risks of avian influenza outbreaks in Spain.

## Local deployment (for development)

### Environment Variables

Create a file with name `.env` in the root of the project folder and set the next variables (change `<...>` with the value):
```ini
# control
CONTROL_LOG_PATH=<path-to-folder>/logs/control
# Input and output files (formatter) paths
INPUT_PATH=<path-to-folder>/data/input
OUTPUT_PATH=<path-to-folder>/data/formatted
# formatter
FORMATTER_HOST=127.0.0.1
FORMATTER_CTRL_PORT=60001
FORMATTER_LOG_PORT=60002
FORMATTER_LOG_PATH=<path-to-folder>/logs/formatter
# daemon
DAEMON_HOST=127.0.0.1
DAEMON_CTRL_PORT=60011
DAEMON_LOG_PORT=60012
DAEMON_LOG_PATH=<path-to-folder>/logs/daemon
# model
MODEL_HOST=127.0.0.1
MODEL_CTRL_PORT=60021
MODEL_LOG_PORT=60022
MODEL_LOG_PATH=<path-to-folder>/logs/model
MODEL_PREDS_PATH=<path-to-folder>/predictions
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
> Note: in the file above some variables has defined values (likes the hosts and ports), but every variable can have the value you consider.

> Note: if you want to use MongoDB locally you can download [MongoDB Compass](https://www.mongodb.com/products/tools/compass).

If you want to use the same file structure as the file above shows, create the next folder tree:

`<path-to-folder>/`
- `data/`
    - `input/`
    - `formatted/`
- `logs/`
    - `control/`
    - `daemon/`
    - `formatter/`
    - `model/`
- `predictions/`

### Dependecies

The next libraries are required to be installed:
- pandas
- python-dotenv
- loguru
- openpyxl
- pymongo
- requests
- schema
- pycountry

### Installation for development

```
pip install pandas
pip install python-dotenv
pip install loguru
pip install openpyxl
pip install pymongo
pip install requests
pip install schema
pip install pycountry
```
or
```
pip install -r requirements.txt
```

### Run

Before running the application you have to copy all files inside `_common/` folder to `control/`, `daemon/`, `formatter/` and `model/`. You can do this using `script.sh` or copying manually with `cp`.

> Note: in Windows you may have problems with the 'end of line' characters when you try to run `./script.sh` in WSL.

After that you can run the next commands:

```
python ./control/main.py
python ./formatter/main.py
python ./daemon/main.py
python ./model/main.py
```
> Note: run each command in a different terminal

## Deployment with Docker Compose

For deployment with Docker Compose there's a YML file in the root of the project folder: `compose.yml`. This YML file include the container for the web app (https://github.com/Diego-0110/diflusion-web) so you should have a copy of that repository or remove the declaration of the container `web` in `compose.yml`. 

### Environment variables

To set environment variables we need two files, one for variables to use inside `compose.yml` (`compose.env`) and other for variables to use in the containers (`production.env`).

Create a file called `compose.env` in the root of the project and set the next variables:

```ini
# Path where logs, predictions, dumps and data will be saved in the local computer (share volumes with containers)
LOCAL_PATH=<path-to-folder>
# Path where the project diflusion-web is allocated
WEB_PATH=<path-to-web-folder>
# Database user and password
DB_USER=user
DB_PASSWORD=pass
```

Create a file called `production.env` in the root of the project and set the next variables:

```ini
# control
CONTROL_LOG_PATH=/control/logs # compose.yml volumes
# files paths
INPUT_PATH=/diflusion/data/input # compose.yml volumes
OUTPUT_PATH=/diflusion/data/formatted # compose.yml volumes
# formatter
FORMATTER_HOST=formatter # compose.yml
FORMATTER_CTRL_PORT=60001
FORMATTER_LOG_PORT=60002
FORMATTER_LOG_PATH=/formatter/logs # compose.yml volumes
# daemon
DAEMON_HOST=daemon # compose.yml
DAEMON_CTRL_PORT=60011
DAEMON_LOG_PORT=60012
DAEMON_LOG_PATH=/daemon/logs # compose.yml volumes
# model
MODEL_HOST=model # compose.yml
MODEL_CTRL_PORT=60021
MODEL_LOG_PORT=60022
MODEL_PREDS_PATH=/model/predictions # compose.yml volumes
MODEL_LOG_PATH=/model/logs # compose.yml volumes
# databases
MODEL_DB_URL=mongodb://<user>:<password>@mongodb
MODEL_DB_NAME=diflusionMDB
WEB_DB_URL=mongodb://<user>:<password>@mongodb
WEB_DB_NAME=diflusionWDB
HISTORY_DB_URL=mongodb://<user>:<password>@mongodb
HISTORY_DB_NAME=diflusionHDB
# API keys
WEATHER_API_KEY=<API-key> # TuTiempo API key
# Timezone
TZ=Europe/Madrid # Example
```
> Note: all values can be changed but some of them should be change also in `compose.yml`.

> Note: the URL to database should be consistent with the `DB_USER` and `DB_PASSWORD` variables from `compose.env` file. For example: if `DB_USER=user` and `DB_PASSWORD=pass`, then `MODEL_DB_URL=mongodb://user:pass@mongodb` and `WEB_DB_URL` and `HISTORY_DB_URL` too.

### Images

```
docker pull python:3.12.3-alpine3.18
docker pull mongodb/mongodb-community-server:6.0-ubi8
docker pull node:18-alpine
```

### Deployment

With the environment variables set in `compose.env` and `production.env` files and a copy of the 'diflusion-web' repository, you can deploy the whole application with the next command:

```
docker compose --env-file .\compose.env up -d
```

In case you want to undo the deployment:
```
docker compose down
```

### Common tasks

#### Access to 'control' module's terminal or any module

To Access to a terminal of a certain module and interact with the CLI ('control', 'daemon', ...) use:

```
docker attach <container-name>
# Exit with Ctrl+P + Ctrl+Q
```

> Note: use `docker ps` to obtain the name

#### Consult mongo database

To consult the database using `mongosh` enter the next commands:

```
docker exec -it <mongodb-container-name> bash
mongosh -u <username> -p <password>
```

With this you can see all databases (`show dbs`), access to a database (`use <database-name>`), get collections from a database (`show collections`), search for documents (`db.coll.find({...})`), ... See: https://www.mongodb.com/developer/products/mongodb/cheat-sheet/

#### Dump the whole database

Dump the whole database in the share volume:

```
docker exec -it <mongodb-container-name> /usr/bin/mongodump --uri=mongodb://<username>:<password>@mongodb --gzip --archive=/dump/mongodb.tar.gz
```

Dump the whole database in a local path:

```
docker exec -i <mongodb-container-name> /usr/bin/mongodump --uri=mongodb://<username>:<password>@mongodb --gzip --archive > <path>/mongodb.tar.gz
```

#### Restore the whole database

Restore the whole database from a file in the share volume:

```
docker exec -i <mongodb-container-name> /usr/bin/mongorestore --uri=mongodb://<username>:<password>@mongodb --gzip --archive=/dump/mongodb.tar.gz
```

Restore the whole database from a local file:

```
docker exec -i <mongodb-container-name> /usr/bin/mongorestore --uri=mongodb://<username>:<password>@mongodb --gzip --archive < <path>/mongodb.tar.gz
```

#### Restore specific a collection
```
mongorestore --db=diflusionMDB --collection=weather --uri=mongodb://user:pass@mongodb /data/db/dumpm/diflusionMDB/weather.bson
```

#### Restore from JSON
```
docker cp ~/Downloads/dump <container_name>:/dump
```
```
docker exec -i diflusion-back-end-mongodb-1 /usr/bin/mongoimport --authenticationDatabase=admin --db=diflusionMDB --collection=weather --uri=mongodb://user:pass@mongodb --jsonArray --file=/data/db/dumpm/diflusionMDB/diflusionMDB.weather.json
```
> Note: `--authenticationDatabase=admin` is required to avoid errors (`mongodump` and `mongorestore` by default set this to `admin`, but `mongoimport` may not set it)

## Usage guide

Every module ('control', 'daemon', ...) has an interactive CLI (Command Line Interface) where you can run commands.

'control' module by default is in CLI mode, but the rest of the terminals are in log mode. You can escape of log mode entering the letter 'q'.

> Note: you can always resort to `-h` option to get help in the CLI. Examples: `-h` (show available commands and its descriptions), `conn -h` (show usage details of `conn` command).

### Input files

The 'formatter' module read files from `INPUT_PATH`, the next files should exist in `INPUT_PATH`:

- `raw_migrations.xlsx`: file with migrations and birds.
- `raw_outbreaks.xlsx`: file with outbreaks.
- `raw_regions.geojson`: file with regions.
- `weather_stations.xlsx`: file with ubications for weather predictions.

### Shared commands

This commands are shared in all terminals.

- `conn`: given certain connections ids (`-ids <...>`) you can get the status of those connections (`status`) and restart them (`restart`).
    - Examples:
        - `conn status`: show the status of all connections.
        - `conn restart -ids model model_log`: restart the connections 'model' and 'model_log'.
        - `conn restart`: restart all the connections.
- `log-mode`: change to log mode, where you can see all the logs updating in real time (in 'control' module also the logs from other terminals). Exit (return to CLI) entering character 'q'.
- `quit`: exit the module's terminal safely (close connections and running threads).

### Control's commands

Specific commands for 'control' module.

- `send`: send a command (`-cmd`) to a specific module (`-id`). Optionally, you can add `--log-mode` flag to activate log mode right before sending the command.
    - Examples:
        - `send -id formatter --log-mode -cmd format birds`: activates log mode and then send the command `format birds` to 'formatter' module.
- `cron`: executes a command at a certain date and time (`-dtime`). Optionally, you can set `-days` value (>0 and integer) and the command will be executed every x days.
    - Examples:
        - `cron -dtime 01-01-2024-14:00 -days 7`: wait the user to introduce a command to execute it at 14:00 every 7 days since 01-01-2024.

### Formatter's commands

Specific commands for 'formatter' module.

- `format`: format one or more types of data.
    - Examples:
        - `format birds migrations`: format the data 'birds' and 'migrations'.

### Daemon's commands

Specific commands for 'daemon' module.

- `update`: update one or more types of data in the database. Optionally, if you add `--update-duplicates` flag, duplicate data (same id) will be updated.
    - Examples:
        - `update birds --update-duplicates`: update the data 'birds' updating the duplicates.

### Model's commands

Specific commands for 'model' module.

- `predict`: run a predictor for an interval of x days (`-days`: optional and 7 by default) starting from a certain date (`-date`: optional and today date by default). Optionally, you can save prediction in a spreadsheet instead of saving to the database (default) (`--compare-mode` flag) and\or update prediction (`--update` flag) when there's already a prediction in the same date range.
    - Examples:
        - `predict A --compare-mode -days 3`: run the predictor 'A' for and interval of 3 days starting today and save the results in a xlsx file.
