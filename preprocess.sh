cd trajnetplusplusdataset
python -m trajnetdataset.convert_train --acceptance 1.0 1.0 1.0 1.0 --train_fraction 1.0 --val_fraction 0.0 --fps 2.5 --obs_len 9 --pred_len 12
python -m trajnetdataset.convert_test --acceptance 1.0 1.0 1.0 1.0 --train_fraction 0.0 --val_fraction 0.0 --fps 2.5 --obs_len 9 --pred_len 0 --chunk_stride 1

#This step will give you the training and testing data under 'output' folder, then you need to move the data to the following
mv output ../jrdb_baselines/DATA_BLOCK/jrdb_traj
