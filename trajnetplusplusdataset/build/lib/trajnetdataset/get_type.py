""" Categorization of Primary Pedestrian """

import numpy as np
import pysparkling

import trajnetplusplustools
from trajnetplusplustools.kalman import predict as kalman_predict
from trajnetplusplustools.interactions import check_interaction, group
from trajnetplusplustools.interactions import get_interaction_type

import pickle
from .orca_helper import predict_all

def get_type(scene, args):
    '''
    Categorization of Single Scene
    :param scene: All trajectories as TrackRows, args
    :return: The type of the traj
    '''

    ## Get xy-coordinates from trackRows
    scene_xy = trajnetplusplustools.Reader.paths_to_xy(scene)

    ## Type 1
    def euclidean_distance(row1, row2):
        """Euclidean distance squared between two rows."""
        return np.sqrt((row1.x - row2.x) ** 2 + (row1.y - row2.y) ** 2)

    ## Type 2
    def linear_system(scene, obs_len, pred_len):
        '''
        return: True if the traj is linear according to Kalman
        '''
        kalman_prediction, _ = kalman_predict(scene, obs_len, pred_len)[0]
        return trajnetplusplustools.metrics.final_l2(scene[0], kalman_prediction)

    ## Type 3
    def interaction(rows, pos_range, dist_thresh, obs_len):
        '''
        :return: Determine if interaction exists and type (optionally)
        '''
        interaction_matrix = check_interaction(rows, pos_range=pos_range, \
                                 dist_thresh=dist_thresh, obs_len=obs_len)
        return np.any(interaction_matrix)

    ## Category Tags
    mult_tag = []
    sub_tag = []

    # Static
    if euclidean_distance(scene[0][0], scene[0][-1]) < args.static_threshold:
        mult_tag.append(1)

    # Linear
    elif linear_system(scene, args.obs_len, args.pred_len) < args.linear_threshold:
        mult_tag.append(2)

    # Interactions
    elif interaction(scene_xy, args.inter_pos_range, args.inter_dist_thresh, args.obs_len) \
         or np.any(group(scene_xy, args.grp_dist_thresh, args.grp_std_thresh, args.obs_len)):
        mult_tag.append(3)

    # Non-Linear (No explainable reason)
    else:
        mult_tag.append(4)

    # Interaction Types
    if mult_tag[0] == 3:
        sub_tag = get_interaction_type(scene_xy, args.inter_pos_range,
                                       args.inter_dist_thresh, args.obs_len)
    else:
        sub_tag = []

    return mult_tag[0], mult_tag, sub_tag

def check_collision(scene, n_predictions):
    '''
    Skip the track if collision occurs between primanry and others
    return: True if collision occurs
    '''
    ped_interest = scene[0]
    for ped_other in scene[1:]:
        if trajnetplusplustools.metrics.collision(ped_interest, ped_other, n_predictions):
            return True
    return False

def add_noise(observation):
    ## Last Position Noise
    # observation[0][-1] += np.random.uniform(0, 0.04, (2,))

    ## Last Position Noise
    thresh = 0.005  ## 0.01 for num_ped 3
    observation += np.random.uniform(-thresh, thresh, observation.shape)
    return observation

def orca_validity(scene, goals, pred_len=12, obs_len=9, mode='trajnet', iters=15):
    '''
    Check ORCA can reconstruct scene on rounding (To clean in future)
    '''
    scene_xy = trajnetplusplustools.Reader.paths_to_xy(scene)
    for _ in range(iters):
        observation = add_noise(scene_xy[:obs_len].copy())
        orca_pred = predict_all(observation, goals, mode, pred_len)
        if len(orca_pred[0]) != pred_len:
            # print("Length Invalid")
            return True
        for m, _ in enumerate(orca_pred):
            if len(orca_pred[m]) != pred_len:
                continue
            diff_ade = np.mean(np.linalg.norm(np.array(scene_xy[-pred_len:, m]) - np.array(orca_pred[m]), axis=1))
            diff_fde = np.linalg.norm(np.array(scene_xy[-1, m]) - np.array(orca_pred[m][-1]))
            if diff_ade > 0.11 or diff_fde > 0.2:   ## (0.08, 0.1) for num_ped 3
                # print("ORCA Invalid")
                return True
    return False

def all_ped_present(scene):
    """ 
    Consider only those scenes where all pedestrians are present
    Note: Different from removing incomplete trajectories
    Useful for generating dataset for fast_parallel code: https://github.com/vita-epfl/trajnetplusplusbaselines/tree/fast_parallel
    """
    scene_xy = trajnetplusplustools.Reader.paths_to_xy(scene)
    return (not np.isnan(scene_xy).any())

