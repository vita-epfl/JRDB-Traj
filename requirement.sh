cd jrdb_baselines/ 
pip install -e .
cd ../trajnetplusplusdataset/ 
pip install -e .
pip install -e '.[test, plot]'
!rm -rf Python_RVO2-main/
wget https://github.com/sybrenstuvel/Python-RVO2/archive/master.zip
unzip master.zip
rm master.zip
cd Python-RVO2-main/
pip install cmake
pip install cython
python setup.py build
python setup.py install
cd ../
wget https://github.com/svenkreiss/socialforce/archive/refs/heads/main.zip
unzip main.zip
rm main.zip
cd socialforce-main/
pip install -e .
cd ../
cd ../
pip install python-json-logger
pip install joblib
pip install tqdm
