from PIL import Image as im
from PIL import ImageDraw as draw

def blank_dom(width):
    blank = im.new(mode="RGB", size=(width, width*2), color=(0, 0, 0))
    dr = draw.Draw(blank)
    #2 middle lines
#    dr.line((0, width-1) + (width, width-1), fill=(255,255,255))
#    dr.line((0, width) + (width, width), fill=(255,255,255))
    #left line
    dr.line((0, 0) + (0, width*2-1), fill=(255,255,255))
    #top line
    dr.line((0, 0) + (width-1, 0), fill=(255,255,255))
    #right line
    dr.line((width-1, width*2-1) + (width-1, 0), fill=(255,255,255))
    #bottom line
    dr.line((0, width*2-1) + (width-1, width*2-1), fill=(255,255,255))
    return(blank)

def one_face(pic,number,space,radius):
    faces = {0: (0, 0, 0, 0, 0, 0, 0, 0, 0), 1: (0, 0, 0, 0, 1, 0, 0, 0, 0), 2: (1, 0, 0, 0, 0, 0, 0, 0, 1), 3: (1, 0, 0, 0, 1, 0, 0, 0, 1),
             4: (1, 0, 1, 0, 0, 0, 1, 0, 1), 5: (1, 0, 1, 0, 1, 0, 1, 0, 1), 6: (1, 0, 1, 1, 0, 1, 1, 0, 1),
             7: (1, 0, 1, 1, 1, 1, 1, 0, 1), 8: (1, 1, 1, 1, 0, 1, 1, 1, 1), 9: (1, 1, 1, 1, 1, 1, 1, 1, 1)}
    dr = draw.Draw(pic)
    which_dot = faces[number]
    if which_dot[0] == 1:
        dr.ellipse((space, space, space+radius, space+radius), fill=(255,255,255))
    if which_dot[1] == 1:
        dr.ellipse((space*2+radius, space, 2*space+2*radius, space+radius), fill=(255,255,255))
    if which_dot[2] == 1:
        dr.ellipse((space*3+2*radius, space, space*3+3*radius, space+radius), fill=(255,255,255))
    if which_dot[3] == 1:
        dr.ellipse((space, space*2+radius, space+radius, 2*space+2*radius), fill=(255,255,255))
    if which_dot[4] == 1:
        dr.ellipse((space*2+radius, space*2+radius, 2*space+2*radius, 2*space+2*radius), fill=(255,255,255))
    if which_dot[5] == 1:
        dr.ellipse((space*3+2*radius, space*2+radius, space*3+3*radius, 2*space+2*radius), fill=(255,255,255))
    if which_dot[6] == 1:
        dr.ellipse((space, space*3+2*radius, space+radius, space*3+3*radius), fill=(255,255,255))
    if which_dot[7] == 1:
        dr.ellipse((space*2+radius, space*3+2*radius, 2*space+2*radius, space*3+3*radius), fill=(255,255,255))
    if which_dot[8] == 1:
        dr.ellipse((space*3+2*radius, space*3+2*radius, space*3+3*radius, space*3+3*radius), fill=(255,255,255))

def complete_dom(name,number1,number2,width,space,rad):
    blank =  blank_dom(width)
    one_face(blank,number2,space,rad)
    blank = blank.rotate(180)
    one_face(blank,number1,space,rad)
    blank.save(name)

def domino_generator(w,space,rad):
    for a in range (0,10):
        for b in range (a,10):
            name = str(a) + str(b) + ".png"
            complete_dom(name,a,b,w,space,rad)

'''
the function below generates domino of size 42*84 pixel 
with radius of 10 pixels for each dot and 3 pixel spacing between them

In general: para1 = para2*4 + para3*3
'''
domino_generator(42,3,10)




