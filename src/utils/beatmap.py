import requests


class Beatmap:

    def __init__(self, content):
        self.content = content

    def save(self, path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.content.decode('utf-8'))

    @classmethod
    def download(cls, bmap_id):
        url = f'https://osu.ppy.sh/osu/{bmap_id}'
        with requests.get(url) as r:
            return cls(r.content)
