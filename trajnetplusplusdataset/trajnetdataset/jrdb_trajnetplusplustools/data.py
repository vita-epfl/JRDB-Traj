from collections import namedtuple


TrackRow = namedtuple('Row', ['frame', 'pedestrian', 'x', 'y', 'h', 'w', 'l', 'rot_z', 'bb_left', 'bb_top', 'bb_width', 'bb_height', 'prediction_number', 'scene_id'])
TrackRow.__new__.__defaults__ = (None, None, None, None, None, None, None, None, None, None, None, None, None, None)
SceneRow = namedtuple('Row', ['scene', 'pedestrian', 'start', 'end', 'fps', 'tag'])
SceneRow.__new__.__defaults__ = (None, None, None, None, None, None)
