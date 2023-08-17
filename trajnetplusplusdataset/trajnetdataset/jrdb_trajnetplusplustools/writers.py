import json
from .data import SceneRow, TrackRow


def trajnet_tracks(row):
    x = row.x
    y = row.y
    h = row.h
    w = row.w
    l = row.l
    rot_z = row.rot_z
    bb_left = row.bb_left
    bb_top = row.bb_top
    bb_width = row.bb_width
    bb_height = row.bb_height


    


    if row.prediction_number is None:
        return json.dumps({'track': {'f': row.frame, 'p': row.pedestrian, 'x': x, 'y': y, 
                                    'h': h, 'w': w, 'l': l, 'rot_z': rot_z,
                                    'bb_left' : bb_left, 'bb_top' : bb_top, 'bb_width' : bb_width, 'bb_height' :bb_height}})
    return json.dumps({'track': {'f': row.frame, 'p': row.pedestrian, 'x': x, 'y': y,
                                'h': h, 'w': w, 'l': l, 'rot_z': rot_z,
                                'bb_left' : bb_left, 'bb_top' : bb_top, 'bb_width' : bb_width, 'bb_height' :bb_height,
                                'prediction_number': row.prediction_number,
                                'scene_id': row.scene_id}})



def trajnet_scenes(row):
    return json.dumps(
        {'scene': {'id': row.scene, 'p': row.pedestrian, 's': row.start, 'e': row.end,
                   'fps': row.fps, 'tag': row.tag}})


def trajnet(row):
    if isinstance(row, TrackRow):
        return trajnet_tracks(row)
    if isinstance(row, SceneRow):
        return trajnet_scenes(row)

    raise Exception('unknown row type')
