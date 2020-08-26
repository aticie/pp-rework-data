import matplotlib.pyplot as plt
import numpy as np
import os
import json
import pickle as pkl

from utils.metadata import ScoreMeta
from utils.hitobj_cursor_relations import *

from slider.beatmap import Beatmap


def get_limits(pt1, pt2):
    min_x = min(pt1.x, pt2.x) - 50
    min_y = min(pt1.y, pt2.y) - 50
    max_x = max(pt1.x, pt2.x) + 50
    max_y = max(pt1.y, pt2.y) + 50
    return min_x, min_y, max_x, max_y


def show_hitobj_pair_with_replay(replay_slice, hitobj_pair, key_events):
    fig, ax = plt.subplots()
    ax.set_aspect('equal')

    hitobj1_circle = plt.Circle((hitobj_pair.hit_obj1.position.x, hitobj_pair.hit_obj1.position.y),
                                hitobj_pair.circle_radius, color='grey', fill=False, linewidth=3)
    hitobj2_circle = plt.Circle((hitobj_pair.hit_obj2.position.x, hitobj_pair.hit_obj2.position.y),
                                hitobj_pair.circle_radius, color='grey', fill=False, linewidth=3)

    bbox = get_limits(hitobj_pair.hit_obj1.position, hitobj_pair.hit_obj2.position)
    ax.set_xlim(left=bbox[0], right=bbox[2])
    ax.set_ylim(bottom=bbox[1], top=bbox[3])

    ax.add_artist(hitobj1_circle)
    ax.add_artist(hitobj2_circle)

    mouse_x = [frame.mouse_pos.x for frame in replay_slice]
    mouse_y = [frame.mouse_pos.y for frame in replay_slice]

    plt.scatter(mouse_x, mouse_y, marker="x", c='black')

    for i in key_events:
        mp = replay_slice[i].mouse_pos
        plt.scatter(mp.x, mp.y, marker="x")

    plt.text(hitobj_pair.hit_obj1.position.x, hitobj_pair.hit_obj1.position.y,
             f'{(hitobj_pair.start_time + hitobj_pair.hit_window).total_seconds() * 1000:.0f}')

    plt.text(hitobj_pair.hit_obj2.position.x, hitobj_pair.hit_obj2.position.y,
             f'{(hitobj_pair.end_time - hitobj_pair.hit_window).total_seconds() * 1000:.0f}')

    plt.text(replay_slice[0].mouse_pos.x, replay_slice[0].mouse_pos.y, f'{replay_slice[0].abs_time}')
    plt.text(replay_slice[-1].mouse_pos.x, replay_slice[-1].mouse_pos.y, f'{replay_slice[-1].abs_time}')

    f1 = hitobj_pair.max_vel_point.f1
    f2 = hitobj_pair.max_vel_point.f2
    dx, dy = f2.mouse_pos.x - f1.mouse_pos.x, f2.mouse_pos.y - f1.mouse_pos.y
    plt.arrow(f1.mouse_pos.x, f1.mouse_pos.y, dx, dy, color='red')
    plt.text(f1.mouse_pos.x, f1.mouse_pos.y + 5, f'{hitobj_pair.max_vel_point.velocity:.2f}')

    plt.show()

    return


if __name__ == "__main__":

    bmap_id = 1714634
    score_id = 2627460092

    bmap_cache = os.path.join('cache', 'beatmaps')
    scores_cache = os.path.join('cache', 'fixed_scores')
    bmap_path = os.path.join(bmap_cache, f'{bmap_id}.osu')

    bmap = Beatmap.from_path(bmap_path)

    replay_path = os.path.join(scores_cache, f'{bmap_id}', f'{score_id}.pkl')
    score_meta_path = os.path.join(scores_cache, f'{bmap_id}', f'{score_id}.json')

    with open(replay_path, 'rb') as f:
        replay_frames = pkl.load(f)
    with open(score_meta_path, 'r') as f:
        score_meta = ScoreMeta(json.load(f))

    hitobj_pairs = get_hitobject_pairs(bmap, score_meta)
    replay_frame_times = []
    for frame in replay_frames:
        replay_frame_times.append(frame.abs_time)

    for hitobj_pair in hitobj_pairs:
        replay_slice = get_replay_slice_between_hitobjects(hitobj_pair, replay_frame_times, replay_frames)
        i1, o1, i2 = hitobj_pair.find_max_velocity_of_cursor(replay_slice)
        key_events = [i1, o1, i2]
        if not (hitobj_pair.max_vel_point.velocity == -1):
            show_hitobj_pair_with_replay(replay_slice, hitobj_pair, key_events)
