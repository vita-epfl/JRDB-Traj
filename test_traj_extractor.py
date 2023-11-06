import numpy as np
import csv
import os
import argparse

def create_directories(output_path, down_sample_path, conf_path):
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.exists(down_sample_path):
        os.makedirs(down_sample_path)
    if not os.path.exists(conf_path):
        os.makedirs(conf_path)

def process_jrdb_data(jrdb_path, output_path, down_sample_path, conf_path):
    # List of file names, shifts, benchmark frames, and final frames
    file_names = [
            ######alphabeta-order of test set
            'cubberly-auditorium-2019-04-22_1',
            'discovery-walk-2019-02-28_0',
            'discovery-walk-2019-02-28_1',
            'food-trucks-2019-02-12_0',
            'gates-ai-lab-2019-04-17_0',
            'gates-basement-elevators-2019-01-17_0',
            'gates-foyer-2019-01-17_0',
            'gates-to-clark-2019-02-28_0',
            'hewlett-class-2019-01-23_0',
            'hewlett-class-2019-01-23_1',
            'huang-2-2019-01-25_1',
            'huang-intersection-2019-01-22_0',
            'indoor-coupa-cafe-2019-02-06_0',
            'lomita-serra-intersection-2019-01-30_0',
            'meyer-green-2019-03-16_1',
            'nvidia-aud-2019-01-25_0',
            'nvidia-aud-2019-04-18_1',
            'nvidia-aud-2019-04-18_2',
            'outdoor-coupa-cafe-2019-02-06_0',
            'quarry-road-2019-02-28_0',
            'serra-street-2019-01-30_0',
            'stlc-111-2019-04-19_1',
            'stlc-111-2019-04-19_2',
            'tressider-2019-03-16_2',
            'tressider-2019-04-26_0',
            'tressider-2019-04-26_1',
            'tressider-2019-04-26_3'
    ]

    shifts = [2, 0, 4, 5, 3, 5, 0, 2, 2, 0, 2, 4, 1, 0, 3, 4, 2, 1, 0, 5, 0, 1, 0, 1, 3, 2, 4]
    benchmark_frames = [1030, 666, 740, 1555, 1173, 589, 1614, 376, 742, 738, 520, 1610, 1619, 1128, 957, 1178, 454, 449,
                        1602, 385, 1350, 449, 426, 593, 1173, 1612, 1610]

    for dataset_index, file_name in enumerate(file_names):
        shift = shifts[dataset_index]
        fname = f"{jrdb_path}{str(dataset_index).zfill(4)}.txt"

        # Delete the 'pedestrian' column and convert data to float
        trajs = np.loadtxt(fname, dtype=str)
        trajs = np.delete(trajs, 2, 1)
        trajs = np.array(trajs).astype(float)

        # Downsample and select specific frames for leaderboard
        with open(f"{down_sample_path}{file_name}.csv", 'w', newline='') as result:
            writer = csv.writer(result)
            for row in range(trajs.shape[0]):
                if (trajs[row, 0] + shift) < benchmark_frames[dataset_index]:
                    continue
                if (trajs[row, 0] + shift) % 6 == 0:
                    writer.writerow((int(trajs[row, 0]), int(trajs[row, 1]), trajs[row, -2], trajs[row, -1]))

        # Add confidence score column
        with open(f"{down_sample_path}{file_name}.csv") as input_file, \
                open(f"{conf_path}{file_name}.csv", 'w', newline='') as output_file:
            csv_reader = csv.reader(input_file)
            csv_writer = csv.writer(output_file)
            for row in csv_reader:
                row.insert(4, 1)
                csv_writer.writerow(row)

        p_id_list = []

        # Get all pedestrian IDs in this video
        with open(f"{conf_path}{file_name}.csv") as input_file:
            csv_reader = csv.reader(input_file)
            for row_temp in csv_reader:
                if row_temp[1] in p_id_list:
                    pass
                else:
                    p_id_list.append(row_temp[1])

        # Add 'nan' to missed pedestrians
        with open(f"{conf_path}{file_name}.csv") as input_file, \
                open(f"{output_path}{file_name}.csv", 'w', newline='') as output_file:
            csv_reader = csv.reader(input_file)
            csv_writer = csv.writer(output_file, delimiter=',')
            last_frame_id = benchmark_frames[dataset_index]
            p_id_list_temp = []

            for row in csv_reader:
                if int(row[0]) == last_frame_id:
                    p_id_list_temp.append(row[1])
                    csv_writer.writerow(row)
                else:
                    nan_id = [x for x in p_id_list if x not in p_id_list_temp]
                    if len(nan_id) != 0:
                        for i in nan_id:
                            row_temp = [last_frame_id, i, 'nan', 'nan', 0]
                            csv_writer.writerow(row_temp)
                    p_id_list_temp.clear()
                    p_id_list_temp.append(row[1])
                    last_frame_id = int(row[0])
                    csv_writer.writerow(row)

def main(out_path, jrdb_path):

    down_sample_path = os.path.join(out_path,'temp/')
    conf_path = os.path.join(out_path, 'conf_temp/')
    

    create_directories(out_path, down_sample_path, conf_path)
    process_jrdb_data(jrdb_path, out_path, down_sample_path, conf_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--out_path', type=str, help='Output data path')
    parser.add_argument('--jrdb_test_path', type=str, help='JRDB test data path')
    args = parser.parse_args()

    main(args.out_path, args.jrdb_test_path)
