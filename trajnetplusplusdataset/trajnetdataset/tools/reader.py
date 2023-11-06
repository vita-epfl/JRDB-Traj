from collections import defaultdict
import itertools
import json
import random

import numpy as np

from .data import SceneRow, TrackRow


class Reader(object):
    """Read trajnet files.

    :param scene_type: None -> numpy.array, 'rows' -> TrackRow and SceneRow, 'paths': grouped rows (primary pedestrian first), 'tags': numpy.array and scene tag
    :param image_file: Associated image file of the scene
    """
    def __init__(self, input_file, scene_type=None, image_file=None):
        if scene_type is not None and scene_type not in {'rows', 'paths', 'tags'}:
            raise Exception('scene_type not supported')
        self.scene_type = scene_type

        self.tracks_by_frame = defaultdict(list)
        self.scenes_by_id = dict()

        self.read_file(input_file)

    def read_file(self, input_file):
        with open(input_file, 'r') as f:
            for line in f:
                line = json.loads(line)

                track = line.get('track')
                if track is not None:
                    row = TrackRow(track['f'], track['p'], track['x'], track['y'], track['v'],
                                    # track['h'], track['w'], track['l'], track['rot_z'],
                                    # track['bb_left'], track['bb_top'], track['bb_width'], track['bb_height'],
                                   track.get('prediction_number'), track.get('scene_id'))
                    self.tracks_by_frame[row.frame].append(row)
                    continue

                scene = line.get('scene')
                if scene is not None:
                    row = SceneRow(scene['id'], scene['p'], scene['s'], scene['e'], \
                                   scene.get('fps'), scene.get('tag'))
                    self.scenes_by_id[row.scene] = row

    def scenes(self, randomize=False, limit=0, ids=None, sample=None):
        scene_ids = self.scenes_by_id.keys()
        if ids is not None:
            scene_ids = ids
        if randomize:
            scene_ids = list(scene_ids)
            random.shuffle(scene_ids)
        if limit:
            scene_ids = itertools.islice(scene_ids, limit)
        if sample is not None:
            scene_ids = random.sample(scene_ids, int(len(scene_ids) * sample))
        for scene_id in scene_ids:
            yield self.scene(scene_id)

    @staticmethod
    def track_rows_to_paths(primary_pedestrian, track_rows):
        primary_path = []
        other_paths = defaultdict(list)
        for row in track_rows:
            if row.pedestrian == primary_pedestrian:
                primary_path.append(row)
                continue
            other_paths[row.pedestrian].append(row)

        return [primary_path] + list(other_paths.values())

    @staticmethod
    def paths_to_xy(paths):
        """Convert paths to numpy array with nan as blanks."""
        frames = set(r.frame for r in paths[0])
        pedestrians = set(row.pedestrian
                          for path in paths
                          for row in path if row.frame in frames)
        paths = [path for path in paths if path[0].pedestrian in pedestrians]
        frames = sorted(frames)
        pedestrians = list(pedestrians)

        frame_to_index = {frame: i for i, frame in enumerate(frames)}
        xy = np.full((len(frames), len(pedestrians), 3), np.nan)

        for ped_index, path in enumerate(paths):
            for row in path:
                if row.frame not in frame_to_index:
                    continue
                entry = xy[frame_to_index[row.frame]][ped_index]
                entry[0] = row.x
                entry[1] = row.y
                entry[2] = row.v

                # entry[3] = row.h
                # entry[4] = row.w
                # entry[5] = row.l
                # entry[6] = row.rot_z

                # entry[7] = row.bb_left
                # entry[8] = row.bb_top
                # entry[9] = row.bb_width
                # entry[10] = row.bb_height


        return xy

    def scene(self, scene_id):
        scene = self.scenes_by_id.get(scene_id)
        if scene is None:
            raise Exception('scene with that id not found')

        frames = range(scene.start, scene.end + 1)
        track_rows = [r
                      for frame in frames
                      for r in self.tracks_by_frame.get(frame, [])]

        # return as rows
        if self.scene_type == 'rows':
            return scene_id, scene.pedestrian, track_rows

        # return as paths
        paths = self.track_rows_to_paths(scene.pedestrian, track_rows)
        if self.scene_type == 'paths':
            return scene_id, paths

        ## return with scene tag
        if self.scene_type == 'tags':
            return scene_id, scene.tag, self.paths_to_xy(paths)

        # return a numpy array
        return scene_id, self.paths_to_xy(paths)
