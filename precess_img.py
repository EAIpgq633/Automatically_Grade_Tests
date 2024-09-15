import imutils
import numpy as np
import cv2
from math import floor


# s = [img, [x, y, w, h]]
def get_x(s):
    return s[1][0]

def get_y(s):
    return s[1][1]

def get_h(s):
    return s[1][3]

def get_x_ver1(s):
    s = cv2.boundingRect(s)
    return s[0] * s[1]


# IMAGE PROCESSING IN THE ANSWER SECTION
def crop_image(img):
    """
        
    """

    # Convert image BGR to GRAY to apply canny edge detection algorithm
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # remove noise by blur image
    blurred = cv2.GaussianBlur(gray_img, (5, 5), 0)

    # apply canny edge detection algorithm
    img_canny = cv2.Canny(blurred, 100, 200)

    # Find countours
    cnts = cv2.findContours(img_canny.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    ans_blocks = []
    x_old, y_old, w_old, h_old = 0, 0, 0, 0

    # ensure that at least one contour was found
    if len(cnts) >0:
        # sort the contours according to their size in descending order
        cnts = sorted(cnts, key=get_x_ver1)

        # loop over the sorted contours
        for i, c in enumerate(cnts):
            x_curr, y_curr, w_curr, h_curr = cv2.boundingRect(c)

            if w_curr * h_curr > 300_000 and w_curr * h_curr < 500_000:
                # check overlap countours
                check_xy_min = x_curr*y_curr - x_old*y_old
                check_xy_max = (x_curr + w_curr) * (y_curr + h_curr) - (x_old + w_old) * (y_old + h_old)

                # if list answer box is empty
                if len(ans_blocks) == 0:
                    ans_blocks.append(
                        (gray_img[y_curr: y_curr + h_curr, x_curr:x_curr + w_curr],
                        [x_curr, y_curr, w_curr, h_curr]))
                    
                    # update coordinates (x, y) and (height, width) of added contours
                    x_old = x_curr
                    y_old = y_curr
                    w_old = w_curr
                    h_old = h_curr
                
                elif check_xy_min > 2000 and check_xy_max > 2000:
                    ans_blocks.append(
                        (gray_img[y_curr:y_curr + h_curr, x_curr:x_curr + w_curr], [x_curr, y_curr, w_curr, h_curr]))
                    # update coordinates (x, y) and (height, width) of added contours
                    x_old = x_curr
                    y_old = y_curr
                    w_old = w_curr
                    h_old = h_curr
    
        # sort ans_block arrcording to x coodinate
        sorted_ans_block = sorted(ans_blocks, key=get_x)

        return sorted_ans_block


# Get the positions of answer blocks containing alphabetic characters
def location_answer(sorted_ans_block):
    """
        Get the positions of the blocks containing the characters A, B, C, D
        
        Args:
            sorterd_ans_block: List the locations and sizes of the 4 column blocks in the answer section
            sorted_ans_block[i] = (img, [x, y, w, h])

        Returns:
            List of positions and sizes of the blocks containing the characters A, B, C, D
    """

    # Initialize a list to store the box positions that is 1/6 the size of the original box position.
    location_in_img_origal = []

    for ans_block in sorted_ans_block:
        # position of each block in 4 blocks
        x , y, w, h = ans_block[1]

        # length of sub block
        offset1 = floor((h) / 6)
        
        # Use loop to get the position of 6 sub blocks
        for i in range(6):
            # location of each sub-block
            location_box = ( x, y + i*offset1 + 14 , w, offset1 - 14 )
            x1, y1, w1, h1 = location_box

            # length of sub loaction_box
            offset2 = floor((h1) / 5)

            add = 0
            # Use loop to get the position of 5 sub location_box
            for j in range(5):
                if j>=3:
                    add = 10
                location_in_img_origal.append((x1, y1 + j*offset2 - add, w1, offset2))

    # Initialize a list that receives the positions of the blocks containing the characters
    list_location_one_text = []
    offset = 60
    start = 60

    # Use a loop to get the positions of the blocks containing the questions
    for ans_location in location_in_img_origal:
        x, y, w, h = ans_location
        r = 0
        # Use a loop to get the positions of blocks containing characters
        for i in range(4):
            if i == 3:
                r = 6
            bubble_choice = (x + start + i*offset, y, offset - r, h )
            list_location_one_text.append(bubble_choice)

    return list_location_one_text 


def get_answer_candidate(list_location_one_text,img_answer):
    """
        Get test answers from candidates

        Args:
            list_location_one_text: List of positions and sizes of the blocks containing the characters A, B, C, D
            img_answer: Photo of answer sheet

        Returns:
            List of candidates' answers
    """
    
    # change data
    translation = {'A' : 0, 'B': 1, 'C': 2, 'D': 3}
    reversed_translation = {0: 'A', 1: 'B', 2: 'C', 3: 'D' }

    # Create a list to get answers from candidates
    list_choice_candidate = []

    # Check if the candidate has taken the test
    flag = True
    # 
    for i, lct in enumerate(list_location_one_text):
        # 
        x, y, w, h = lct
        img_box =  img_answer[ y:y+ h , x: x + w]
        gray = cv2.cvtColor(img_box, cv2.COLOR_BGR2GRAY)
        # Image thresholding
        thresh = cv2.threshold(gray, 0, 255, 
                        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        
        # Calculate total pixels
        total = np.sum(thresh)

        # Check to see if it has been painted.
        if total > 80_000:
            list_choice_candidate.append(reversed_translation[i%4])
            flag = False
        if ((i+1)%4 == 0) and flag:
            list_choice_candidate.append(None)
        if (i+1)% 4 == 0:
            flag = True

    return list_choice_candidate

def draw_cricle(location, color, img_answer):
    """
        Circle the characters

        Args:
            location: Location and size
            color: Color
            img_answer: Image

    """

    s = location
    img = img_answer[ s[1]:s[1]+ s[3] , s[0]: s[0] + s[2]]

    # Convert image BGR to GRAY
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY )

    # Image thresholding
    thresh = cv2.threshold(img_gray, 0, 255, 
                               cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # Draw
    cv2.drawContours(img, cnts, -1, color, 3)


def check_and_draw(list_choice_candidate,list_location_one_text, ANSWER_KEY, img_answer):
    """
        Check the results and draw in the selected boxes, the correct answer boxes

        Args:
            list_choice_candidate: List of candidates' answers
            list_location_one_text: List of positions and sizes of the blocks containing the characters A, B, C, D
            ANSWER_KEY: List of answers
            img_answer: Image

        Returns:
            Number of correct answers of candidates
    """

    translation = {'A' : 0, 'B': 1, 'C': 2, 'D': 3}
    reversed_translation = {0: 'A', 1: 'B', 2: 'C', 3: 'D' }
    count_question = len(list_choice_candidate)

    # initialize variable to count correct answers
    count_true = 0

    # Use loop to check candidate's answers with answer key
    for i in range(count_question):
            # Get key
            student = list_choice_candidate[i] 
            actual = ANSWER_KEY[i] 

            # Check and color the correct sentences in green and the incorrect sentences in red.
            if student == actual:
                location = list_location_one_text[i*4 + translation[actual]]
                draw_cricle(location, (0, 255, 0), img_answer)
                # Plus one
                count_true += 1

            
            elif student is not None:
                location_actual = list_location_one_text[i*4 + translation[actual]]
                draw_cricle(location_actual, (0, 255, 0), img_answer)
                  
                location_student = list_location_one_text[i*4 + translation[student]]
                draw_cricle(location_student, (0, 0, 255), img_answer)

            # Candidates did not do this question, draw blue color
            else: 
                location_actual = list_location_one_text[i*4 + translation[actual]]
                draw_cricle(location_actual, (255, 0, 0), img_answer)

    return count_true

