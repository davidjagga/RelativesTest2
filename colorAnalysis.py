import cv2
import os,argparse,uuid,math
import mediapipe,cv2,filetype
import numpy as np
import webcolors
from sklearn.cluster import KMeans
from collections import Counter

def remove_black_areas(estimator_labels, estimator_cluster):
    """
    Remove out the black pixel from the selected area
    By default OpenCV does not handle transparent images and replaces those with zeros (black).
    Useful when thresholding is used in the image.
    """
    # Check for black
    hasBlack = False

    # Get the total number of occurance for each color
    occurance_counter = Counter(estimator_labels)

    # Quick lambda function to compare to lists
    compare = lambda x, y: Counter(x) == Counter(y)

    # Loop through the most common occuring color
    for x in occurance_counter.most_common(len(estimator_cluster)):

        # Quick List comprehension to convert each of RBG Numbers to int
        color = [int(i) for i in estimator_cluster[x[0]].tolist()]

        # Check if the color is [0,0,0] that if it is black
        if compare(color, [0, 0, 0]) == True:
            # delete the occurance
            del occurance_counter[x[0]]
            # remove the cluster
            hasBlack = True
            estimator_cluster = np.delete(estimator_cluster, x[0], 0)
            break

    return (occurance_counter, estimator_cluster, hasBlack)

def get_color_information(estimator_labels, estimator_cluster, hasThresholding=False):
    """
    Extract color information based on predictions coming from the clustering.
    Accept as input parameters estimator_labels (prediction labels)
                               estimator_cluster (cluster centroids)
                               has_thresholding (indicate whether a mask was used).
    Return an array the extracted colors.
    """
    # Variable to keep count of the occurance of each color predicted
    occurance_counter = None

    # Output list variable to return
    colorInformation = []

    # Check for Black
    hasBlack = False

    # If a mask needs to be applied, remove the black
    if hasThresholding == True:
        (occurance, cluster, black) = remove_black_areas(estimator_labels, estimator_cluster)
        occurance_counter = occurance
        estimator_cluster = cluster
        hasBlack = black
    else:
        occurance_counter = Counter(estimator_labels)

    # Get the total sum of all the predicted occurences
    totalOccurance = sum(occurance_counter.values())

    # Loop through all the predicted colors
    for x in occurance_counter.most_common(len(estimator_cluster)):
        index = (int(x[0]))

        # Quick fix for index out of bound when there is no threshold
        index = (index - 1) if ((hasThresholding & hasBlack) & (int(index) != 0)) else index

        # Get the color number into a list
        color = estimator_cluster[index].tolist()

        # Get the percentage of each color
        color_percentage = (x[1] / totalOccurance)

        # make the dictionay of the information
        colorInfo = {"cluster_index": index, "color": color, "color_percentage": color_percentage}

        # Add the dictionary to the list
        colorInformation.append(colorInfo)

    return colorInformation

def extract_dominant_colors(image, number_of_colors=5, hasThresholding=False):
    """
    Accept as input parameters image -> the input image in BGR format (8 bit / 3 channel)
                                     -> the number of colors to be extracted.
                                     -> hasThresholding indicate whether a thresholding mask was used.
    Leverage machine learning by using an unsupervised clustering algorithm (Kmeans Clustering) to cluster
    the image pixels data based on their RGB values.
    """
    # Quick Fix Increase cluster counter to neglect the black(Read Article)
    if hasThresholding == True:
        number_of_colors += 1

    # Taking Copy of the image
    img = image.copy()

    # Convert Image into RGB Colours Space
    #img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Reshape Image
    img = img.reshape((img.shape[0] * img.shape[1]), 3)

    # Initiate KMeans Object
    estimator = KMeans(n_clusters=number_of_colors, random_state=0)

    # Fit the image
    estimator.fit(img)

    # Get Colour Information
    colorInformation = get_color_information(estimator.labels_, estimator.cluster_centers_, hasThresholding)

    return colorInformation

def get_top_dominant_color(dominant_colors):
    """
    Return the top dominant color out of the dominant colors
    """
    def find_closest_color(req_color):
        # This is the function which converts an RGB pixel to a color name
        min_colours = {}
        for name, key in webcolors.CSS3_HEX_TO_NAMES.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(name)
            rd = (r_c - req_color[0]) ** 2
            gd = (g_c - req_color[1]) ** 2
            bd = (b_c - req_color[2]) ** 2
            min_colours[(rd + gd + bd)] = key
            closest_name = min_colours[min(min_colours.keys())]
        return closest_name

    #print(dominant_colors)
    #print(dominant_colors[0].get('cluster_index'))
    #print(dominant_colors[0].get('color'))
    #print(dominant_colors[0].get('color_percentage'))

    color_value = (
                  int(dominant_colors[0].get('color')[2])
                , int(dominant_colors[0].get('color')[1])
                , int(dominant_colors[0].get('color')[0])
                )

    closest_color_name = find_closest_color(
        (
            int(dominant_colors[0].get('color')[0])
           ,int(dominant_colors[0].get('color')[1])
           ,int(dominant_colors[0].get('color')[2])
        )
    )
    color_score = round( dominant_colors[0].get('color_percentage') * 100,2)
    return color_value, closest_color_name, color_score

if __name__ == '__main__':
    img = cv2.imread('files1/eye4.png')
    for d in extract_dominant_colors(img):
        print(d)
    cv2.imshow('eye', img)
    cv2.waitKey(0)