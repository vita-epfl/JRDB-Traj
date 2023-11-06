# JRDB-Traj
JRDB Data Preprocessing and Trajectory Prediction Baselines 

## Prerequisites
Install requirements with `bash requirement.sh`.

## Repository Overview
The pipeline encompasses four key steps:

1. `bash dataload.sh`: This script preprocesses the JRDB dataset, extracting trajectories for further analysis.
2. `bash preprocess.sh`: Utilizing the TrajNet++ benchmark, this script categorizes '.csv' files and generates '.ndjson' files for the next step.
3. `bash train.sh`: This script train baseline trajectory prediction models using the meticulously prepared data.
4. `bash eval.sh`: This script will generate predictions in JRDB leaderboard format.


## Work in Progress
This repository is being updated so please stay tuned!
