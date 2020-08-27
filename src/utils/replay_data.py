import os
import lzma
import requests
import base64
from typing import Union

from utils.math_utils import Vec2
from utils.metadata import ScoreMeta


class ReplayKeyState:
    """
    Replay Key State inferred from a key dictionary
    """

    def __init__(self, keys: dict):
        self.__dict__ = keys
        return

    @classmethod
    def from_dict(cls, key_dict):
        return cls(key_dict)


class ReplayFrame:
    """
    A single Replay frame as saved within .osr file
    """

    def __init__(self, raw_frame: str):
        frame_parts = raw_frame.split('|')
        self.time = int(frame_parts[0])
        self.mouse_pos = Vec2(float(frame_parts[1]), float(frame_parts[2]))
        ks = int(frame_parts[3])
        self.key_state = ReplayKeyState.from_dict({'m1': ks & 1 and not (ks << 2) & 1,
                                                   'm2': ((ks << 1) & 1) and not (ks << 3) & 1,
                                                   'k1': (ks << 2) & 1,
                                                   'k2': (ks << 3) & 1,
                                                   'smoke': (ks << 4) & 1})


class ReplayFrameWithAbsTime:
    """
    osu! replay frame with absolute time part added.
    """

    def __init__(self, rel_time: int, abs_time: int, mouse_pos: Vec2, key_state: ReplayKeyState):
        self.rel_time = rel_time
        self.abs_time = abs_time
        self.mouse_pos = mouse_pos
        self.key_state = key_state

    @classmethod
    def from_string(cls, frame_str: str, abs_time: int):
        frame_parts = frame_str.split('|')
        rel_time = int(frame_parts[0])
        mouse_pos = Vec2(float(frame_parts[1]), float(frame_parts[2]))
        ks = int(frame_parts[3])
        key_state = ReplayKeyState.from_dict({'m1': ks & 1 and not (ks << 2) & 1,
                                              'm2': ((ks << 1) & 1) and not (ks << 3) & 1,
                                              'k1': (ks << 2) & 1,
                                              'k2': (ks << 3) & 1,
                                              'smoke': (ks << 4) & 1})

        return cls(rel_time, abs_time, mouse_pos, key_state)


'''
raw_lzma = base64.b64decode(raw_lzma_b64)
self.raw_data = lzma.decompress(raw_lzma).decode()
self.parse_frames()
'''


class Replay:

    def __init__(self, score_id, raw_bytes):
        self.score_id = score_id
        self.raw_lzma_bytes = raw_bytes
        return

    @classmethod
    def from_api(cls, score_id: Union[str, int]):
        params = {'k': os.environ['API_KEY'], 's': score_id}
        while True:
            with requests.get('https://osu.ppy.sh/api/get_replay', params=params) as r:
                if r.status_code == 429:
                    continue
                else:
                    raw_lzma_b64 = r.json()['content']
                    break

        raw_lzma_bytes = base64.b64decode(raw_lzma_b64)
        return cls(score_id, raw_lzma_bytes)

    def save(self, save_folder: str):
        lzma_save_path = os.path.join(save_folder, f'{self.score_id}.lzma')
        with open(lzma_save_path, 'wb') as f:
            f.write(self.raw_lzma_bytes)

    @classmethod
    def from_path(cls, file_path):
        score_id = os.path.splitext(os.path.basename(file_path))[0]
        with open(file_path, 'rb') as f:
            raw_bytes = f.read()
        return cls(score_id, raw_bytes)

    def parse_frames(self):
        raw_data = lzma.decompress(self.raw_lzma_bytes).decode()
        offset = int(raw_data.split(',')[1].split("|")[0]) + int(raw_data.split(',')[0].split("|")[0])
        abs_time = offset
        frames = []
        for line in raw_data.split(',')[2:-2]:
            frame_parts = line.split('|')
            time = int(frame_parts[0])
            abs_time += time
            frames.append(ReplayFrameWithAbsTime.from_string(line, abs_time))

        return frames


class ScoreWithReplay:
    def __init__(self, score_meta: ScoreMeta, replay_data: Replay):
        self.score = score_meta
        self.replay = replay_data
