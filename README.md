# README

Run [Whisper](https://github.com/openai/whisper/) on local PC.

## Usage

Require [ffmpeg](https://ffmpeg.org/) .

1. Create `.env` at the same directory as `dictate.py` as below.

    ```
    SENDER_ADDRESS=●●
    CC_ADDRESS=●●
    SENDER_PASSWORD=●●
    SMTP_HOST=●●
    SMTP_PORT=●●
    ```

1. Put `.mp3` files in `.\in` directory.

1. Run:

    ```
    uv run .\dictate.py hogehoge@fuga.net small
    ```

    - Specify the email address to send notifications by the first argument.
    - Specify the model as the second argument, one of `base`, `small`, `medium`, or `large`.
    - Dictation results are save in the `.\out` directory.
