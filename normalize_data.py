# -*- coding: utf-8 -*-
"""
######################################################################################################################################
This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License. To view a copy of this license,
visit http://creativecommons.org/licenses/by-nc-sa/4.0/ or send a letter to Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.

Any publications arising from the use of this software, including but
not limited to academic journal and conference publications, technical
reports and manuals, must cite at least one of the following works:

Revisiting Data Normalization for Appearance-Based Gaze Estimation
Xucong Zhang, Yusuke Sugano, Andreas Bulling
in Proc. International Symposium on Eye Tracking Research and Applications (ETRA), 2018
######################################################################################################################################
"""

import os
import cv2
import numpy as np
import csv
import scipy.io as sio

def draw_gaze(image_in, pitchyaw, thickness=2, color=(0, 0, 255)):
    """Draw gaze angle on given image with a given eye positions."""
    image_out = image_in
    (h, w) = image_in.shape[:2]
    length = np.min([h, w]) / 2.0
    pos = (int(w / 2.0), int(h / 2.0))
    if len(image_out.shape) == 2 or image_out.shape[2] == 1:  # to draw on the image, we need to convert to RGB
        image_out = cv2.cvtColor(image_out, cv2.COLOR_GRAY2BGR)
    dx = -length * np.sin(pitchyaw[1]) * np.cos(pitchyaw[0])
    dy = -length * np.sin(pitchyaw[0])
    cv2.arrowedLine(image_out, tuple(np.round(pos).astype(int)),
                   tuple(np.round([pos[0] + dx, pos[1] + dy]).astype(int)), color,
                   thickness, cv2.LINE_AA, tipLength=0.2)

    return image_out

def estimateHeadPose(landmarks, face_model, camera, distortion, iterate=True):
    ret, rvec, tvec = cv2.solvePnP(face_model, landmarks, camera, distortion, flags=cv2.SOLVEPNP_EPNP)

    ## further optimize
    if iterate:
        ret, rvec, tvec = cv2.solvePnP(face_model, landmarks, camera, distortion, rvec, tvec, True)

    return rvec, tvec

def normalizeData(img, face, hr, ht, gc, cam):
    ## normalized camera parameters
    # To change the image size, you need to modify the roiSize parameter, and then adjust focal_norm and distance_norm accordingly.
    focal_norm = 960 # focal length of normalized camera
    distance_norm = 600 # normalized distance between eye and camera
    roiSize = (60, 36) # size of cropped eye image

    img_u = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to grayscale, feel free to remove it.

    ## compute estimated 3D positions of the landmarks
    ht = ht.reshape((3,1)) # head translation vector
    gc = gc.reshape((3,1)) # gaze direction vector
    hR = cv2.Rodrigues(hr)[0] # rotation matrix
    Fc = np.dot(hR, face) + ht # 3D positions of facial landmarks
    re = 0.5*(Fc[:,0] + Fc[:,1]).reshape((3,1)) # center of left eye
    le = 0.5*(Fc[:,2] + Fc[:,3]).reshape((3,1)) # center of right eye
    
    ## normalize each eye
    data = []  # variable to save normalized data
    for et in [re, le]:  ## right eye first and then left eye
        ## ---------- normalize image ----------
        distance = np.linalg.norm(et) # actual distance between eye and original camera
        
        z_scale = distance_norm/distance
        cam_norm = np.array([  # camera matrix of normalized camera
            [focal_norm, 0, roiSize[0]/2],
            [0, focal_norm, roiSize[1]/2],
            [0, 0, 1.0],
        ])
        S = np.array([ # scaling matrix
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, z_scale],
        ])
        
        hRx = hR[:,0]
        forward = (et/distance).reshape(3)
        down = np.cross(forward, hRx)
        down /= np.linalg.norm(down)
        right = np.cross(down, forward)
        right /= np.linalg.norm(right)
        R = np.c_[right, down, forward].T # rotation matrix R
        
        W = np.dot(np.dot(cam_norm, S), np.dot(R, np.linalg.inv(cam))) # transformation matrix
        
        img_warped = cv2.warpPerspective(img_u, W, roiSize) # image normalization
        img_warped = cv2.equalizeHist(img_warped)  # a post-processing step, feel free to remove it.
        
        ## ---------- normalize rotation ----------
        hR_norm = np.dot(R, hR) # rotation matrix in normalized space
        hr_norm = cv2.Rodrigues(hR_norm)[0] # convert rotation matrix to rotation vectors
        
        ## ---------- normalize gaze vector ----------
        gc_normalized = gc - et # gaze vector
        # For new data normalization in our ETRA 2018 paper, scaling is not applied to gaze direction, so here is only R applied.
        # For original data normalization, the following line should be:
        # "M = np.dot(S,R)
        # gc_normalized = np.dot(M, gc_normalized)"
        gc_normalized = np.dot(R, gc_normalized)
        gc_normalized = gc_normalized/np.linalg.norm(gc_normalized)  # normalize gaze vector, it is important!
        
        data.append([img_warped, hr_norm, gc_normalized])
        
    return data

if __name__ == '__main__':
    ## load calibration data, these paramters can be obtained by camera calibration functions in OpenCV
    fid = cv2.FileStorage('./data/calibration/cameraCalib.xml', cv2.FileStorage_READ)
    camera_matrix = fid.getNode("camera_matrix").mat()
    camera_distortion = fid.getNode("cam_distortion").mat()

    # load example
    filepath = os.path.join('./data/example/day01_0087.jpg')
    img_original = cv2.imread(filepath)
    img = cv2.undistort(img_original, camera_matrix, camera_distortion)
    # load the detected facial landmarks
    # this code does not contain facial landmark detection
    landmarks = np.array([[551, 408], [603, 405], [698, 398], [755, 393], [603, 566], [724, 557]])

    # load the generic face model, which includes 6 facial landmarks: four eye corners and two mouth corners
    face = np.loadtxt('./data/faceModelGeneric.txt')
    num_pts = face.shape[1]
    facePts = face.T.reshape(num_pts, 1, 3)

    # estimate head pose
    landmarks = landmarks.astype(np.float32)
    landmarks = landmarks.reshape(num_pts, 1, 2)
    hr, ht = estimateHeadPose(landmarks, facePts, camera_matrix, camera_distortion)

    # load 3D gaze target position in camera coordinate system
    gc = np.array([-127.790719, 4.621111, -12.025310])  # 3D gaze taraget position

    # data normalization for left and right eye image
    data = normalizeData(img, face, hr, ht, gc, camera_matrix)

    # show results of right eye image
    label = data[0][2]
    head_pose_right = data[0][1]
    head_pose_left = data[1][1]
    gaze_right = data[0][2]
    gaze_left = data[1][2]
    print('The label is: ', label)
    # convert label to euler angle
    gaze_theta = np.arcsin((-1) * gaze_right[1])
    gaze_phi = np.arctan2((-1) * gaze_right[0], (-1) * gaze_right[2])

    # show normalized image
    img_normalized = data[0][0]
    img_normalized = draw_gaze(img_normalized, np.array([gaze_theta[0], gaze_phi[0]]))
    cv2.imshow('image', img_normalized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()