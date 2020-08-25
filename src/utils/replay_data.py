import os
import lzma
import requests
import base64
from typing import Union

from utils.math_utils import Vec2


class ReplayKeyState:
    def __init__(self, key_dict):
        self.__dict__ = key_dict


class ReplayFrame:
    def __init__(self, raw_frame: str):
        frame_parts = raw_frame.split('|')
        self.time = int(frame_parts[0])
        self.mouse_pos = Vec2(float(frame_parts[1]), float(frame_parts[2]))
        ks = int(frame_parts[3])
        self.key_state = ReplayKeyState({'m1': ks & 1 and not (ks << 2) & 1,
                                         'm2': ((ks << 1) & 1) and not (ks << 3) & 1,
                                         'k1': (ks << 2) & 1,
                                         'k2': (ks << 3) & 1,
                                         'smoke': (ks << 4) & 1})


class Replay:

    def __init__(self):
        self.raw_data = None
        self.frames = None
        return

    def get_from_api(self, score_id: Union[str, int]):
        params = {'k': os.environ['API_KEY'], 's': score_id}
        with requests.get('https://osu.ppy.sh/api/get_replay', params=params) as r:
            raw_lzma_b64 = r.json()['content']
        raw_lzma = base64.b64decode(raw_lzma_b64)
        self.raw_data = lzma.decompress(raw_lzma).decode()
        self.parse_frames()

    def parse_frames(self):
        self.frames = [ReplayFrame(line) for line in self.raw_data.split(',')[:-1]]
