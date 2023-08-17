import numpy as np
import json
import csv
import os
import argparse

# Function to process the JSON files and generate CSV output
def process_files(file_names, jrdb_3d, jrdb_2d, out_path):
    for file_name in file_names:
        # Create file paths for 3D and 2D JSON files
        fname = os.path.join(jrdb_3d, file_name + '.json')
        twod_box = os.path.join(jrdb_2d, file_name + '.json')

        # Load data from 3D JSON file
        with open(fname) as json_file:
            orig_labels = json.load(json_file)

        # Load data from 2D JSON file
        with open(twod_box) as json_file_2dbox:
            orig_labels_2dbox = json.load(json_file_2dbox)

        # Create and open the CSV file for writing
        with open(os.path.join(out_path, file_name + '.csv'), 'w', newline='') as result:
            writer = csv.writer(result)

            # Iterate through 3D and 2D data to match and process
            for pcd_id, pcd_data in orig_labels['labels'].items():
                for twod_box_id, twod_box_data in orig_labels_2dbox['labels'].items():
                    # Downsample the frames and check for matching IDs
                    if int(pcd_id[:6]) % 6 == 0 and int(pcd_id[:6]) == int(twod_box_id[:6]):
                        for target in pcd_data:
                            for target_box in twod_box_data:
                                # Match 3D and 2D Bounding boxes based on pedestrian ID
                                if int(target['label_id'][11:]) == int(target_box['label_id'][11:]):
                                    # Write the combined data to the CSV file
                                    writer.writerow((
                                        int(pcd_id[:6]), int(target['label_id'][11:]),
                                        target['box']['cx'], target['box']['cy'],
                                        target['box']['h'], target['box']['w'],
                                        target['box']['l'], target['box']['rot_z'],
                                        target_box['box'][0], target_box['box'][1],
                                        target_box['box'][2], target_box['box'][3]
                                    ))
                                    break

def main():

    # Define paths and filenames
    parser = argparse.ArgumentParser()
    parser.add_argument('--jrdb_path', default='jrdb/test/',
                        help='CHANGE TO YOUR DATA PATH')
    parser.add_argument('--out_path', default='jrdb_raw/',
                        help='CHANGE TO YOUR DATA PATH')
    jrdb_3d = os.path.join(jrdb_path, 'labels_3d/')
    jrdb_2d = os.path.join(jrdb_path, 'labels_2d_stitched/')

    # List of file names to process
    file_names = [
        'bytes-cafe-2019-02-07_0',
        'huang-lane-2019-02-12_0',
        'gates-basement-elevators-2019-01-17_1',
        'hewlett-packard-intersection-2019-01-24_0',
        'jordan-hall-2019-04-22_0',
        'packard-poster-session-2019-03-20_2',
        'stlc-111-2019-04-19_0',
        'svl-meeting-gates-2-2019-04-08_0',
        'svl-meeting-gates-2-2019-04-08_1',
        'tressider-2019-03-16_1',
    ]

    process_files(file_names, jrdb_3d, jrdb_2d, out_path)

if __name__ == "__main__":
    main()

