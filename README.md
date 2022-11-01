# Secrete asynchronous chat

The project scripts can work with TCP chat.

## Prerequisites

Python 3.10 is required.

## Installing

- Download the project files
- Set up packages:

```bash
pip install -r requirements.txt
```

- Set up environmental variables in your operating system or in .env file. The variables are:
  - `DEBUG_MODE` is used to output logs, False by default;
  - `CHAT_HOST` is a hostname, `minechat.dvmn.org` by default
  - `LISTEN_PORT` is a port to listen the chat, 5000 by default
  - `LISTEN_FILE` is a file path to write down the chat history
  - `SEND_PORT` is a port to send a message or authorization data, 5000 by default
  - `TOKEN_PATH` is a file path to your authorization token

To set up variables in .env file, create it in the root directory of the project and fill it up like this:

```bash
CHAT_HOST=minechat.dvmn.org
LISTEN_PORT=5000
LISTEN_FILE=history.txt
SEND_PORT=5050
TOKEN_PATH=token.json
DEBUG_MODE=true
```

## Using scripts

### Script "listen-minechat"

- The script can write the chat history to a file;

- Run:

```bash
python listen-minechat.py
```

- You can specify debug mode, host, port, history file path, e.g.:

```bash
python listen-minechat.py --debug_mode --host minechat.dvmn.org --port 5000 --file_path chat_history.txt
```

- To find out more, run:

```bash
python listen-minechat.py -h
```

### Script "register"

- The script can register a new chat user. It creates a *.json file with a token.
- Run:

```bash
python register.py --nickname my_best_name
```

- You can specify debug mode, host, port, token path, e.g.:

```bash
python register.py --nickname my_best_name --debug_mode --host minechat.dvmn.org --port 5050 --token_path my_token.json
```

- To find out more, run:

```bash
python register.py -h
```

### Script "send-minechat"

- The script can send a message to the chat. It uses a *.json file with a token (see [Script "register"](#script-register))
- Run:

```bash
python send-minechat.py --message 'Hello, everybody!'
```

- You can specify debug mode, host, port, token path, e.g.:

```bash
python send-minechat.py --message 'Hello, everybody!' --debug_mode --host minechat.dvmn.org --port 5050 --token_path my_token.json
```

- To find out more, run:

```bash
python send-minechat.py -h
```

## Project goals

The project was created for educational purposes.
It's a lesson for python and web developers at [Devman](https://dvmn.org)
