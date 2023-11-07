# import pickle
# import numpy as np
import json
import pickle
import numpy as np
import sys, os
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from trajnetbaselines.lstm.tools.reader import Reader

def load_test_datasets(dataset, goal_flag, args):
    """Load Test Prediction file with goals (optional)"""
    all_goals = {}
    dataset_name = dataset.replace(args.path.replace('_pred', '') + 'test/', '') + '.ndjson'
    print('Dataset Name: ', dataset_name)

    # Read Scenes from 'test' folder
    reader = Reader(args.path.replace('_pred', '') + dataset + '.ndjson', scene_type='paths')
    ## Necessary modification of train scene to add filename (for goals)
    scenes = [(dataset, s_id, s) for s_id, s in reader.scenes()]

    if goal_flag:
        print("Loading Goal File: ", 'goal_files/test_private/' + dataset +'.pkl')
        goal_dict = pickle.load(open('goal_files/test_private/' + dataset +'.pkl', "rb"))
        all_goals[dataset] = {s_id: [goal_dict[path[0].pedestrian] for path in s] for _, s_id, s in scenes}
        scene_goals = [np.array(all_goals[filename][scene_id]) for filename, scene_id, _ in scenes]
    else:
        scene_goals = [np.zeros((len(paths), 2)) for _, scene_id, paths in scenes]

    return dataset_name, scenes, scene_goals


def preprocess_test(scene, obs_len):
    """Remove pedestrian trajectories that appear post observation period.
    Can occur when the test set has overlapping scenes."""
    obs_frames = [primary_row.frame for primary_row in scene[0]][:obs_len]
    last_obs_frame = obs_frames[-1]
    scene = [[row for row in ped if row.frame <= last_obs_frame]
                for ped in scene if ped[0].frame <= last_obs_frame]

    return scene


def write_predictions(pred_list, scenes, model_name, dataset_name, dataset_index, args):
    """Write predictions corresponding to the scenes in the respective file"""
    dataset_name = dataset_name.replace('.ndjson','_temp.txt')

    path_temp = args.path+model_name+'/'+'temp/'+dataset_name
    path_pred = args.path+model_name+'/'+'jrdb_submission/'

    with open(path_temp, "a") as myfile:
        ## Write All Predictions
        for (predictions, (_, scene_id, paths)) in zip(pred_list, scenes):
            ## Extract 1) first_frame, 2) frame_diff 3) ped_ids for writing predictions
            observed_path = paths[0]
            frame_diff = observed_path[1].frame - observed_path[0].frame
            first_frame = observed_path[args.obs_length-1].frame + frame_diff
            ped_id = observed_path[0].pedestrian
         
            for m in range(len(predictions)):
                prediction, _ = predictions[m]
                ## Write Primary
                for i in range(len(prediction)):

                    data = [first_frame + i * frame_diff, ped_id,prediction[i, 0].item(), prediction[i, 1].item(), prediction[i,2].item()]
                    for d in data:
                        myfile.write(str(d))
                        myfile.write(' ')
                    myfile.write('\n')

    txt_name = path_temp

    trajs = np.loadtxt(txt_name, dtype=str)
    trajs = np.array(trajs).astype(float)
    with open(path_pred+ str(dataset_index).zfill(4)+'.txt', 'a') as txtfile:
        for pred_id in range(12):
            for row_id in range(trajs.shape[0]):
                if trajs[row_id,0] == trajs[pred_id,0]:

                    data_final = [int(trajs[row_id,0]),int(trajs[row_id,1]), 'Pedestrian', 0, 0, -1 ,-1, -1, -1, -1, trajs[row_id,2], trajs[row_id,3]]

                    for d_final in data_final:
                        txtfile.write(str(d_final))
                        txtfile.write(' ')
                    txtfile.write('\n')

