import json
import re
import sys
import typing


def discover_items(url: str) -> typing.Iterator[str]:
    for pattern, type_ in {
        r'^https?://prcm\.jp/album/([^/\?&;]+/pic/[0-9]+)$': 'pic',
        r'^https?://prcm\.jp/album/([^/\?&;]+)$': 'album',
        r'^https?://prcm\.jp/user/([^/\?&;]+)$': 'user',
        r'^https?://prcm\.jp/list/([^/\?&;]+)$': 'list',
        r'^https?://(prof\.prepics-cdn\.com/.+)$': 'cdn',
        r'^https?://(pics\.prcm\.jp/.+)$': 'cdn',
        r'^https?://(img\.prepics\.com/.+)$': 'cdn',
        r'^https?://prcm\.jp/talk/list/([^/\?&;]+)$': 'talk-list'
    }.items():
        match = re.search(pattern, url.strip(), re.I)
        if match:
            yield type_ + ':' + match.group(1)


def discover_items_from_json(data: dict) -> typing.Iterator[str]:
    if type(data) is list:
        for v in data:
            yield from discover_items_from_json(v)
    elif type(data) is dict:
        for k, v in data.items():
            yield from discover_items_from_json(k)
            yield from discover_items_from_json(v)
    elif type(data) is str:
        yield from discover_items(data)


def main(filename: str):
    items = set()
    with open(filename, 'r') as f:
        print('Processing', f.name)
        for line in f:
            if line.startswith('{'):
                try:
                    data = json.loads('['+line.replace('}{', '},{')+']')
                except Exception:
                    print(line)
                items |= set(discover_items_from_json(data))
            else:
                items |= set(discover_items(line))
    print('Found', len(items), 'items')
    with open(filename+'.items', 'w') as f:
        print('Writing', f.name)
        f.write('\n'.join(items)+'\n')

if __name__ == '__main__':
    for filename in sys.argv[1:]:
        main(filename)

