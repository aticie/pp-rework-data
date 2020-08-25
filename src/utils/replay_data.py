import os
import lzma
import requests
import base64
from typing import Union

from utils.math_utils import Vec2
from utils.metadata import ScoreMeta


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


class ReplayFrameWithAbsTime:
    def __init__(self, rel_time: int, abs_time: int, mouse_pos: Vec2, key_state: ReplayKeyState):
        self.rel_time = rel_time
        self.abs_time = abs_time
        self.mouse_pos = mouse_pos
        self.key_state = key_state


class Replay:

    def __init__(self):
        self.raw_data = None
        self.frames = []
        return

    def get_from_api(self, score_id: Union[str, int]):
        params = {'k': os.environ['API_KEY'], 's': score_id}
        while True:
            with requests.get('https://osu.ppy.sh/api/get_replay', params=params) as r:
                if r.status_code == 429:
                    continue
                else:
                    raw_lzma_b64 = r.json()['content']
                    break

        raw_lzma = base64.b64decode(raw_lzma_b64)
        self.raw_data = lzma.decompress(raw_lzma).decode()
        self.parse_frames()

    def parse_frames(self):
        offset = int(self.raw_data.split(',')[1].split("|")[0]) + int(self.raw_data.split(',')[0].split("|")[0])
        abs_time = offset
        for line in self.raw_data.split(',')[2:-2]:
            frame_parts = line.split('|')
            time = int(frame_parts[0])
            abs_time += time
            self.frames.append(ReplayFrame(line))


class ScoreWithReplay:
    def __init__(self, score_meta: ScoreMeta, replay_data: Replay):
        self.score = score_meta
        self.replay = replay_data
