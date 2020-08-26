import pickle as pkl
import json
import os

from utils.hitobj_cursor_relations import *
from utils.replay_data import ScoreWithReplay, ReplayFrameWithAbsTime
from utils.metadata import ScoreMeta

import numpy as np
from slider import Beatmap

bmap_cache = os.path.join('cache', 'beatmaps')
scores_cache = os.path.join('cache', 'fixed_scores')


def extract_max_velocity_data_as_npy(bmap_id, score_id, save_path):
    replay_path = os.path.join(scores_cache, f'{bmap_id}', f'{score_id}.pkl')
    score_meta_path = os.path.join(scores_cache, f'{bmap_id}', f'{score_id}.json')

    with open(replay_path, 'rb') as f:
        replay_frames = pkl.load(f)
    with open(score_meta_path, 'r') as f:
        score_meta = ScoreMeta(json.load(f))

    print(f'Nr of replay frames:{len(replay_frames)}')

    bmap_path = os.path.join(bmap_cache, f'{bmap_id}.osu')
    bmap = Beatmap.from_path(bmap_path)

    hitobj_pairs = get_hitobject_pairs(bmap, score_meta)

    replay_frame_times = []
    for frame in replay_frames:
        replay_frame_times.append(frame.abs_time)

    valid_hitobj_pairs = []
    for hitobj_pair in hitobj_pairs:
        replay_slice = get_replay_slice_between_hitobjects(hitobj_pair, replay_frame_times, replay_frames)
        hitobj_pair.find_max_velocity_of_cursor(replay_slice)
        if not (hitobj_pair.max_vel_point.velocity == -1):
            valid_hitobj_pairs.append(hitobj_pair)

    required_data = []
    for hitobj_pair in valid_hitobj_pairs:
        max_velocity_array = [hitobj_pair.max_vel_point.velocity,
                              # Max velocity in hit object pair

                              hitobj_pair.max_vel_point.f1.mouse_pos.x,
                              hitobj_pair.max_vel_point.f1.mouse_pos.y,
                              # Mouse position of 1st frame at max velocity

                              hitobj_pair.max_vel_point.f2.mouse_pos.x,
                              hitobj_pair.max_vel_point.f2.mouse_pos.y,
                              # Mouse position of 2nd frame at max velocity

                              hitobj_pair.max_vel_point.f1.abs_time,
                              # Time of 1st frame at max velocity point pair

                              hitobj_pair.max_vel_point.f2.abs_time,
                              # Time of 2nd frame at max velocity point pair

                              hitobj_pair.hit_obj1.position.x,
                              hitobj_pair.hit_obj1.position.y,
                              hitobj_pair.hit_obj2.position.x,
                              hitobj_pair.hit_obj2.position.y,
                              # Hit object positions

                              position.distance(hitobj_pair.hit_obj1.position, hitobj_pair.hit_obj2.position),
                              # Distance between hit objects

                              hitobj_pair.hit_obj1.time.total_seconds() * 1000,
                              hitobj_pair.hit_obj2.time.total_seconds() * 1000,
                              # Time in ms of hit objects

                              (hitobj_pair.hit_obj2.time - hitobj_pair.hit_obj1.time).total_seconds() * 1000
                              # Time between hit objects
                              ]

        required_data.append(max_velocity_array)

    np_data = np.array(required_data)
    np.save(save_path, np_data)


if __name__ == '__main__':

    extracted_data_folder = 'data'
    os.makedirs(extracted_data_folder, exist_ok=True)
    
    for bmap_id in os.listdir(scores_cache):
        bmap_folder = os.path.join(scores_cache, bmap_id)
        for score_id_dot_pkl in os.listdir(bmap_folder):
            if score_id_dot_pkl.endswith('.json'):
                continue
            score_id = score_id_dot_pkl.replace('.pkl', '')

            save_path = os.path.join(extracted_data_folder, f'{bmap_id}_{score_id}.npy')
            extract_max_velocity_data_as_npy(bmap_id, score_id, save_path)