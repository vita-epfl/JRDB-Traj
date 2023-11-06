cd jrdb_baselines
python -m trajnetbaselines.lstm.trainer --type social --n 10 --layer_dims 1024 --pool_dim 32 --hidden-dim 8 --lr 1e-4 --epochs 15 --path jrdb_traj --augment --loss 'L2' --output jrdb_traj_test
