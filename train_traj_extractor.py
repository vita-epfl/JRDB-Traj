import numpy as np
import json
import csv
import os
from csv import reader, writer
import argparse


# Function to process the JSON files and generate CSV output
def process_files(file_names, jrdb_3d, out_path):
    for file_name in file_names:
        # Create file paths for 3D and 2D JSON files
        fname = os.path.join(jrdb_3d, file_name + '.json')

        # Load data from 3D JSON file
        with open(fname) as json_file:
            orig_labels = json.load(json_file)

        # Create and open the CSV file for writing
        with open(os.path.join(out_path, file_name + '.csv'), 'w', newline='') as result:
            writer = csv.writer(result)

            # Iterate through 3D and 2D data to match and process
            for pcd_id, pcd_data in orig_labels['labels'].items():
                # for twod_box_id, twod_box_data in orig_labels_2dbox['labels'].items():
                    # Downsample the frames and check for matching IDs
                    if int(pcd_id[:6]) % 6 == 0:
                        for target in pcd_data:
                                    # Write the combined data to the CSV file
                                    writer.writerow((
                                        int(pcd_id[:6]), int(target['label_id'][11:]),
                                        target['box']['cx'], target['box']['cy'],
                                    ))

def add_confidence_score(input_file, output_file):
    with open(input_file, 'r') as input_csv, open(output_file, 'w', newline='') as output_csv:
        csv_reader = reader(input_csv)
        csv_writer = writer(output_csv)
        for row in csv_reader:
            row.insert(4, 1)
            csv_writer.writerow(row)

def extract_pedestrian_ids(input_file):
    p_id_list = []
    with open(input_file, 'r') as input_csv:
        csv_reader = reader(input_csv)
        for row in csv_reader:
            if row[1] not in p_id_list:
                p_id_list.append(row[1])
    return p_id_list

def add_nan(file_name, output_path, conf_path, nan_path):
    input_path = os.path.join(output_path, file_name + '.csv')
    conf_output_path = os.path.join(conf_path, file_name + '.csv')
    nan_output_path = os.path.join(nan_path, file_name + '.csv')

    add_confidence_score(input_path, conf_output_path)
    p_id_list = extract_pedestrian_ids(conf_output_path)

    with open(conf_output_path, 'r') as input_csv, open(nan_output_path, 'w', newline='') as output_csv:
        csv_reader = reader(input_csv)
        csv_writer = writer(output_csv, delimiter=',')
        p_id_list_temp = []
        last_frame_id = -1
        for row in csv_reader:
            if int(row[0]) == last_frame_id:
                p_id_list_temp.append(row[1])
                csv_writer.writerow(row)
            else:
                nan_id = [x for x in p_id_list if x not in p_id_list_temp]
                if nan_id and last_frame_id != -1:
                    for i in nan_id:
                        row_temp = [last_frame_id, i, 'nan', 'nan', 0]
                        csv_writer.writerow(row_temp)
                p_id_list_temp.clear()
                p_id_list_temp.append(row[1])
                last_frame_id = int(row[0])
                csv_writer.writerow(row)

def main(out_path, jrdb_path):

    temp_down_sample_path = os.path.join(out_path,'temp/')
    conf_path = os.path.join(out_path,'conf_temp/')
    nan_path = out_path
    jrdb_3d = os.path.join(jrdb_path, 'labels_3d/')

    # Check if the path exists
    if not os.path.exists(conf_path):
        os.makedirs(conf_path)
    if not os.path.exists(temp_down_sample_path):
        os.makedirs(temp_down_sample_path)

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
        'gates-ai-lab-2019-02-08_0',
        'packard-poster-session-2019-03-20_1',
        'tressider-2019-03-16_0',
    ]
    print('Extracting trajectories (1/2) ...')
    process_files(file_names, jrdb_3d, temp_down_sample_path)
    
    print('Add nan to missed ones (2/2) ...')
    for file_name in file_names:
        add_nan(file_name, temp_down_sample_path, conf_path, nan_path)
    print('All done!')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_path', type=str, help='Output data path')
    parser.add_argument('--jrdb_path', type=str, help='JRDB data path')
    args = parser.parse_args()

    main(args.out_path, args.jrdb_path)