def write(rows, path, new_scenes, new_frames):
    """ Writing scenes with categories """
    output_path = path.replace('output_pre', 'output')
    pysp_tracks = rows.filter(lambda r: r.frame in new_frames).map(trajnetplusplustools.writers.trajnet)
    pysp_scenes = pysparkling.Context().parallelize(new_scenes).map(trajnetplusplustools.writers.trajnet)
    pysp_scenes.union(pysp_tracks).saveAsTextFile(output_path)

def trajectory_type(rows, path, fps, track_id=0, args=None):
    """ Categorization of all scenes """

    ## Read
    reader = trajnetplusplustools.Reader(path, scene_type='paths')
    scenes = [s for _, s in reader.scenes()]
    ## Filtered Frames and Scenes
    new_frames = set()
    new_scenes = []

    start_frames = set()
    ###########################################################################
    # scenes_test helps to handle both test and test_private simultaneously
    # scenes_test correspond to Test
    ###########################################################################
    test = 'test' in path
    if test:
        path_test = path.replace('test_private', 'test')
        reader_test = trajnetplusplustools.Reader(path_test, scene_type='paths')
        scenes_test = [s for _, s in reader_test.scenes()]
        ## Filtered Test Frames and Test Scenes
        new_frames_test = set()
        new_scenes_test = []

    ## For ORCA (Sensitivity)
    orca_sensitivity = False
    if args.goal_file is not None:
        goal_dict = pickle.load(open(args.goal_file, "rb"))
        orca_sensitivity = True
        print("Checking sensitivity to initial conditions")

    ## Initialize Tag Stats to be collected
    tags = {1: [], 2: [], 3: [], 4: []}
    mult_tags = {1: [], 2: [], 3: [], 4: []}
    sub_tags = {1: [], 2: [], 3: [], 4: []}
    col_count = 0

    if not scenes:
        raise Exception('No scenes found')

    for index, scene in enumerate(scenes):
        if (index+1) % 50 == 0:
            print(index)

        ## Primary Path
        ped_interest = scene[0]

        # if ped_interest[0].frame in start_frames:
        #     # print("Got common start")
        #     continue

        # Assert Test Scene length
        if test:
            assert len(scenes_test[index][0]) >= args.obs_len, \
                   'Scene Test not adequate length'

        ## Check Collision
        ## Used in CFF Datasets to account for imperfect tracking
        # if check_collision(scene, args.pred_len):
        #     col_count += 1
        #     continue

        # ## Consider only those scenes where all pedestrians are present
        # # Note: Different from removing incomplete trajectories
        if args.all_present and (not all_ped_present(scene)):
            continue

        ## Get Tag
        tag, mult_tag, sub_tag = get_type(scene, args)

        if np.random.uniform() < args.acceptance[tag - 1]:
            ## Check Validity
            ## Used in ORCA Datasets to account for rounding sensitivity
            if orca_sensitivity:
                goals = [goal_dict[path[0].pedestrian] for path in scene]
                # print('Type III')
                if orca_validity(scene, goals, args.pred_len, args.obs_len, args.mode):
                    col_count += 1
                    continue

            ## Update Tags
            tags[tag].append(track_id)
            for tt in mult_tag:
                mult_tags[tt].append(track_id)
            for st in sub_tag:
                sub_tags[st].append(track_id)

            ## Define Scene_Tag
            scene_tag = []
            scene_tag.append(tag)
            scene_tag.append(sub_tag)

            ## Filtered scenes and Frames
            # start_frames |= set(ped_interest[i].frame for i in range(len(ped_interest[0:1])))
            # print(start_frames)
            new_frames |= set(ped_interest[i].frame for i in range(len(ped_interest)))
            new_scenes.append(
                trajnetplusplustools.data.SceneRow(track_id, ped_interest[0].pedestrian,
                                           ped_interest[0].frame, ped_interest[-1].frame,
                                           fps, scene_tag))

            ## Append to list of scenes_test as well if Test Set
            if test:
                new_frames_test |= set(ped_interest[i].frame for i in range(args.obs_len))
                new_scenes_test.append(
                    trajnetplusplustools.data.SceneRow(track_id, ped_interest[0].pedestrian,
                                               ped_interest[0].frame, ped_interest[-1].frame,
                                               fps, 0))

            track_id += 1


    # Writes the Final Scenes and Frames
    write(rows, path, new_scenes, new_frames)
    if test:
        write(rows, path_test, new_scenes_test, new_frames_test)

    ## Stats

    # Number of collisions found
    print("Col Count: ", col_count)

    if scenes:
        print("Total Scenes: ", index)

        # Types:
        print("Main Tags")
        print("Type 1: ", len(tags[1]), "Type 2: ", len(tags[2]),
              "Type 3: ", len(tags[3]), "Type 4: ", len(tags[4]))
        print("Sub Tags")
        print("LF: ", len(sub_tags[1]), "CA: ", len(sub_tags[2]),
              "Group: ", len(sub_tags[3]), "Others: ", len(sub_tags[4]))

    return track_id
