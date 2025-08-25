import os
from dotenv import load_dotenv

from ui import build_interface


def main():
    load_dotenv()
    demo = build_interface()
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")))


if __name__ == "__main__":
    main()