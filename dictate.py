import os
import smtplib
import sys
import shutil
from email.message import EmailMessage
from typing import List

import whisper
from dotenv import load_dotenv


load_dotenv(dotenv_path=".env")


def send_email(to_address: str, attachment_path: str, total: int, idx: int) -> None:
    msg = EmailMessage()
    msg["From"] = os.getenv("SENDER_ADDRESS")
    if len(to_address) < 1:
        msg["To"] = os.getenv("CC_ADDRESS")
    else:
        msg["To"] = to_address
    msg["Cc"] = os.getenv("CC_ADDRESS")
    num = idx + 1
    msg["Subject"] = "【自動送信】文字起こしが完了しました（{}/{}）".format(num, total)
    content = "{}件中{}件目の文字起こしが完了しました！ 結果を添付します。\n\n".format(
        total, num
    )
    if num == total:
        content += (
            "PCにテキストファイルと音声データが残っているので適宜処分してください。"
        )
    else:
        content += "引き続き残りのファイルの文字起こしを続けます。"
    msg.set_content(content)

    with open(attachment_path, "rb") as f:
        msg.add_attachment(
            f.read(),
            maintype="text",
            subtype="plain",
            filename=os.path.basename(f.name),
        )

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as smtp:
        smtp.starttls()
        smtp.connect(host=os.getenv("SMTP_HOST"))
        smtp.login(os.getenv("SENDER_ADDRESS"), os.getenv("SENDER_PASSWORD"))
        smtp.send_message(msg)


def dictate(path: str, model: whisper.Whisper) -> str:
    basename = os.path.splitext(os.path.basename(path))[0]
    out_path = os.path.join(os.getcwd(), "out", basename + ".txt")
    result = model.transcribe(
        path,
        verbose=True,
        language="japanese",
        fp16=False,
        word_timestamps=True,
    )

    lines = []
    for segment in result["segments"]:
        lines.append(segment["text"])

    result_str = "\n".join(lines)
    with open(out_path, mode="w", encoding="utf-8") as f:
        f.write(result_str)

    return out_path


def dictate_files(paths: List[str], model: str, mail_address: str) -> None:

    # https://qiita.com/halhorn/items/d2672eee452ba5eb6241
    ai_model = whisper.load_model(model, device="cpu")
    _ = ai_model.half()
    _ = ai_model.cpu()
    for m in ai_model.modules():
        if isinstance(m, whisper.model.LayerNorm):
            m.float()

    for i, path in enumerate(paths):
        out_path = dictate(path, ai_model)
        send_email(mail_address, out_path, len(paths), i)
        print("===== FINISED! =====")


def main(args) -> None:
    if shutil.which("ffmpeg") is None:
        print("ffmpeg not found on this pc.")
        return

    models = ["base", "small", "medium", "large"]
    if len(args) < 3:
        print(
            "Specify mail address to send notification by 1st arg, and specify model by 2nd arg ({}).".format(
                "|".join(models)
            )
        )
        return
    if "@" not in args[1]:
        print("Invalid mail address.")
        return
    if args[2] not in models:
        print("Model should be ({}).".format("|".join(models)))
        return

    address = args[1]
    model = args[2]
    targets = [
        os.path.join(os.getcwd(), "in", f)
        for f in os.listdir("in")
        if f.endswith(".mp3")
    ]
    dictate_files(targets, model, address)


if __name__ == "__main__":
    main(sys.argv)
