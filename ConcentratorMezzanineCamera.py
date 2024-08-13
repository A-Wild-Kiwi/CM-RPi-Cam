from picamera2 import Picamera2, Preview
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import itertools as it
import datetime as dt

"""
#Reference photo
with Image.open("PXL_20240723_215721945.jpg") as im:
    px = im.load()
"""


picam = Picamera2()

# width is x axis; height is y axis for the photo's dimensions
width = 3280
height = 2464

picam.configure(picam.create_preview_configuration(main={"size":(width, height)},buffer_count=4))


picam.start_preview(Preview.QTGL)

picam.start()
Query = input("Take photo (Y/N): ")

if Query == "Y" or Query == "y" or Query == "Yes" or Query == "yes" or Query == "YES":
    fileName = dt.datetime.now()
    picam.capture_file("CM_%s.jpg" % fileName)
    print("Photo taken as CM_%s.jpg" % fileName)
elif Query == "N" or Query == "n":
    quit()
else:
    print("Please use a different input and try again.")
    quit()
picam.close()


"""
#Scaled Photo for reference
with Image.open("CM_RPi_size.jpg") as im:
    px = im.load()
"""

# Actual photo from camera
with Image.open("CM_%s.jpg" % fileName) as im:
    px = im.load()


Card = np.array([0,0])
#Target Scan (Faster) - Update Numbers when stand is made for faster code
for a in it.chain(range(0,0.11*width), range(0.88*width,width)):
    for b in it.chain(range(0*height,0.3*height),range(0.7*height,height)):
        test = px[a,b]
        if 48 <= test[0] <= 122:
            if 76 <= test[1] <= 145:
                if 15<=test[2]<=58:
                    Card = np.vstack((Card, [a,b]))

#Full Scan - too slow
"""
for a in range(width):
    for b in range(height):
        test = px[a,b]
        if 48 <= test[0] <= 122:
            if 76 <= test[1] <= 145:
                if 15<=test[2]<=58:
                    Card = np.vstack((Card, [a,b]))
"""
Card = np.delete(Card, 0, 0)

#Locate 4 corners of card - Update to center of width/height values
Card_TL = [width/2,height/2]
Card_TR = [width/2,height/2]
Card_BL = [width/2,height/2]
Card_BR = [width/2,height/2]

# Change subtraction values to width/height
for a in range(len(Card)):
    if (Card_TL[0]**2 + Card_TL[1]**2)**(1/2) >= (Card[a][0]**2 + Card[a][1]**2)**(1/2):
        Card_TL = Card[a]
    if ((Card_TR[0]-width)**2 + Card_TR[1]**2)**(1/2) >= ((Card[a][0]-width)**2 + Card[a][1]**2)**(1/2):
        Card_TR = Card[a]    
    if (Card_BL[0]**2 + (Card_BL[1]-height)**2)**(1/2) >= (Card[a][0]**2 + (Card[a][1]-height)**2)**(1/2):
        Card_BL = Card[a]
    if ((Card_BR[0]-width)**2 + (Card_BR[1]-height)**2)**(1/2) >= ((Card[a][0]-width)**2 + (Card[a][1]-height)**2)**(1/2):
        Card_BR = Card[a]


print(Card_TL)
print(Card_TR)
print(Card_BL)
print(Card_BR)

Corner = np.array([0,0])
Corner = np.vstack((Corner, Card_TL))
Corner = np.vstack((Corner, Card_TR))
Corner = np.vstack((Corner, Card_BL))
Corner = np.vstack((Corner, Card_BR))
Corner = np.delete(Corner, 0, 0)

Hole = np.array([0,0])


for a in range(width):
    for b in range(height):
        test = px[a,b]
        if test[0] >= 190:
            if 148 <= test[1] <= 200:
                if test[2]<=53:
                    Hole = np.vstack((Hole, [a,b]))

Hole = np.delete(Hole, 0, 0)

Hole_Avg = np.sum(Hole, axis=0)/Hole.shape[0]



# Check orientation of card
Corner_dist = np.sum((Corner - Hole_Avg)**2, axis = 1)**(1/2)
for a in range(3):
    if Corner_dist[a] < Corner_dist[3]:
        print("Card is incorrectly orientated. Ensure yellow screw hole is near bottom right.")
        quit()
print("Card is correctly orientated")
# Define scalars (L is length(x axis); W is width(y axis))
IW = (Corner[0][1] + Corner[1][1])/2
IL = (Corner[0][0] + Corner[2][0])/2
W  = (Corner[2][1] + Corner[3][1])/2 - IW
L  = (Corner[1][0] + Corner[3][0])/2 - IL

print("IW:",IW)
print("IL:",IL)
print("W:",W)
print("L:",L)


Chip = np.array([0,0])

# These percentages may change
x1 = min(round(0.2613*L+IL),round(0.4302*L+IL))
x2 = max(round(0.2613*L+IL),round(0.4302*L+IL))
x3 = min(round(0.5928*L+IL),round(0.7747*L+IL))
x4 = max(round(0.5928*L+IL),round(0.7747*L+IL))
y1 = min(round(0.3090*W+IW),round(0.6723*W+IW))
y2 = max(round(0.3090*W+IW),round(0.6723*W+IW))

for a in it.chain(range(x1,x2), range(x3,x4)):
    for b in range(y1,y2):
        test = px[a,b]
        if 0 <= test[0] <= 45:
            if 0 <= test[1] <= 30:
                if 0<=test[2]<=18:
                    Chip = np.vstack((Chip, [a,b]))
Chip = np.delete(Chip, 0, 0)

