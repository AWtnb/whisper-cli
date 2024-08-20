# README

Run [Whisper](https://github.com/openai/whisper/) on local PC.

## Usage

Require [ffmpeg](https://ffmpeg.org/) .

```
dictate.exe input.mp3 small
```

```
dictate.exe input.mp3 base hogehoge@fuga.net
```

## Build

Create `.env` at the same directory as `main.py`.

```
.\
├─main.py
└─.env
```

`.env` :

```
SENDER_ADDRESS=●●
CC_ADDRESS=●●
SENDER_PASSWORD=●●
SMTP_HOST=●●
SMTP_PORT=●●
```

Create venv:

```
python -m venv .venv
```

Install packages:

```
python -m pip install python-dotenv
python -m pip install openai-whisper
```

Build pyinstaller locally (`.exe` generated with pip-installed pyinstaller is often considered as virus by security soft):

1. `git clone https://github.com/pyinstaller/pyinstaller`
1. `cd .\pyinstaller\bootloader\`
1. `python .\waf all`
    - Build would fail, but it is ignorable.
    - Visual Studio C++ compiler is required for build.
        - It can be installed with [Scoop](https://scoop.sh/) : `scoop install vcredist2015` .
    - In my environment, 2015 and 2022 were installed. If just installing vcredist2015 results in error, try installing the latest version as well.
1. `cd ..` (move to `pyinstaller` directory)
1. `pip install .`
1. Delete `pyinstaller` folder.
    - This folder is used only for package build and no longer used.


### Build `dictate.exe`

1. Enter venv ([skippable on VSCode](https://github.com/microsoft/vscode-python/wiki/Activate-Environments-in-Terminal-Using-Environment-Variables))

    ```
    .\.venv\Scripts\activate
    ```

1. Run:

    ```
    pyinstaller --onefile --name dictate --collect-data whisper --add-data ".env;." .\main.py
    ```

    - If error was raised around pathlib, uninstall it: `python -m pip uninstall pathlib -y`
    - After build, re-install: `python -m pip install pathlib`

1. Exit from venv ([skippable on VSCode](https://github.com/microsoft/vscode-python/wiki/Activate-Environments-in-Terminal-Using-Environment-Variables))

    ```
    deactivate
    ```

