import os
import requests
import json


class MetaClass:
    def __init__(self):
        return

    def load(self, j):
        self.__dict__ = json.loads(j)

    def save(self, save_path):
        with open(save_path, 'w') as f:
            json.dump(self.__dict__, f, indent=2)


class ScoreMeta(MetaClass):
    def __init__(self, j):
        super().__init__()
        self.__dict__ = j
        return

    @classmethod
    def top_n_from_api(cls, bmap_id, limit=50):
        params = {'k': os.environ['API_KEY'], 'b': bmap_id, 'limit': limit}
        with requests.get(f'https://osu.ppy.sh/api/get_scores', params=params) as r:
            return [cls(j) for j in r.json()]

    @classmethod
    def from_api(cls, score_id):
        params = {'k': os.environ['API_KEY'], 's': score_id, }
        with requests.get(f'https://osu.ppy.sh/api/get_scores', params=params) as r:
            cls(r.json())

    @classmethod
    def from_path(cls, path):
        with open(path, 'r', encoding='utf-8') as f:
            return cls(json.load(f))


class BeatmapMeta(MetaClass):
    def __init__(self):
        super().__init__()
        return

    def get_from_api(self, bmap_id):
        params = {'k': os.environ['API_KEY'], 'b': bmap_id}
        with requests.get(f'https://osu.ppy.sh/api/get_beatmaps', params=params) as r:
            self.__dict__ = r.json()[0]

        return