#ECON_T & ECON_D Orientation
Sum_TX = 0
Sum_TY = 0
Count_T = 0
Sum_DX = 0
Sum_DY = 0
Count_D = 0

for a in range(len(Chip)):
    if Chip[a][0] < round(0.4938*L+IL):
        Sum_TX += Chip[a][0]
        Sum_TY += Chip[a][1]
        Count_T += 1
    else:
        Sum_DX += Chip[a][0]
        Sum_DY += Chip[a][1]
        Count_D += 1
ECON_T = np.array([Sum_TX/Count_T,Sum_TY/Count_T])
ECON_D = np.array([Sum_DX/Count_D,Sum_DY/Count_D])


if ECON_T[0] < round(0.3436*L+IL) and ECON_T[1] > round(0.4888*W+IW):
    print("ECON_T is correctly orientated")
else:
    print("ECON_T is BAD")
    
if ECON_D[0] < round(0.6823*L+IL) and ECON_D[1] > round(0.4888*W+IW):
    print("ECON_D is correctly orientated")
else:
    print("ECON_D is BAD")

# Used for debugging on plot visualization
#Chip = np.vstack((Chip, ECON_T))
#Chip = np.vstack((Chip, ECON_D))


#Capacitors (26) - To be updated when measurements are known.
#locate the center pixel of each component
#Code checks a region of 2% of L and W centered at pixel below
#Code to be implemented once new card is seen
"""
C1  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C2  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C3  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C4  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C5  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C6  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C7  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C8  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C9  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C10 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C11 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C12 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C13 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C14 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C15 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C16 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C17 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C18 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C19 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C20 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C21 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C22 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C23 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C24 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C25 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
C26 = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
"""
#Resistors (13+4)
"""
R1   = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R2   = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R3   = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R4   = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R5   = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R6   = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R7   = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R8   = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R9   = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R10  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R11  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R12  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
R13  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
#RD_SCL
R14  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
#RD_SDA
R15  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
#RT_SCL
R16  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
#RT_SDA
R17  = np.array([round(0.XXXX*L+IL), round(0.xxxx*W+IW)])
"""
#Capacitor Checker (by checking the number of empty card in the region)
#Could be changed to capacitor pixel color
# Code below requires the capacitor/resistor locations to be mapped above
# in order to run correctly 
"""
for i in range(1,27):
    misses = 0
    cap = "C"+str(i)
    L1 = ((cap[0] - IL)/L - 0.01)*L
    L2 = ((cap[0] - IL)/L + 0.01)*L
    W1 = ((cap[1] - IW)/W - 0.01)*W
    W2 = ((cap[1] - IW)/W + 0.01)*W
    for a in range(L1,L2):
        for b in range(W1,W2):
            test = px[a,b]
            if 0 <= test[0] <= 45:
                if 0 <= test[1] <= 30:
                    if 0<=test[2]<=18:
                        misses += 1
    # If >75% of the region is not capacitor, there is likely not a capacitor
    # Expectation is min ~35% of the area to be component
    # This can be improved with a dictionary denoting the orientation
    # for each component (Veritcal or horizontal) to change the percentages
    if misses >= 0.75*0.02**2*L*W:
        print ("Capacitor"+str(i) +" is missing")
    else:
        print ("Capacitor"+str(i) +" is present")

#Resistor Checker (by checking the number of empty card in the region)
#Could be changed to ressitor pixel color
for i in range(1,18):
    misses = 0
    res = "R"+str(i)
    L1 = ((res[0] - IL)/L - 0.01)*L
    L2 = ((res[0] - IL)/L + 0.01)*L
    W1 = ((res[1] - IW)/W - 0.01)*W
    W2 = ((res[1] - IW)/W + 0.01)*W
    for a in range(L1,L2):
        for b in range(W1,W2):
            test = px[a,b]
            if 0 <= test[0] <= 45:
                if 0 <= test[1] <= 30:
                    if 0<=test[2]<=18:
                        misses += 1
    # If >75% of the region is not resistor, there is likely not a resistor
    # Expectation is min ~35% of the area to be component
    # This can be improved with a dictionary denoting the orientation
    # for each component (Veritcal or horizontal) to change the percentages
    if misses >= 0.75*0.02**2*L*W:
        print ("Resistor"+str(i) +" is missing")
    else:
        print ("Resistor"+str(i) +" is present")
print("Resistors 14-17 are RD_SCL, RD_SDA, RT_SCL, and RT_SDA")
"""
# Plot visualization code - Used for Debugging test results
fig = plt.figure("Test_Plot")

ax = fig.add_subplot(111) 

ax.set_xlabel('X Axis')
ax.set_ylabel('Y Axis')
ax.set_xlim([0, width])
ax.set_ylim([-1*height, -0])

xs=Hole[:,0]
ys=-1*Hole[:,1]
t=np.ones(Hole.shape[0])

xs=np.append(xs,Corner[:,0])
ys=np.append(ys,-1*Corner[:,1])
t=np.append(t,0*np.ones(Corner.shape[0]))

xs=np.append(xs,Chip[:,0])
ys=np.append(ys,-1*Chip[:,1])
t=np.append(t,3*np.ones(Chip.shape[0]))

ax.scatter(xs,ys,c=t, cmap='rainbow')

plt.show()


"""
Future goals for additions 
- Turn code into classes/objects for better readablility
- Incorporate While with prompt of what card number is next to run 
multiple tests in one sitting
- Map out each capacitor and resistor location
- Add plotting code for capacitors and resistors based on miss vs hit
- Add code for picture of back side of card

"""