import os
import requests
import json


class MetaClass:
    def __init__(self):
        return

    def load_class(self, j):
        self.__dict__ = json.loads(j)


def get_scores_of_bmap_from_api(bmap_id):
    params = {'k': os.environ['API_KEY'], 'b': bmap_id}
    with requests.get(f'https://osu.ppy.sh/api/get_scores', params=params) as r:
        return [ScoreMeta(j) for j in r.json()]


class ScoreMeta(MetaClass):
    def __init__(self, j):
        super().__init__()
        self.__dict__ = j
        return


class BeatmapMeta(MetaClass):
    def __init__(self):
        super().__init__()
        return

    def get_from_api(self, bmap_id):
        params = {'k': os.environ['API_KEY'], 'b': bmap_id}
        with requests.get(f'https://osu.ppy.sh/api/get_beatmaps', params=params) as r:
            self.__dict__ = r.json()[0]

        return
