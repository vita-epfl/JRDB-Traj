NEW: Converting new external dataset into TrajNet++ format. `Tutorial <https://thedebugger811.github.io/posts/2020/10/data_conversion/>`_

Install
-------

.. code-block:: sh

    pip install -e '.[test,plot]'
    pylint trajnetdataset
    pytest


Prepare Data
------------

Existing real world data:

.. code-block::

    data/
        data_arxiepiskopi.rar
        data_university_students.rar
        data_zara.rar
        ewap_dataset_light.tgz
        # 3DMOT2015Labels  # from: https://motchallenge.net/data/3DMOT2015Labels.zip (video file at http://cs.binghamton.edu/~mrldata/public/PETS2009/S2_L1.tar.bz2)
        Train.zip  # from trajnet.epfl.ch
        cvpr2015_pedestrianWalkingPathDataset.rar  # from http://www.ee.cuhk.edu.hk/~syi/ (website not accessible but data are also here: https://www.dropbox.com/s/7y90xsxq0l0yv8d/cvpr2015_pedestrianWalkingPathDataset.rar?dl=0.+63)
        cff_dataset.zip # from https://www.dropbox.com/s/cnnk2ofreeoshuz/cff_dataset.zip?dl=0

Extract:

.. code-block:: sh

    # biwi
    mkdir -p data/raw/biwi
    tar -xzf data/ewap_dataset_light.tgz --strip-components=1 -C data/raw/biwi

    # crowds
    mkdir -p data/raw/crowds
    unrar e data/data_arxiepiskopi.rar data/raw/crowds
    unrar e data/data_university_students.rar data/raw/crowds
    unrar e data/data_zara.rar data/raw/crowds

    # cff
    mkdir -p data/raw/cff_dataset
    unzip data/cff_dataset.zip -d data/raw/
    rm -r data/raw/__MACOSX

    # Wildtrack: https://www.epfl.ch/labs/cvlab/data/data-wildtrack/
    mkdir -p data/raw/wildtrack
    unzip data/Wildtrack_dataset_full.zip -d data/raw/wildtrack

    # L-CAS: https://drive.google.com/drive/folders/1CPV9XeJsZzvtTxPQ9u1ppLGs_29e-XdQ
    mkdir -p data/raw/lcas
    cp data/lcas_pedestrian_dataset/minerva/train/data.csv data/raw/lcas

    # pedestrian walking dataset
    mkdir -p data/raw/syi
    unrar e data/cvpr2015_pedestrianWalkingPathDataset.rar data/raw/syi

    PETS09 S2L1 ground truth -- not used because people behavior is not normal
    mkdir -p data/raw/mot
    unzip data/3DMOT2015Labels.zip -d data/
    cp data/3DMOT2015Labels/train/PETS09-S2L1/gt/gt.txt data/raw/mot/pets2009_s2l1.txt

    # Edinburgh Informatics Forum tracker -- not used because tracks are not good enough
    mkdir -p data/raw/edinburgh
    wget -i edinburgh_informatics_forum_urls.txt -P data/raw/edinburgh/

Prepare synthetic data:

.. code-block:: sh

    python -m trajnetdataset.controlled_data

Help menu for generating diverse synthetic data:
``python -m trajnetdataset.controlled_data --help``

Run
---

.. code-block:: sh

    python -m trajnetdataset.convert

The above command performs the following operations:

* Step 1. readers.py: reads the raw data files and converts them to trackrows in .ndjson format
* Step 2. scene.py: prepares different scenes given the obtained trackrows
* Step 3. get_type.py: categorizes each scene based on our defined trajectory categorization

.. code-block:: sh

    # create plots to check new dataset
    python -m trajnetplusplustools.summarize output/train/*.ndjson

    # obtain new dataset statistics
    python -m trajnetplusplustools.dataset_stats output/train/*.ndjson

    # visualize sample scenes
    python -m trajnetplusplustools.trajectories output/train/*.ndjson

Difference in generated data
----------------------------

* partial tracks are now included (for correct occupancy maps)
* pedestrians that appear in multiple chunks had the same id before (might be a problem for some input readers)
* explicit index of scenes with annotation of the primary pedestrian

# * the primary pedestrian has to move by more than 1 meter
* at one point, the primary pedestrian has to be <3m away from another pedestrian

Citation
========

If you find this code useful in your research then please cite

.. code-block::

    @inproceedings{Kothari2020HumanTF,
      title={Human Trajectory Forecasting in Crowds: A Deep Learning Perspective},
      author={Parth Kothari and Sven Kreiss and Alexandre Alahi},
      year={2020}
    }

References
----------
* ``eth``: 

.. code-block::

    @article{Pellegrini2009YoullNW,
      title={You'll never walk alone: Modeling social behavior for multi-target tracking},
      author={Stefano Pellegrini and Andreas Ess and Konrad Schindler and Luc Van Gool},
      journal={2009 IEEE 12th International Conference on Computer Vision},
      year={2009},
      pages={261-268}
    }
    
* ``ucy``:

.. code-block::

    @article{Lerner2007CrowdsBE,
      title={Crowds by Example},
      author={Alon Lerner and Yiorgos Chrysanthou and Dani Lischinski},
      journal={Comput. Graph. Forum},
      year={2007},
      volume={26},
      pages={655-664}
    }

* ``wildtrack``:

.. code-block::

    @inproceedings{chavdarova-et-al-2018,
        author = "Chavdarova, T. and Baqué, P. and Bouquet, S. and Maksai, A. and Jose, C. and Bagautdinov, T. and Lettry, L. and Fua, P. and Van Gool, L. and Fleuret, F.",
        title = {{WILDTRACK}: A Multi-camera {HD} Dataset for Dense Unscripted Pedestrian Detection},
        journal = "Proceedings of the IEEE international conference on Computer Vision and Pattern Recognition (CVPR)",
        year = 2018,
    }

* ``L-CAS``:

.. code-block::

    @article{Sun20173DOFPT,
      title={3DOF Pedestrian Trajectory Prediction Learned from Long-Term Autonomous Mobile Robot Deployment Data},
      author={Li Sun and Zhi Yan and Sergi Molina Mellado and Marc Hanheide and Tom Duckett},
      journal={2018 IEEE International Conference on Robotics and Automation (ICRA)},
      year={2017},
      pages={1-7}
    }

* ``CFF``:

.. code-block::

  @article{Alahi2014SociallyAwareLC,
      title={Socially-Aware Large-Scale Crowd Forecasting},
      author={Alexandre Alahi and Vignesh Ramanathan and Fei-Fei Li},
      journal={2014 IEEE Conference on Computer Vision and Pattern Recognition},
      year={2014},
      pages={2211-2218}
    }
    
* ``syi``: Shuai Yi, Hongsheng Li, and Xiaogang Wang. Understanding Pedestrian Behaviors from Stationary Crowd Groups. In Proceedings of IEEE Conference on Computer Vision and Pattern Recognition (CVPR 2015).
* ``edinburgh``: B. Majecka, "Statistical models of pedestrian behaviour in the Forum", MSc Dissertation, School of Informatics, University of Edinburgh, 2009.
