cd train
python -m trajnetbaselines.lstm.trainer --type social --layer_dims 1024 --path jrdb_track_3dbb_2dbb --loss 'L2' --output baseline_aug --epochs 15 --lr 1e-4 --hidden-dim 8 --pool_dim 32 --n 10 --augment
