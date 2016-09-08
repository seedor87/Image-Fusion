# import the necessary packages
import numpy as np
import argparse
import imutils
import glob
import cv2
import os
from zoom_staging import generate_lines
from PIL import Image
import sys
import traceback

# use stage zoom to fudge a zoomed image
im1 = Image.open('C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\Two Crop.png')
im1 = im1.resize((int(im1.size[0]*3.0), int(im1.size[1]*3.0)), Image.ANTIALIAS)



# im1 = cv2.imread('C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\Two Crop.png', 0)
im2 = cv2.imread('C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\Two Infrared.png', 0)
# im1 = generate_lines(im1, as_np_arr=True)
# im2 = generate_lines(im2, as_np_arr=True)

im1 = cv2.cvtColor(np.array(im1), cv2.COLOR_RGB2BGR)
cv2.imshow("Visualize", im1)
cv2.waitKey(0)

for i in np.arange(0, min(im1.shape[0], im1.shape[1]), 1):
    try:

        # re zoom the crop to be 'full - size'
        height, width, thow_away = im1.shape
        im1 = cv2.resize(im1, (width - i, height - i), interpolation = cv2.INTER_CUBIC)


        # load the image image, convert it to grayscale, and detect edges
        template = im1
        template = cv2.Canny(template, 50, 200)
        (tH, tW) = template.shape[:2]
        cv2.imshow("Template", template)

        image = im2
        gray = image
        found = None

        # loop over the scales of the image
        for scale in np.linspace(0.2, 1.0, 20)[::-1]:
            print "running"
            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break

            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            edged = cv2.Canny(resized, 50, 200)
            result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            clone = np.dstack([edged, edged, edged])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
                          (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
            cv2.imshow("Visualize", clone)
            cv2.waitKey(0)

            # if we have found a new maximum correlation value, then ipdate
            # the bookkeeping variable
            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

            # unpack the bookkeeping varaible and compute the (x, y) coordinates
            # of the bounding box based on the resized ratio
            (_, maxLoc, r) = found
            (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
            (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

            # draw a bounding box around the detected result and display the image
            cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
            cv2.imshow("Image", image)
            cv2.waitKey(0)
            break

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback)
        print "trying", im1.shape[1]-i, im1.shape[0]-i
        pass

print "failed"

# un zoom the crop to be 'full - size'
# im1 = im1.resize(im2.size, Image.ANTIALIAS)

# construct the argument parser and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-t", "--template", required=True, help="Path to template image")
# ap.add_argument("-i", "--images", required=True,
#     help="Path to images where template will be matched")
# ap.add_argument("-v", "--visualize",
#     help="Flag indicating whether or not to visualize each iteration")
# args = vars(ap.parse_args())

# load the image image, convert it to grayscale, and detect edges
template = im1
template = cv2.Canny(template, 50, 200)
(tH, tW) = template.shape[:2]
cv2.imshow("Template", template)

# loop over the images to find the template in
# for imagePath in glob.glob(args["images"]):
#     # load the image, convert it to grayscale, and initialize the
#     # bookkeeping variable to keep track of the matched region
#     image = cv2.imread(imagePath)
#     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#     found = None
#
#     # loop over the scales of the image
#     for scale in np.linspace(0.2, 1.0, 20)[::-1]:
#         # resize the image according to the scale, and keep track
#         # of the ratio of the resizing
#         resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
#         r = gray.shape[1] / float(resized.shape[1])
#
#         # if the resized image is smaller than the template, then break
#         # from the loop
#         if resized.shape[0] < tH or resized.shape[1] < tW:
#             break
#
#         # detect edges in the resized, grayscale image and apply template
#         # matching to find the template in the image
#         edged = cv2.Canny(resized, 50, 200)
#         result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
#         (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
#
#         # check to see if the iteration should be visualized
#         if args.get("visualize", False):
#             # draw a bounding box around the detected region
#             clone = np.dstack([edged, edged, edged])
#             cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
#                 (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
#             cv2.imshow("Visualize", clone)
#             cv2.waitKey(0)
#
#         # if we have found a new maximum correlation value, then ipdate
#         # the bookkeeping variable
#         if found is None or maxVal > found[0]:
#             found = (maxVal, maxLoc, r)

image = im2
gray = image
found = None

# loop over the scales of the image
for scale in np.linspace(0.2, 1.0, 20)[::-1]:
    # resize the image according to the scale, and keep track
    # of the ratio of the resizing
    resized = imutils.resize(gray, width = int(gray.shape[1] * scale))
    r = gray.shape[1] / float(resized.shape[1])

    # if the resized image is smaller than the template, then break
    # from the loop
    if resized.shape[0] < tH or resized.shape[1] < tW:
        break

    # detect edges in the resized, grayscale image and apply template
    # matching to find the template in the image
    edged = cv2.Canny(resized, 50, 200)
    result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)
    (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

    # check to see if the iteration should be visualized
    # if args.get("visualize", False):
    #     # draw a bounding box around the detected region
    #     clone = np.dstack([edged, edged, edged])
    #     cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
    #         (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
    #     cv2.imshow("Visualize", clone)
    #     cv2.waitKey(0)

    clone = np.dstack([edged, edged, edged])
    cv2.rectangle(clone, (maxLoc[0], maxLoc[1]),
        (maxLoc[0] + tW, maxLoc[1] + tH), (0, 0, 255), 2)
    cv2.imshow("Visualize", clone)
    cv2.waitKey(0)

    # if we have found a new maximum correlation value, then ipdate
    # the bookkeeping variable
    if found is None or maxVal > found[0]:
        found = (maxVal, maxLoc, r)

    # unpack the bookkeeping varaible and compute the (x, y) coordinates
    # of the bounding box based on the resized ratio
    (_, maxLoc, r) = found
    (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
    (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))

    # draw a bounding box around the detected result and display the image
    cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
    cv2.imshow("Image", image)
    cv2.waitKey(0)