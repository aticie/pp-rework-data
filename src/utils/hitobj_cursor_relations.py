from datetime import timedelta
from typing import List

from utils.math_utils import binary_search_frame_index
from utils.replay_data import ReplayFrameWithAbsTime
from utils.metadata import ScoreMeta

from slider.beatmap import HitObject, Beatmap
from slider import position

'''
max cursor velocity between circles determined between time when cursor leaves circle area and enters circle area

max cursor velocity between slider points determined by time between slider points

position of cursor at point of recorded cursor velocity

time in replay at recorded max cursor velocity

distance between circles / slider points at recorded max cursor velocity

time between circles / sliders points at recorded max cursor velocity
'''


class MaxVelocityPoint:
    def __init__(self, hitobj1: HitObject, hitobj2: HitObject):
        self.f1 = None
        self.f2 = None
        self.hitobj1 = hitobj1
        self.hitobj2 = hitobj2
        self.velocity = -1

    def set_frames(self, frame1: ReplayFrameWithAbsTime, frame2: ReplayFrameWithAbsTime):
        self.f1 = frame1
        self.f2 = frame2
        self.velocity = frame2.mouse_pos.distance(frame1.mouse_pos) / (frame2.abs_time - frame1.abs_time)


class HitObjectPair:

    def __init__(self, hit1: HitObject, hit2: HitObject, overall_difficulty: float, circle_size: float):
        self.hit_obj1 = hit1
        self.hit_obj2 = hit2
        self.distance = position.distance(hit1.position, hit2.position)
        self.hit_window = timedelta(milliseconds=400 - 20 * overall_difficulty)  # 400ms - 20ms * OD
        self.start_time = hit1.time - self.hit_window
        self.end_time = hit2.time + self.hit_window
        self.circle_radius = (109 - 9 * circle_size) / 2
        self.max_vel_point = MaxVelocityPoint(hit1, hit2)

    def prepare_dict(self):
        self.__dict__ = {'obj1': self.hit_obj1,
                         'obj2': self.hit_obj2,
                         'dist': self.distance,
                         'start_time': self.start_time.total_seconds() * 1000,
                         'end_time': self.end_time.total_seconds() * 1000,
                         'max_velocity': self.max_vel_point.velocity,
                         'max_velocity_frame1_time': self.max_vel_point.f1.abs_time,
                         'max_velocity_frame2_time': self.max_vel_point.f2.abs_time,
                         'max_velocity_frame1_mouse_pos': self.max_vel_point.f1.mouse_pos,
                         'max_velocity_frame2_mouse_pos': self.max_vel_point.f2.mouse_pos
                         }

    def __str__(self):
        return f'Hitobjects between {self.start_time}ms - {self.end_time}ms\n' \
               f'Max Velocity: {self.max_vel_point.velocity:.2f}\n' \
            # f'Distance: {self.max_vel_point.f1.mouse_pos.distance(self.max_vel_point.f2.mouse_pos)} osu! px\n' \
        # f'Calculated over {self.max_vel_point.f1.rel_time}ms'

    def find_max_velocity_of_cursor(self, replay_slice: List[ReplayFrameWithAbsTime]):
        inside_first_hitobj = -1
        outside_first_hitobj = -1
        inside_second_hitobj = -1

        for i in range(len(replay_slice)):
            mouse_pos = replay_slice[i].mouse_pos
            if position.distance(self.hit_obj1.position, mouse_pos) <= self.circle_radius:
                inside_first_hitobj = i
                break

        for i in range(inside_first_hitobj, len(replay_slice)):
            mouse_pos = replay_slice[i].mouse_pos
            if position.distance(self.hit_obj1.position, mouse_pos) > self.circle_radius:
                outside_first_hitobj = i
                break

        for i in range(outside_first_hitobj, len(replay_slice)):
            mouse_pos = replay_slice[i].mouse_pos
            if position.distance(self.hit_obj2.position, mouse_pos) <= self.circle_radius:
                inside_second_hitobj = i
                break

        frames_between_hitobjects = replay_slice[outside_first_hitobj: inside_second_hitobj]

        for f1, f2 in zip(frames_between_hitobjects[:-1], frames_between_hitobjects[1:]):
            dist = f2.mouse_pos.distance(f1.mouse_pos)
            dtime = f2.abs_time - f1.abs_time
            if dtime == 0:
                continue
            vel = dist / dtime
            if vel > self.max_vel_point.velocity:
                self.max_vel_point.set_frames(f1, f2)


# Fuck sliders for now
class SliderPointPairs:
    def __init__(self, hit1: HitObject, hit2: HitObject, hit_window: timedelta, circle_size: float):
        self.point1 = hit1
        self.point2 = hit2
        self.distance = position.distance(hit1.position, hit2.position)
        self.start_time = hit1.time - hit_window
        self.end_time = hit2.time + hit_window
        self.circle_radius = (109 - 9 * circle_size) / 2
        self.max_vel_point = MaxVelocityPoint()


def get_hitobject_pairs(beatmap: Beatmap, score_meta: ScoreMeta) -> List[HitObjectPair]:
    enabled_mods = int(score_meta.enabled_mods)
    hr_enabled = (enabled_mods & 16) == 16
    hitobjects = beatmap.hit_objects(sliders=False, spinners=False, hard_rock=hr_enabled)
    circle_size = beatmap.cs(hard_rock=hr_enabled)
    overall_difficulty = beatmap.od(hard_rock=hr_enabled)
    circle_diameter = 109 - 9 * circle_size
    time_threshold = timedelta(seconds=0.8)  # Time threshold between objects,
    # if 2 hit objects are separated apart long time (0.8 sec) -> ignore

    hitobj_pairs = []
    for hitobj1, hitobj2 in zip(hitobjects[:-1], hitobjects[1:]):

        # We do not want touching hit objects
        touching = position.distance(hitobj1.position, hitobj2.position) <= circle_diameter
        # We do not want stacked hit objects
        stacked = hitobj1.position == hitobj2.position
        # We do not want long time intervals between hit objects
        long_time_between_objects = hitobj1.time - hitobj2.time > time_threshold

        if not (stacked or touching or long_time_between_objects):
            hitobj_pairs.append(HitObjectPair(hitobj1, hitobj2, overall_difficulty, circle_size))

    return hitobj_pairs


def get_replay_slice_between_hitobjects(hitobj_pair: HitObjectPair, replay_frame_times: List[int],
                                        replay: List[ReplayFrameWithAbsTime]) -> List[ReplayFrameWithAbsTime]:
    start_time = hitobj_pair.start_time
    end_time = hitobj_pair.end_time

    start_index = binary_search_frame_index(replay_frame_times, start_time.total_seconds() * 1000)
    end_index = binary_search_frame_index(replay_frame_times, end_time.total_seconds() * 1000)

    return replay[start_index: end_index]
