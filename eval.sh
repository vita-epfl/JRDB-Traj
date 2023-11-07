# You can evaluate your saved model with the following command.
# We have also provided the saved checkpoints in the release section. In order to evaluate it, you should put the saved '.pkl' file in the 'jrdb_baselines/OUTPUT_BLOCK/jrdb_traj'
cd jrdb_baselines
python -m trajnetbaselines.lstm.trajnet_evaluator --path jrdb_traj --output OUTPUT_BLOCK/jrdb_traj/lstm_social_baseline.pkl
rm -r DATA_BLOCK/jrdb_traj/test_pred/lstm_social_baseline_modes1/temp

mv DATA_BLOCK/jrdb_traj/test_pred/lstm_social_baseline_modes1/jrdb_submission ..
