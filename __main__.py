#!/usr/bin/env python3

"""
auth.json pattern
{
    "api_id": "",
    "api_hash": ""
}
"""

import json
from sys import argv, stderr
from os import path

from telethon.sync import TelegramClient
from telethon.tl.types import InputMessagesFilterMusic, DocumentAttributeFilename
from tqdm import tqdm


AUTH_DATA_FILE_ADDR = "auth.json"
SESSION_NAME = "music-downloader"
DOWNLOAD_ADDR = "music"


def read_auth_data():
    with open(AUTH_DATA_FILE_ADDR) as f:
        auth_data = json.load(f)
    return auth_data["api_id"], auth_data["api_hash"]


def main():
    if len(argv) not in {2, 3}:
        print("usage:\t%s <chat_id> [<min_id>]", file=stderr)
        exit(2)
    chat_id = argv[1]
    min_id = int(argv[2]) if len(argv) > 2 else None

    config = {}
    if min_id:
        config["min_id"] = min_id

    with TelegramClient(SESSION_NAME, *read_auth_data()) as client:
        me = client.get_me().username
        print("Logged in as %s" % me, flush=True)
        
        for msg in tqdm(client.iter_messages(chat_id, filter=InputMessagesFilterMusic, **config)):
            file_name = None
            for attribute in msg.media.document.attributes:
                if isinstance(attribute, DocumentAttributeFilename):
                    file_name = attribute.file_name
            if not file_name:
                print("File name not found ans skipped: %s" % msg, file=stderr)
                continue

            print("downloading (%s) [%s %s %s] (%s) %s" % (
                msg.id,
                "@%s" % me, "->" if msg.out else "<-", chat_id,
                msg.date,
                file_name,
            ), flush=True)

            addr = msg.download_media(file=path.join(DOWNLOAD_ADDR, file_name))
            print("downloaded %s" % addr, flush=True)


if __name__ == '__main__':
    main()
