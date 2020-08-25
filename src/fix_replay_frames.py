import pickle as pkl
import os
import json

from utils.replay_data import ScoreWithReplay, ReplayFrameWithAbsTime

if __name__ == '__main__':
    scores_folder = os.path.join('cache', 'scores')
    fixed_scores_folder = os.path.join('cache', 'fixed_scores')
    for bmap_id in os.listdir(scores_folder):
        scores_of_bmap_folder = os.path.join(scores_folder, bmap_id)
        for score_id_dot_pkl in os.listdir(scores_of_bmap_folder):
            score_id = score_id_dot_pkl.replace('.pkl', '')
            score_path = os.path.join(scores_of_bmap_folder, score_id_dot_pkl)
            with open(score_path, 'rb') as f:
                score = pkl.load(f)

            os.makedirs(os.path.join(fixed_scores_folder, bmap_id), exist_ok=True)
            with open(os.path.join(fixed_scores_folder, bmap_id, f'{score_id}.json'), 'w') as f:
                json.dump(score.score.__dict__, f, indent=2)

            replay_frames = score.replay.frames
            offset = replay_frames[1].time + replay_frames[0].time
            abs_time = offset
            frames_with_abs_times = []
            for frame in replay_frames[2:-2]:
                abs_time += frame.time
                frames_with_abs_times.append(
                    ReplayFrameWithAbsTime(frame.time, abs_time, frame.mouse_pos, frame.key_state))

            with open(os.path.join(fixed_scores_folder, bmap_id, f'{score_id}.pkl'), 'wb') as f:
                pkl.dump(frames_with_abs_times, f)