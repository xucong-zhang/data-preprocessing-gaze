# Data Normalization
Updated code for paper "Revisiting Data Normalization for Appearance-Based Gaze Estimation", ETRA 2018.

## Update item
Comapring to the [original website](https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/research/gaze-based-human-computer-interaction/revisiting-data-normalization-for-appearance-based-gaze-estimation), we updated the following items.

[25th May, 2023]:

* Bug fixed in the output line. 
* Change the camera calibration file from .mat to .xml. 
* Change the face model file from .mat to .txt file. 
* Add a draw gaze function to visualize the gaze direction.

## Requirements
Numpy\
Opencv-Python

## History of data normalization for gaze estimation
*Written by [Xucong Zhang](https://www.ccmitss.com/zhang)*

The original idea of data normalization was proposed in [1] as a way of synthesizing eye images, at which time it was referred to as "rectify" eye images. It was further developed in [2] for the same purpose with detailed steps. Introduced by Yusuke Sugano, we used the same operations in [2] for the pre-processing of MPIIGaze dataset [3], and we gave the name of this pre-processing as "data normalization". I admit that it is not a good name.

Around 2017, we sensed that the scaling operation might not be used for the gaze direction normalization. Mathematically, the gaze direction should also be scaled given the whole normalized space is scaled by the focal length of the virtual camera, instead of physically moving the virtual camera towards the eye. However, we do not need to scale the gaze direction if we assume the eye is a 2D planar, given the long distance between the real camera and the eye. After multiple discussions at length, we decided to verify our ideas with experiments, which result in an ETRA paper [4] concluded that we should NOT apply the scaling factor to the gaze direction. In short, the absolute gaze estimation error would be scaled according to the "real distance between the real camera and eye" and the "distance between the virtual camera and eye". For the MPIIGaze and MPIIFaceGaze datasets, the gaze estimation error becomes smaller if the scaling factor is applied during the data normalization. 

We were preparing the camera-ready version of the MPIIFaceGaze dataset paper [5] when we realized this issue. However, all experiments were done with the scaling factor already. Therefore, we converted the results from the normalized space to the original camera space to cancel the scaling factor. Technically, it is not equal to training a model without the scaling factor in the gaze direction space. We released the normalized data for MPIIFaceGaze without the scaling factor on the gaze direction on [our website](https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/research/gaze-based-human-computer-interaction/its-written-all-over-your-face-full-face-appearance-based-gaze-estimation/). It was chaos and caused unnecessary confusion for other people.

After 2017, experiments on the MPIIFaceGaze dataset on all of my gaze estimation papers (listed on my personal webpage and google scholar) were conducted on the normalized MPIIFaceGaze dataset downloaded from [our website](https://www.mpi-inf.mpg.de/departments/computer-vision-and-machine-learning/research/gaze-based-human-computer-interaction/its-written-all-over-your-face-full-face-appearance-based-gaze-estimation/), which does not use the scaling factor on the gaze direction. We directly compare our later methods with the number reported in [5] for the MPIIFaceGaze dataset due to the fact that these numbers are in the original camera space. However, we did not update experiment results for the MPIIGaze dataset [3] and the TPAMI extension [6], since it was already published. In other words, the gaze estimation errors reported in MPIIGaze papers [3] and [6] are in the scaled normalized space, and they are not directly comparable to results in the MPIIFaceGaze paper [5] which are in the original camera space. BTW, the main difference between MPIIGaze and MPIIFaceGaze is that MPIIGaze only has the eye region, and MPIIFaceGaze has the full-face images.

Seonwook Park improved the data normalization with a better head pose estimation in [7], and he made effort to make the GazeCapture dataset [8] to a the same normalized space. The pre-processing code can be found in the [Github code](https://github.com/swook/faze_preprocess/tree/5c33caaa1bc271a8d6aad21837e334108f293683).

In principle, you are free to develop your gaze estimation method with any pre-processing in your favor, as long as the comparison of different methods used the same process. Using data normalization or not, using scaling factor on gaze direction or not, does not affect the performance ranking of methods. It only causes problems when comparing methods with different pre-processing that we should pay attention to.


### References
[1] Head Pose-Free Appearance-Based Gaze Sensing via Eye Image Synthesis. Lu et al. ICPR 2012.\
[2] Learning-by-Synthesis for Appearance-based 3D Gaze Estimation. Sugano et al. CVPR 2014.\
[3] Appearance-Based Gaze Estimation in the Wild. Zhang et al. CVPR 2015.\
[4] Revisiting Data Normalization for Appearance-Based Gaze Estimation. Zhang et al. ETRA 2018.\
[5] It’s Written All Over Your Face: Full-Face Appearance-Based Gaze Estimation. Zhang et al. CVPR workshop 2017.\
[6] MPIIGaze: Real-World Dataset and Deep Appearance-Based Gaze Estimation. Zhang et al. TPAMI 2017.\
[7] Few-Shot Adaptive Gaze Estimation. Park et al. ICCV 2019.\
[8] Eye Tracking for Everyone. Krafka et al. CVPR 2016.

## License
The code is under the license of [CC BY-NC-SA 4.0 license](https://creativecommons.org/licenses/by-nc-sa/4.0/)

## Citation
Please cite the following publication if you use the code-base in your research:

    @inproceedings{zhang2018revisiting,
        title={Revisiting data normalization for appearance-based gaze estimation},
        author={Zhang, Xucong and Sugano, Yusuke and Bulling, Andreas},
        booktitle={Proceedings of the 2018 ACM symposium on eye tracking research \& applications},
        pages={1--9},
        year={2018}
    }

