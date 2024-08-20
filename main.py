import os
import smtplib
import subprocess
import sys
from email.message import EmailMessage

import whisper
from dotenv import load_dotenv


# https://github.com/theskumar/python-dotenv/issues/259
def get_root_dir() -> str:
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.getcwd()


load_dotenv(dotenv_path=os.path.join(get_root_dir(), ".env"))


def send_email(to_address: str, attachment_path: str) -> None:
    msg = EmailMessage()
    msg["From"] = os.getenv("SENDER_ADDRESS")
    msg["To"] = to_address
    msg["Cc"] = os.getenv("CC_ADDRESS")
    msg["Subject"] = "【自動送信】文字起こしが完了しました"
    msg.set_content(
        "文字起こしが完了しました！ 結果を添付します。\n\nPCにテキストファイルと音声データが残っているので適宜お片付けください。"
    )

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


def dictate(src_path: str, model: str, mail_address: str) -> None:
    out_basename = os.path.splitext(os.path.basename(src_path))[0]
    out_path = os.path.join(os.path.dirname(src_path), out_basename + ".txt")

    # https://qiita.com/halhorn/items/d2672eee452ba5eb6241
    ai_model = whisper.load_model(model, device="cpu")
    _ = ai_model.half()
    _ = ai_model.cpu()
    for m in ai_model.modules():
        if isinstance(m, whisper.model.LayerNorm):
            m.float()

    result = ai_model.transcribe(
        src_path,
        verbose=True,
        language="japanese",
        fp16=False,
        word_timestamps=True,
    )

    lines = []
    for segment in result["segments"]:
        lines.append(segment["text"])
    result_str = os.linesep.join(lines)
    with open(out_path, mode="w", encoding="utf-8") as f:
        f.write(result_str)

    if 0 < len(mail_address):
        send_email(
            mail_address,
            out_path
        )

    print("===== FINISED! =====")


def test_ffmpeg() -> bool:
    try:
        subprocess.run(
            ["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True
    except:
        return False


def main(args) -> None:
    if not test_ffmpeg():
        print("ffmpeg not found on this pc.")
        return
    try:
        assert 2 < len(args), "specify at least target file path and mode"
        src = args[1]
        model = args[2]
        models = ["base", "small", "medium", "large"]
        assert model in models, "model should be one of {}".format(
            ", ".join(["'" + m + "'" for m in models])
        )
        if 3 < len(args):
            address = args[3]
        else:
            address = ""
        dictate(src, model, address)
    except AssertionError as err:
        print("ERROR: {}\n".format(err))
        return


if __name__ == "__main__":
    main(sys.argv)
