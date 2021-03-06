import cv2, os
from PIL import Image, ImageDraw
import sys
import numpy as np

cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
inp_dir = os.path.join(cur_dir, 'Input')
demo_dir = os.path.join(cur_dir, 'Merging', 'demo_images')

sub_img_path = os.path.join(inp_dir, "homography_demo_in1_file.jpg")
base_img_path = os.path.join(inp_dir, "homography_demo_in2_file.jpg")
res_img_path = os.path.join(inp_dir, 'homography_demo_result_file.jpg')

def feature_detection():

    img_path = 'C:\Users\Bob S\PycharmProjects\Image-Fusion\Input\\One Infrared.jpg'
    orb =  cv2.ORB_create()
    img = cv2.imread(img_path)

    kp, des = orb.detectAndCompute(img, None)

    print kp
    print des

def apply_border(img, points, color=(255,0,0), border=3):

    draw = ImageDraw.Draw(img)

    shifted = points[1:] + points[:1]
    lis = zip(points, shifted)

    for pair in lis:
        draw.line((pair[0][0], pair[0][1], pair[1][0], pair[1][1]), fill=color, width=border)

    return img

def main(demo=None):

    show = []
    sub_img = cv2.imread(sub_img_path)
    tot_img = cv2.imread(base_img_path)

    ############################

    im = Image.open(sub_img_path)

    top_left = [0,0]
    top_right = [im.size[0],0]
    bottom_right= [im.size[0], im.size[1]]
    bottom_left = [0,im.size[1]]

    pts_base = np.array([top_left, top_right, bottom_right, bottom_left])

    if demo:
        show.append(im)
        im.save(os.path.join(demo_dir, 'im1.jpg'))

    ##############################

    im = Image.open(base_img_path)

    # top_left = [70, 129]
    # top_right = [170, 216]
    # bottom_right= [148, 268]
    # bottom_left = [20, 200]

    top_left = [363, 151]
    top_right = [693, 75]
    bottom_right = [715, 257]
    bottom_left = [356, 289]

    pts_moded = np.array([top_left, top_right, bottom_right, bottom_left])

    if demo:
        show.append(im)
        im.save(os.path.join(demo_dir, 'im2.jpg'))

    ##############################

    h, status = cv2.findHomography(pts_base, pts_moded)

    im_out = cv2.warpPerspective(sub_img, h, (tot_img.shape[1], tot_img.shape[0]))

    cv2.imwrite(res_img_path, im_out)

    im1 = Image.open(res_img_path)

    if demo:
        show.append(im1)
        im1.save(os.path.join(demo_dir, 'im3.jpg'))

    #############################

    sub_pix = im1.load()

    im2 = Image.open(base_img_path)
    im2.convert("RGBA")
    tot_pix = im2.load()

    thresh = 25
    for i in range(im1.size[0]):
        for j in range(im1.size[1]):
            if sub_pix[i, j][0] < thresh and sub_pix[i, j][1] < thresh and sub_pix[i, j][1] < thresh:
                pass
            else:
                tot_pix[i,j] = sub_pix[i,j]

    im2.save(res_img_path)

    img_out = apply_border(im2, points=[top_left, top_right, bottom_right, bottom_left])
    if demo:
        show.append(im2)
        im2.save(os.path.join(demo_dir, 'im4.jpg'))

    if demo:
        import slideshow
        slideshow.slideshow(show)
    print "Finishing"

if __name__ == '__main__':

    main(demo=1)

    sys.exit(0)

