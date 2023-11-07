# After extracting the raw data, you will get the extracted data located at the output_path you set.
jrdb_path="<your_data_path>/train_dataset/labels/"
# You should put the "Test Trackings" results downloaded from the JRDB webpage in the following address
jrdb_test_path="<your_data_path>/test_trackings/"

out_path="OUT_tmp"

python train_traj_extractor.py --out_path $out_path  --jrdb_path $jrdb_path 
python test_traj_extractor.py --out_path $out_path  --jrdb_path $jrdb_test_path 


# There will also be two temp folders named 'temp' and 'conf_temp', can be removed. 
rm -r $out_path/temp $out_path/conf_temp

# Move the extracted data to 'trajnetplusplusdataset/data/raw/'.)
mv $out_path trajnetplusplusdataset/data/raw
