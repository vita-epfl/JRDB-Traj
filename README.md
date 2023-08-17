# JRDB-Traj
JRDB Data Preprocessing and Trajectory Prediction Baselines 


## Repository Overview
The pipeline encompasses three key steps:

1. `traj_extractor.py`: This script preprocesses the JRDB dataset, extracting trajectories for further analysis.
2. `python -m trajnetdataset.convert --acceptance 1.0 1.0 1.0 1.0 --train_fraction 1.0 --val_fraction 0.0 --fps 2.5 --obs_len 9 --pred_len 12 `: In trajnetplusplusdataset folder, use this command to categorizes '.csv' files and generates '.ndjson' files for enhanced data representation.
3. `train.py`: This script train baseline trajectory prediction models using the meticulously prepared data.

## Work in Progress
This repository is being updated so stay tuned!
