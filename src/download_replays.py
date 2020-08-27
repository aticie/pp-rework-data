import time
import os

from utils import metadata
from utils.replay_data import Replay
from utils.beatmap import Beatmap

from tqdm import tqdm

if __name__ == '__main__':
    # Parse beatmap list from txt
    with open('beatmaps.txt', 'r') as f:
        lines = f.read().splitlines()

    bmap_ids = [int(line.split('/')[-1]) for line in lines]  # Populate beatmap ids in a list

    # Get beatmap metadata from api
    for bmap_id in bmap_ids:
        print(f'Getting beatmap information for bmap id: {bmap_id}')
        bmap_save_folder = os.path.join('cache', 'beatmaps')
        score_save_folder = os.path.join('cache', 'new_scores', f'{bmap_id}')

        os.makedirs(bmap_save_folder, exist_ok=True)
        os.makedirs(score_save_folder, exist_ok=True)

        bmap_save_path = os.path.join(bmap_save_folder, f'{bmap_id}.osu')

        if os.path.exists(bmap_save_path):
            score_count = len(os.listdir(score_save_folder))
            if score_count == 50:
                continue
        else:
            # Download and save beatmap (.osu file)
            bmap = Beatmap.download(bmap_id)
            bmap.save(bmap_save_path)

        print(f'Getting top 50 scores of: {bmap_id}')
        scores = metadata.ScoreMeta.top_n_from_api(bmap_id)
        time.sleep(.5)  # Maybe can get rate limited

        for score in tqdm(scores):

            score_meta_save_path = os.path.join(score_save_folder, f'{score.score_id}.json')

            if not score.replay_available:
                continue
            if os.path.exists(score_meta_save_path):
                continue

            replay_data = Replay.from_api(score.score_id)
            replay_data.save(score_save_folder)
            score.save(score_meta_save_path)
            time.sleep(6)  # As this is quite a load-heavy request, it has special rules about rate limiting.
            # You are only allowed to do 10 requests per minute.
            # Also, please note that this request is not intended for batch retrievals.
