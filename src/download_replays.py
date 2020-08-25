import time
import pickle
import os

from utils import metadata
from utils.replay_data import Replay

from tqdm import tqdm
import requests


class ScoreWithReplay:
    def __init__(self, score_meta, replay_data):
        self.score = score_meta
        self.replay = replay_data


if __name__ == '__main__':
    # Parse beatmap list from txt
    with open('beatmaps.txt', 'r') as f:
        lines = f.read().splitlines()

    bmap_ids = [int(line.split('/')[-1]) for line in lines]  # Populate beatmap ids in a list

    # Get beatmap metadata from api
    for bmap_id in bmap_ids:
        print(f'Getting beatmap information for bmap id: {bmap_id}')
        bmap_meta = metadata.BeatmapMeta()
        bmap_meta.get_from_api(bmap_id)
        time.sleep(.5)  # Maybe can get rate limited

        print(f'Getting top 100 scores of: {bmap_meta.title}')
        scores = metadata.get_scores_of_bmap_from_api(bmap_id)
        time.sleep(.5)  # Maybe can get rate limited
        os.makedirs(os.path.join('cache', 'beatmaps'), exist_ok=True)
        url = f'https://osu.ppy.sh/osu/{bmap_id}'
        bmap_save_path = os.path.join('cache', 'beatmaps', f'{bmap_id}.osu')
        with requests.get(url) as r:
            with open(bmap_save_path, 'w', encoding='utf-8') as f:
                f.write(r.content.decode('utf-8'))
        with open(os.path.join('cache', 'beatmaps', f'{bmap_id}.pkl'), 'wb') as f:
            pickle.dump(bmap_meta, f)

        for score in tqdm(scores):
            score_save_path = os.path.join('cache', 'scores', f'{score.score_id}.pkl')
            if not score.replay_available:
                continue
            if os.path.exists(score_save_path):
                continue
            replay_data = Replay()
            replay_data.get_from_api(score.score_id)
            time.sleep(6)  # As this is quite a load-heavy request, it has special rules about rate limiting.
            # You are only allowed to do 10 requests per minute.
            # Also, please note that this request is not intended for batch retrievals.
            os.makedirs(os.path.join('cache', 'scores'), exist_ok=True)
            score_with_replay = ScoreWithReplay(score, replay_data)
            with open(score_save_path, 'wb') as f:
                pickle.dump(score_with_replay, f)
