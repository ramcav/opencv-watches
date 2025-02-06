import numpy as np
import cv2 as cv
from datetime import datetime
 
# COLORS

# SILVER
SILVER = (192, 192, 192)

# DARK SILVER
DARK_SILVER = (128, 128, 128)

# METALLIC BLUE
METALLIC_BLUE = (206, 157, 151)  # BGR format

# DARK GRAY
DARK_GRAY = (64, 64, 64)

def main():

    # Set the width and height of the screen
    width = 512
    height = 512
    
    # Using a loop to constantly re-draw the clock and get a new time every 1 ms
    while True:
        img = np.zeros((width, height, 3), np.uint8)
        draw_clock(img, width, height)
        
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv.destroyAllWindows()

def draw_clock(img, width, height):
    """
    Function that draws a clock by using all of the methods defined within the file
    """

    radius = width * 0.3
    center = (width//2,height//2)

    # Outer polygon
    draw_polygon(img, center, radius)

    # Inner polygon
    draw_polygon(img, center, radius-30)

    # Draw hour markers
    draw_hour_markers(img, center, radius-15)

    # Draw bolts
    draw_bolts(img, center, radius - 15)

    # Draw hands
    draw_clock_hands(img, center, radius-30)

    # Draw logo
    draw_logo(img, center)

    # Draw belt
    draw_bottom_links(img, center, radius)

    draw_top_links(img, center, radius)

    # Draw the image
    cv.imshow('Image', img)

def draw_polygon(img, center, radius):
    """
    Function that draws a polygon (octagon) by taking a center and a radius
    and going around a circle plotting points and then using cv.polylines
    to join them.

    This function uses trigonometry to calculate x and y by using the radius,
    sin, cos and center of the circle.
    """
    points = []

    for i in range(8):

        # This functionality basically uses the formula for a circle to generate points for an octagon
        # so all the points are equidistant from the center and are placed in 
        # the correct angle from the center as I divided the circle into 8 equal parts

        angle = (i * (2 * np.pi / 8)) + (np.pi / 8) # adding pi/8 to the angle to start from the top of the circle

        x = int(center[0] + radius * np.cos(angle))
        y = int(center[1] + radius * np.sin(angle))

        points.append([x, y])

    # This is necessary to pass the points in the proper formatting OpenCV expects.
    # https://docs.opencv.org/4.x/dc/da5/tutorial_py_drawing_functions.html
    pts = np.array(points, np.int32)
    pts = pts.reshape((-1, 1, 2))


    cv.polylines(img, [pts], True, SILVER, 2)

def draw_bolts(img, center, radius):
    """
    Function that draws the bolts of the AP watch.
    It uses a similar logic to the `draw_polygon`implementation.
    """

    for i in range(8):

        angle = (i * (2 * np.pi / 8)) + (np.pi / 8)

        x = int(center[0] + radius * np.cos(angle))
        y = int(center[1] + radius * np.sin(angle))

        cv.circle(img,(x,y), 7, SILVER, -1)

        cv.line(img,(x-3,y-3),(x+3,y+3),DARK_GRAY,5)

def draw_logo(img, center):
    """
    Function that draws a logo/text on the screen,
    adapted to properly display the AUDEMARS PIGUET logo.
    """


    text = 'AUDEMARS PIGUET'
    font = cv.FONT_HERSHEY_DUPLEX
    font_scale = 0.35
    thickness = 1
    color = SILVER

    (text_width, text_height), baseline = cv.getTextSize(text, font, font_scale, thickness)
    

    x = center[0] - (text_width // 2)
    y = center[1] - 60
    
    cv.putText(img, text, (x, y), font, font_scale, color, thickness, cv.LINE_AA)

def draw_hour_markers(img, center, radius):
    """
    Function to draw the hour markers.

    In particular, this function does something different for the first iteration
    as the example watch has two parallel lines on hour 12.

    The rest are drawn using the angle of the circle, just as the two methods above,
    with some added functionality to start at hour 12 (the middle top of a 360 circle divided in 12)
    """
    for i in range(12):
        angle = (i * (2 * np.pi / 12)) - (np.pi / 2)  # Subtract π/2 to start at 12 o'clock

        # Point closest to the rim
        inner_x = int(center[0] + (radius - 44) * np.cos(angle))
        inner_y = int(center[1] + (radius - 44) * np.sin(angle))
        
        # Point closest to the center
        outer_x = int(center[0] + (radius-23.5) * np.cos(angle))
        outer_y = int(center[1] + (radius-23.5) * np.sin(angle))
        
        if i == 0:  # At 12 o'clock

            # Draw two parallel lines

            offset = 4  # Distance between the lines
            
            # Left line
            left_inner_x = int(inner_x - offset * np.sin(angle))
            left_inner_y = int(inner_y + offset * np.cos(angle))
            left_outer_x = int(outer_x - offset * np.sin(angle))
            left_outer_y = int(outer_y + offset * np.cos(angle))
            
            # Right line
            right_inner_x = int(inner_x + offset * np.sin(angle))
            right_inner_y = int(inner_y - offset * np.cos(angle))
            right_outer_x = int(outer_x + offset * np.sin(angle))
            right_outer_y = int(outer_y - offset * np.cos(angle))
            
            cv.line(img, (left_inner_x, left_inner_y), (left_outer_x, left_outer_y), SILVER, 3)
            cv.line(img, (right_inner_x, right_inner_y), (right_outer_x, right_outer_y), SILVER, 3)

        else:

            cv.line(img, (inner_x, inner_y), (outer_x, outer_y), SILVER, 3)

def draw_clock_hands(img, center, radius):

    """
    Function that draws the clock hands for the current time of the computer.

    It uses the datetime library to do so, and employs similar trigonometric methods
    to draw the hands.

    For the hour hand, the circle is divided in 12 and depending on the hour and minutes,
    the hand is drawn. This simulates the real behaviour of a clock, as when minutes go by, the hour
    hand also goes slowly forward.

    For the minute hand, the circle is divided in 60, and the minute and seconds are used to calculate
    the position of the hand.

    For the second hand, the circle is divided by 50 as well and only the seconds are taken into consideration.
    """
    
    # Get current time
    now = datetime.now()
    hour = now.hour % 12
    minute = now.minute
    second = now.second

    # Hour hand
    hour_angle = ((hour + minute/60) * (2 * np.pi / 12)) - (np.pi / 2)
    hour_length = radius * 0.5
    hour_x = int(center[0] + hour_length * np.cos(hour_angle))
    hour_y = int(center[1] + hour_length * np.sin(hour_angle))

    cv.line(img, center, (hour_x, hour_y), SILVER, 4)

    # Minute hand
    minute_angle = ((minute + second/60) * (2 * np.pi / 60)) - (np.pi / 2)
    minute_length = radius * 0.7
    minute_x = int(center[0] + minute_length * np.cos(minute_angle))
    minute_y = int(center[1] + minute_length * np.sin(minute_angle))
    cv.line(img, center, (minute_x, minute_y), SILVER, 3)

    # Second hand
    second_angle = (second * (2 * np.pi / 60)) - (np.pi / 2)
    second_length = radius * 0.8
    second_x = int(center[0] + second_length * np.cos(second_angle))
    second_y = int(center[1] + second_length * np.sin(second_angle))
    cv.line(img, center, (second_x, second_y), METALLIC_BLUE, 2)

    # Draw center circle
    cv.circle(img, center, 8, SILVER, -1)
    cv.circle(img, center, 3, DARK_GRAY, -1)

def draw_bottom_links(img, center, radius):
    """
    Function to draw the bottom links of the watch.

    It first takes into consideration position 3 and 8 of the corners
    of the polygon drawn before to begin drawing the links as per the
    sample image.

    Then, the first link is diagonal, which means that two diagonal
    lines are drawn to an arbitrary distance below and an intersection
    line closes it.

    A second link which is the first before the verticals is added by adding 
    an arbitrary number to the y coordinates, and a small icnrease to x to
    show a small inclination.

    The remaining links are drawn using a while loop.
    """
    # Position 3 and 8 which represent the bolts I want to plot
    angle_1 = (3 * (2 * np.pi / 8)) + (np.pi / 8)  # Position 4
    angle_2 = (8 * (2 * np.pi / 8)) + (np.pi / 8)  # Position 7

    # Calculate start points at the octagon
    x1 = int(center[0] + radius * np.cos(angle_1))
    y1 = int(center[1] + radius * np.sin(angle_1))
    
    x2 = int(center[0] + radius * np.cos(angle_2))
    y2 = int(center[1] + radius * np.sin(angle_2))

    end_y = int(center[1] + radius)

    # First link  - with angle
    cv.line(img, (x1, y1), (x1+60, end_y), SILVER, 2)
    cv.line(img, (x2, y2), (x2-60, end_y), SILVER, 2)
    cv.line(img, (x1+60, end_y), (x2-60, end_y), SILVER, 2)

    # Second link - first vertical

    second_y = end_y + 30
    cv.line(img, (x1+60, end_y), (x1+65, second_y), SILVER, 2)
    cv.line(img, (x2-60, end_y), (x2-65, second_y), SILVER, 2)
    cv.line(img, (x1+65, second_y), (x2-65, second_y), SILVER, 2)

    # Variables for subsequent links
    left_x = x1 + 65
    right_x = x2 - 65
    current_y = second_y
    link_height = 30
    
    # While there is space draw the links (leave a 10px margin tho)
    while current_y + link_height < img.shape[0] - 10:

        # Draw vertical lines
        cv.line(img, (left_x, current_y), (left_x, current_y + link_height), SILVER, 2)
        cv.line(img, (right_x, current_y), (right_x, current_y + link_height), SILVER, 2)
        
        # Draw horizontal line
        cv.line(img, (left_x, current_y + link_height), (right_x, current_y + link_height), SILVER, 2)
        
        current_y += link_height

def draw_top_links(img, center, radius):
    """
    Same exacrt functionality as `draw_bottom_link` but with different starting points
    and subtracting instead of adding.
    """

    angle_1 = (4 * (2 * np.pi / 8)) + (np.pi / 8)
    angle_2 = (3 * (2 * np.pi / 8)) + (np.pi / 8) 

    x1 = int(center[0] + radius * np.cos(angle_1))
    y1 = int(center[1] + radius * np.sin(angle_1))
    
    x2 = int(center[0] - radius * np.cos(angle_2))
    y2 = int(center[1] - radius * np.sin(angle_2))

    end_y = int(center[1] - radius)

    cv.line(img, (x1, y1), (x1+60, end_y), SILVER, 2)
    cv.line(img, (x2, y2), (x2-60, end_y), SILVER, 2)
    cv.line(img, (x1+60, end_y), (x2-60, end_y), SILVER, 2)

    second_y = end_y - 30
    cv.line(img, (x1+60, end_y), (x1+65, second_y), SILVER, 2)
    cv.line(img, (x2-60, end_y), (x2-65, second_y), SILVER, 2)
    cv.line(img, (x1+65, second_y), (x2-65, second_y), SILVER, 2)

    left_x = x1 + 65
    right_x = x2 - 65
    current_y = second_y
    link_height = 30
    
    while current_y - link_height > 10:
        cv.line(img, (left_x, current_y), (left_x, current_y - link_height), SILVER, 2)
        cv.line(img, (right_x, current_y), (right_x, current_y - link_height), SILVER, 2)
        
        cv.line(img, (left_x, current_y - link_height), (right_x, current_y - link_height), SILVER, 2)
        
        current_y -= link_height


if __name__ == "__main__":
    main()

