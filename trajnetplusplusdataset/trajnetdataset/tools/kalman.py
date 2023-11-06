""" Kalman filter Prediction """

import numpy as np
import pykalman
from .data import TrackRow

def predict(paths, obs_len, pred_len, predict_all=False):
    multimodal_outputs = {}
    neighbours_tracks = []

    ## Single Prediction
    if not predict_all:
        paths = paths[0:1]

    for i, path in enumerate(paths):
        path = paths[i]
        initial_state_mean = [path[0].x, 0, path[0].y, 0]

        transition_matrix = [[1, 1, 0, 0],
                             [0, 1, 0, 0],
                             [0, 0, 1, 1],
                             [0, 0, 0, 1]]

        observation_matrix = [[1, 0, 0, 0],
                              [0, 0, 1, 0]]

        kf = pykalman.KalmanFilter(transition_matrices=transition_matrix,
                                   observation_matrices=observation_matrix,
                                   transition_covariance=1e-5 * np.eye(4),
                                   observation_covariance=0.05**2 * np.eye(2),
                                   initial_state_mean=initial_state_mean)
        # kf.em([(r.x, r.y) for r in path[:9]], em_vars=['transition_matrices',
        #                                                'observation_matrices'])

        kf.em([(r.x, r.y) for r in path[:obs_len]])
        observed_states, _ = kf.smooth([(r.x, r.y) for r in path[:obs_len]])

        # prepare predictions
        frame_diff = path[1].frame - path[0].frame
        first_frame = path[obs_len - 1].frame + frame_diff
        ped_id = path[obs_len - 1].pedestrian

        # sample predictions (first sample corresponds to last state)
        # average 5 sampled predictions
        predictions = None
        for _ in range(5):
            _, pred = kf.sample(pred_len + 1, initial_state=observed_states[-1])
            if predictions is None:
                predictions = pred
            else:
                predictions += pred
        predictions /= 5.0
        if i == 0:
            primary_track = [TrackRow(first_frame + j * frame_diff, ped_id, x, y)
                             for j, (x, y) in enumerate(predictions[1:])]
        else:
            neighbours_tracks.append([TrackRow(first_frame + j * frame_diff, ped_id, x, y)
                                      for j, (x, y) in enumerate(predictions[1:])])
    multimodal_outputs[0] = primary_track, neighbours_tracks
    return multimodal_outputs
