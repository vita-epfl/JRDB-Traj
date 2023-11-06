import json
from .data import SceneRow, TrackRow


def trajnet_tracks(row):
    x = row.x
    y = row.y
    v = row.v

    if row.prediction_number is None:
        return json.dumps({'track': {'f': row.frame, 'p': row.pedestrian, 'x': x, 'y': y, 'v' : v}})
                                   
    return json.dumps({'track': {'f': row.frame, 'p': row.pedestrian, 'x': x, 'y': y, 'v' : v,
                             
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
