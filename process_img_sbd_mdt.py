import imutils
import numpy as np
import cv2
from math import ceil, floor

# s = [[x, y, w, h]]
def get_x(s):
    return s[0]

# IMAGE PROCESSING
def crop_img(img):
    """
        Transform the image and determine the position of the block

        Args:
            img: Image
        
        Returns:
            List of blocks
    """
    
    # Convert image BGR to GRAY to apply canny edge detection algorithm
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # remove noise by blur image
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # apply canny edge detection algorithm
    img_canny = cv2.Canny(blurred, 100, 200)

    # Find countours
    cnts = cv2.findContours(img_canny.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    ans_block = []
    # Use loop to get position and size of blocks
    for i, c in enumerate(cnts):
        x, y, w, h = cv2.boundingRect(c)
        area = w*h
        if area > 20_000: 
            ans_block.append([x, y, w, h])
    
    return sorted(ans_block, key= get_x) # sort blocks based on x coordinate


# Get the positions of answer blocks containing numeric characters
def location_box_text_sbd(ans_block):
    """
        Get the positions of answer blocks containing numeric characters

        Args: 
            ans_block: List of blocks
        
        Returns:
            List of block locations and sizes

    """

    x, y, w, h = ans_block[0]
    offset = ceil(w/6)
    location_box_sbd = []

    # Loop over each box in answer block
    for i in range(6):
        box = ( x + i*offset, y, offset, h)
        x1, y1, w1, h1 = box
        offset2 = ceil(h1/10)
        for i in range(10):
            location_box_sbd.append((x1, y1 + i*offset2, w1, offset2))

    return location_box_sbd



def location_box_text_mdt(ans_block):
    """
        Get the positions of answer blocks containing numeric characters

        Args: 
            ans_block: List of blocks
        
        Returns:
            List of block locations and sizes

    """
    x, y, w, h = ans_block[0]
    offset = ceil(w/3)
    location_box_mdt = []
    # Loop over each box in answer block
    for i in range(3):
        box = ( x + i*offset, y, offset, h)
        x1, y1, w1, h1 = box
        offset2 = ceil(h1/10)
        for i in range(10):
            location_box_mdt.append((x1, y1 + i*offset2, w1, offset2))

    return location_box_mdt


def check_and_draw_sbd_mdt(location_box, img):
    """
        Draw circles in the colored boxes

        Args:
            location_box: List of block locations and sizes
            img: Image

        Returns:
            List containing numbers

    """

    number = []
    # Use loop to iterate through each block
    for i, lct in enumerate(location_box):
        x, y, w, h = lct
        img_box =  img[ y:y+ h , x: x + w]
        gray = cv2.cvtColor(img_box, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, 
                        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        
        total = np.sum(thresh)
        # Check threshold and draw shape
        if total > 110_000:
            center = (ceil(w / 2), ceil(h / 2))
            radius = ceil((w / 2) - 1)
            color = (0, 255, 0)
            cv2.circle(img_box, center, radius, color, -1)

            # Add numbers
            number.append(i %10)

    return number















