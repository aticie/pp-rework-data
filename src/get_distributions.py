import pickle as pkl
import json

from utils.hitobj_cursor_relations import *
from utils.replay_data import ScoreWithReplay, ReplayFrameWithAbsTime
from utils.metadata import ScoreMeta

import numpy as np
from slider import Beatmap

if __name__ == '__main__':
    bmap_id = 1714634
    score_id = 2627460092
    replay_path = f'cache/fixed_scores/{bmap_id}/{score_id}.pkl'
    score_meta_path = f'cache/fixed_scores/{bmap_id}/{score_id}.json'
    with open(replay_path, 'rb') as f:
        replay_frames = pkl.load(f)
    with open(score_meta_path, 'r') as f:
        score_meta = ScoreMeta(json.load(f))

    print(f'Nr of replay frames:{len(replay_frames)}')

    bmap_path = f'cache/beatmaps/{bmap_id}.osu'
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
        max_velocity_array = [hitobj_pair.max_vel_point.velocity,  # Max velocity in hit object pair
                              hitobj_pair.max_vel_point.f1.mouse_pos.to_tuple(),
                              # Mouse position of 1st frame at max velocity
                              hitobj_pair.max_vel_point.f2.mouse_pos.to_tuple(),
                              # Mouse position of 2nd frame at max velocity
                              hitobj_pair.max_vel_point.f1.abs_time,  # Time of 1st frame at max velocity point pair
                              hitobj_pair.max_vel_point.f2.abs_time,  # Time of 2nd frame at max velocity point pair
                              position.distance(hitobj_pair.hit_obj1.position, hitobj_pair.hit_obj2.position),
                              # Distance between hit objects
                              (hitobj_pair.hit_obj2.time - hitobj_pair.hit_obj1.time).total_seconds() * 1000
                              # Time between hit objects
                              ]

        required_data.append(max_velocity_array)

    np_data = np.array(required_data, dtype=object)
    np.save(f'{bmap_id}_{score_id}.npy', np_data)