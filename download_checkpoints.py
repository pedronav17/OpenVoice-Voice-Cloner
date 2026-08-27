import hashlib
import os
import urllib.request

CHECKPOINT_DIR = os.path.join("checkpoints_v2", "converter")
CHECKPOINT_PATH = os.path.join(CHECKPOINT_DIR, "checkpoint.pth")
CONFIG_PATH = os.path.join(CHECKPOINT_DIR, "config.json")

CHECKPOINT_URL = (
    "https://huggingface.co/myshell-ai/OpenVoiceV2/"
    "resolve/main/converter/checkpoint.pth"
)

CONFIG_URL = (
    "https://huggingface.co/myshell-ai/OpenVoiceV2/"
    "resolve/main/converter/config.json"
)

EXPECTED_SHA256 = (
    "9652c27e92b6b2a91632590ac9962ef7ae2b712e5c5b7f4c34ec55ee2b37ab9e"
)


def calculate_sha256(path):
    sha256 = hashlib.sha256()

    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(block)

    return sha256.hexdigest()


def download_file(url, destination):
    print(f"[INFO] Descargando: {url}")

    with urllib.request.urlopen(url) as response:
        total = int(response.headers.get("Content-Length", 0))
        downloaded = 0

        with open(destination, "wb") as f:
            while True:
                block = response.read(1024 * 1024)

                if not block:
                    break

                f.write(block)
                downloaded += len(block)

                if total:
                    percent = downloaded * 100 / total
                    print(
                        f"\r[INFO] Progreso: {percent:6.2f}%",
                        end="",
                        flush=True
                    )

    print()


def main():
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    # Checkpoint
    if os.path.isfile(CHECKPOINT_PATH):
        print("[OK] checkpoint.pth ya existe.")

        print("[INFO] Verificando SHA-256...")
        sha256 = calculate_sha256(CHECKPOINT_PATH)

        if sha256 == EXPECTED_SHA256:
            print("[OK] Checkpoint verificado correctamente.")
        else:
            print("[ERROR] El SHA-256 del checkpoint no coincide.")
            print(f"[INFO] SHA-256 encontrado: {sha256}")
            print("[INFO] El archivo será eliminado para volver a descargarlo.")

            os.remove(CHECKPOINT_PATH)

    if not os.path.isfile(CHECKPOINT_PATH):
        download_file(CHECKPOINT_URL, CHECKPOINT_PATH)

        print("[INFO] Verificando SHA-256...")
        sha256 = calculate_sha256(CHECKPOINT_PATH)

        if sha256 != EXPECTED_SHA256:
            print("[ERROR] La descarga no coincide con el SHA-256 esperado.")
            os.remove(CHECKPOINT_PATH)
            raise RuntimeError("Checkpoint corrupto o incorrecto.")

        print("[OK] Checkpoint descargado y verificado correctamente.")

    # Config
    if os.path.isfile(CONFIG_PATH):
        print("[OK] config.json ya existe.")
    else:
        download_file(CONFIG_URL, CONFIG_PATH)
        print("[OK] config.json descargado correctamente.")

    print()
    print("[OK] OpenVoice V2 está preparado.")
    print(f"[INFO] Checkpoint: {CHECKPOINT_PATH}")
    print(f"[INFO] Config:      {CONFIG_PATH}")


if __name__ == "__main__":
    main()
