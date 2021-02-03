import requests
from bs4 import BeautifulSoup
import datetime
from PIL import Image, ImageSequence, ImageDraw, ImageFont
from easyhid import Enumeration
from time import sleep
import signal
import sys
breakCount = 17
fontPath = "cour.ttf"

#Input your schedule here!
evenSchedule = ["Algebra 2", "Chemistry", "Spanish", "Free"]
oddSchedule = ["APCSP", "English", "AP Euro", "Health"]



#check for type of day (even/odd)
def getDay():
    URL = "https://bths.edu"
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    day = soup.find(class_='event diffday first finaleventofday')
    day2 = day.find(class_='title')
    day3 = day2.find('a')
    return(day3.text.strip())




def getStatus(period):
    output = getTimeLeft(period)
    if output == "No More Classes!":
        return("")
    if (output < 0):
        output = 0 - output
        return ("Be there in " + str(output) + " minutes!")
    else:
        return (str(output) + " minutes remaining. ")

def getTimeLeft(period):
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    ts = (hour * 60) + minute
    if (period == 1 or period == 0):
        if (ts <=  512): #if before 832
            return( ts - 512) #return difference between current time and 8 32
        if (ts >= 513): #if after 832
            return(587 - ts) #return difference between current time and 9 47
    if (period == 2):
        if (ts <=  595): #if before 955
            return( ts - 595) #return difference between current time and 9 55
        if (ts >= 596):
            return(670 - ts) #return difference between current time and 11 10
    if (period == 3):
        if (ts <=  678): #if before 11 18
            return( ts - 678) #return difference between current time and 11 18
        if (ts >= 679):
            return(753 - ts) #return difference between current time and 12 33
    if (period == 4):
        if (ts <=  761): #if before 12 41
            return( ts - 761) #return difference between current time and 12 41
        if (ts >= 762):
            return(836 - ts) #return difference between current time and 12 33
    if (period == 5):
        return("No More Classes!")




#check for the curent period (1/2/3/4)
def getPeriod():
    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    if (hour >= 8 and hour <= 9):
        if (hour == 8 and minute >= 32):
            return(1)
        if (hour == 9 and minute <=47):
            return(1)

    if (hour >= 9 and hour <= 11):
        if (hour == 9 and minute >= 48):
            return(2)
        if (hour == 10):
            return(2)
        if (hour == 11 and minute <= 10):
            return(2)

    if (hour >= 11 and hour <= 12):
        if (hour == 11 and minute >= 11):
            return(3)
        if (hour == 12 and minute <=33):
            return(3)

    if (hour >= 12 and hour <= 13):
        if (hour == 12 and minute >= 34):
            return(4)
        if (hour == 13 and minute <=56):
            return(4)

    if (hour >= 13 and minute >= 57):
        return(5)

    if (hour <= 8 and minute <= 31):
        return (0)


def brk(txt, n):
    output = ""
    for i in range(0,len(txt)):
        output = output + txt[i]
        if (i % n == 0 and i >= n):
            output = output + "\n"
    return output

# call this every minute
def getClassInfo():
    day = getDay()
    if day == "EVEN Day":
        period = getPeriod()

        if (period == 0):
            return("Your first class is " + evenSchedule[0])
        if (period == 5):
            return("School is over! Your first class tomorrow is " + oddSchedule[0])
        else:
            txt = "The current class is " +  evenSchedule[period-1] +  ". " + getStatus(period)
            txt = brk(txt, breakCount)
            return(txt)

    if day == "ODD Day":

        if (period == 0):
            return("Your first class is " + oddSchedule[0])
        if (period == 5):
            return("School is over! Your first class tomorrow is " + evenSchedule[0])
        else:
            txt = "The current class is " +  oddSchedule[period-1] + ". " + getStatus(period)
            txt = brk(txt, breakCount)
            return(txt)

        #odd day things
    else:

        return("Special Day!")
        #other things

# print(update())





#im = image. Generate the image here
#OLED CODE BELOW!!



def signal_handler(sig, frame):
    try:
    	# Blank screen on shutdown
        dev.send_feature_report(bytearray([0x61] + [0x00] * 641))
        dev.close()
        print("\n")
        sys.exit(0)
    except:
        sys.exit(0)

# Set up ctrl-c handler
signal.signal(signal.SIGINT, signal_handler)

# Stores an enumeration of all the connected USB HID devices
en = Enumeration()
# Return a list of devices based on the search parameters / Hardcoded to Apex 7
devices = en.find(vid=0x1038, pid=0x1612, interface=1)
if not devices:
    devices = en.find(vid=0x1038, pid=0x1618, interface=1)
if not devices:
    print("No devices found, exiting.")
    sys.exit(0)

# Use first device found with vid/pid
dev = devices[0]

print("Press Ctrl-C to exit.\n")
dev.open()

while(1):
    img = Image.new("RGB", (128,40), color = (73, 109, 137))
    fnt = ImageFont.truetype(fontPath)
    d = ImageDraw.Draw(img)
    d.text((5,0), getClassInfo(), size = 20, fill=(255,255,0))
    img.save('frame.gif')
    im = Image.open('frame.gif')
    print(im)
    for frame in ImageSequence.Iterator(im):
        # Image size based on Apex 7
        frame = frame.resize((128, 40))
        # Convert to monochrome
        frame = frame.convert('1')
        data = frame.tobytes()
        # Set up feature report package
        data = bytearray([0x61]) + data + bytearray([0x00])
        dev.send_feature_report(data)
        sleep(30)

dev.close()
