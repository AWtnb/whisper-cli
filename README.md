# README

Run [Whisper](https://github.com/openai/whisper/) on local PC.

## Usage

Require [ffmpeg](https://ffmpeg.org/) .

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

Run:

```
uv run .\dictate.py hogehoge@fuga.net small
```
