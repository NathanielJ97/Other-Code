# -*- coding: utf-8 -*-
"""
Created on Sat Mar  2 11:26:48 2019

@author: JOS13502565 - Nathaniel Josephs
"""

# JOS13502565_Assignment_Item_1.py
# CMP3103M - Autonomous Mobile Robotics
# Assignment 1 - Visual Object Search
# JOS13502565 - Nathaniel Josephs
#
#For Ease of Access <REMOVE BEFORE HAND-IN!!!>
#Empty Simulation: roslaunch turtlebot_gazebo turtlebot_world.launch world_file:=$(rospack find turtlebot_gazebo)/worlds/empty.world
#Training Simulation Open: roslaunch uol_turtlebot_simulator object-search-training.launch
#Rviz open (use the attached config file): roslaunch turtlebot_rviz_launchers view_robot.launch
#

import numpy, math, time

import cv2
import cv_bridge
import rospy
import actionlib

from sensor_msgs.msg import Image
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from geometry_msgs.msg import PoseStamped

from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from nav_msgs.msg import OccupancyGrid

from numpy import nanmean, nanmin, nansum
from math import radians

class Follow:
    # Initialization method of the Node
    def __init__(self):
        self.bridge = cv_bridge.CvBridge()
        # Defining the image subscriber - Subscribe to the image of the robot (getting the rgb image, rather than the depth)
        self.image_sub = rospy.Subscriber('/camera/rgb/image_raw', Image,
                                          self.image_callback)
        # Defining the laser subscriber - Subscribe to laserscan (used for the collision avoidance)
        self.laser_sub = rospy.Subscriber('/scan', LaserScan, self.laser_callback)
        # Defining the map subscriber - Subscribe to the move-base costmap
        self.map_sub = rospy.Subscriber("/move_base/global_costmap/costmap", OccupancyGrid, self.map_callback)
        # Defining the velocity publisher - Allows to publish velocity commands (which are now located in mobile_base, different in older code)
        self.cmd_vel_pub = rospy.Publisher('/mobile_base/commands/velocity', Twist,
                                           queue_size=1)
        # Defining the move_base goal publisher - Allows to publish next point of interest for the robot to navigate to
        self.goal_pub = rospy.Publisher('/move_base_simple/goal', PoseStamped, queue_size=10)
                                           
        # Twist        
        self.twist = Twist()           
        
        # Current Laserscan distance
        self.currentForwardScanDistance = 100
        self.laserDistances = [0]
        # EXPLAIN THIS ALL MUCH BETTER IN COMMENTS
        self.leftSide = len(self.laserDistances) / 4; #Get the distance for the left side of the robot by getting the index (1/4 index, such as was explained for getting the forward distance) 
        self.rightSide = (len(self.laserDistances) / 4) * 3; #Get the distance for the right side of the robot by getting the 3/4 index
        
        # Colour Finding
        self.redFound = False
        self.blueFound = False
        self.greenFound = False
        self.yellowFound = False
        self.currentColourTarget = 0 # Current colour target for the robot (e.g. 0 = red, 1 = blue)
        
        self.counterPOI = 0 # Set Point of Interest Counter to 0
        # Tell the action client that we want to spin a thread by default
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        self.move_base.wait_for_server()

        
    #Need a method for moving the robot, making it easier than having to write it out in full every time
    def moveRobot(self, linear, angular):
        self.twist.linear.x = linear
        self.twist.angular.z = angular
        self.cmd_vel_pub.publish(self.twist)        
        
    #def goForwardAndScan (self, ?, ?):
        
    # Method that instructs the robot to roam should it not be able to find a colour in its current view
    def roamRobot(self):
        # Roam by spinning the robot around in a circle?
        self.moveRobot(0, 2)
        
    # Method that instructs the robot to move to the next Point of Interest
    def moveToGoal(self):
        print ('Moving to next point of interest (' + str(self.counterPOI) + ')')
        move_to = MoveBaseGoal()
        move_to.target_pose.header.frame_id = "map"
        move_to.target_pose.header.stamp = rospy.Time.now()
        move_to.target_pose.pose.position.x = self.areaCentres[self.counterPOI][0]
        move_to.target_pose.pose.position.y = self.areaCentres[self.counterPOI][1]
        move_to.target_pose.pose.orientation.w = 1.0
        # Set position of goal, then set the 'goalReached' callback when it has reached this point 
        self.move_base.send_goal(move_to, done_cb=self.goalReached)
        
    # Method for Avoiding collision with the poles and other obstacles, this utilises LaserScan  
    def avoidCollision(self):
        #Laserscanner has a 270 degree detection angle. The ranges array returned contains distances for angles within that range (Dependent on the scan frequency etc.).
        #e.g. Straight ahead would be the in the middle of the ranges array (msg.ranges[length / 2] = ~135 degrees). 
        
        #First check if the front is blocked        
        #Check that the distances array is not empty
        if (math.isnan(nanmean(self.laserDistances)) == False):
            #Calculate the arithmetic mean (ignoring nan values)
            if (nanmean(self.laserDistances < 2) or nanmin (self.laserDistances) < 0.75):
                #Move the robot back (maybe add a method for moving the robot to save time from entering the full modification)
                self.moveRobot(0, -1)
                print("Collision detected in front - Robot turning right")
                
                #Then check if the left side is blocked                
                #Calculate the sum of the left and right side values (treating nan values as zero)
            elif nansum(self.laserDistances[:self.leftSide]) > nansum(self.laserDistances[self.rightSide:]):
                #If closer to the left side than the right, move the robot to the right
                self.moveRobot(0.2, -1)
                print("Collision detected to the left - Moving to the right")                
                #Then check if the right side is blocked
                #Calculate the sum of the left and right side values (treating nan values as zero)
            elif nansum(self.laserDistances[:self.leftSide]) < nansum(self.laserDistances[self.rightSide:]):
                #If closer to the right side than the left, move the robot to the left
                self.moveRobot(0.2, 1)
                print("Collision detected to the right - Moving to the left")                
        #Otherwise move the robot backwards
        else:
            self.moveRobot(-1, 0)
            print("Otherwise, move backwards")      
            
    # callback method to peform an action once the goal has been reached
    def goalReached(self, state, res):
        print("Goal Reached!")    
        #Look for the Colour, if it is found... move on to the next goal
        self.findingColour()
        #Increment point counter as the last point completed succesfully
        if self.counterPOI + 1 <= len(self.areaCentres):
            self.counterPOI += 1
    
    # Method for finding the colour (What was previously in image callback)
    def findingColour(self):
        print("Looking For Colour...")
                 
        #cv2.namedWindow("window", 1) # Named window to display the robot camera image
        #cv2.namedWindow("mask", 1) # Named window to display the mask   

        # Stop any goals currently in progress so that the robot can correctly search for the colour pole
        self.move_base.cancel_goals_at_and_before_time(rospy.Time.now())
        #print("Current Goals Cancelled!")
                       
        if (self.redFound == True and self.blueFound == True and self.greenFound == True and self.yellowFound == True):
            # Check if all colours have been found, if so call the searchComplete Method
            self.searchComplete()
        else:
            # Loop through finding each colour for 5 seconds
            for self.currentColourTarget in range(0, 4):             
                # Upper and lower bounds for the colour range, also check the current colour target
                # 0 RED        
                if (self.redFound == False and self.currentColourTarget == 0):
                    lower_bound = numpy.array([0, 200, 100])
                    upper_bound = numpy.array([0, 255, 150])          
                    print ('Looking for the Colour Red!')
                # 1 BLUE
                elif (self.blueFound == False  and self.currentColourTarget == 1):
                    lower_bound = numpy.array([90, 200, 100])
                    upper_bound = numpy.array([140, 255, 230])
                    print ('Looking for the Colour Blue!')
                # 2 GREEN
                elif (self.greenFound == False and self.currentColourTarget == 2):
                    lower_bound = numpy.array([55, 200, 70])
                    upper_bound = numpy.array([90, 255, 225])
                    print ('Looking for the Colour Green!')
                # 3 YELLOW
                elif (self.yellowFound == False and self.currentColourTarget == 3):
                    lower_bound = numpy.array([30, 200, 50])
                    upper_bound = numpy.array([50, 255, 200])
                    print ('Looking for the Colour Yellow!')
                # If not, just set it to a (BLACK OR WHITE??????) mask
                else:
                    lower_bound = numpy.array([255, 255, 255])
                    upper_bound = numpy.array([255, 255, 255]) 
                    print ('Colour already found (' + str(self.currentColourTarget) + '), passing this loop')
                    continue #Skip this loop and go to the next one
                    
                # These bounds are used, and then checked if something is found    
                print("Set Bounds!")            
                
                # Give the robot 2.5 seconds to find the colour pole
                t_end = time.time() + 2.5
                while time.time() < t_end:
                    #print ("time:" + str(time.time())) Printing time for testing purposes
                    mask = cv2.inRange(self.global_hsv, lower_bound, upper_bound) # Thesholding operation, defining the mask as being within the defined range
                    h, w, d = self.global_image.shape # Access image properties getting number of rows, columns and channels (If grayscale would only return the first two) + defining mask size
                    
                    M = cv2.moments(mask) # Calculates all the moments of a shape (the Mask in this case)
                    # If the robot is grater than 0.75 to the target (Done using the minimum value of the laser distances, ignoring NaNs), proceed as normal
                    if nanmin(self.laserDistanceArray,axis = 0) >= 0.75: 
                        if M['m00'] > 0:
                            cx = int(M['m10']/M['m00']) # Center point x
                            cy = int(M['m01']/M['m00']) # Center point y
                            cv2.circle(self.global_image, (cx, cy), 20, (0, 0, 255), -1) # Draws a circle
                            
                            # Move towards colour, allow 10 seconds to identify the colour
                            t_end = time.time() + 10
                            err = cx - w/2 # Calculating the 'error'
                            self.moveRobot(1, -float(err) / 100) # Call moveRobot method to modify the linear and angular (based on calucated error) velocity components
                            #print self.twist.angular.z # Print the angular correction                            
                            
                            # Checking if the colour has been found
                            if (self.currentForwardScanDistance < 1.25) and (self.currentForwardScanDistance >= 0.75): 
                                self.foundColour() # Call the 'foundColour' method
                                break # If the colour is found exit this loop using break
                        else:
                            # Cannot find colour --- ROAM AROUND THIS GOAL
                            self.roamRobot()                
                    else:
                        self.avoidCollision() # If too close, then avoid collison (by calling method), THIS MAY NEED FURTHER MODIFCATION BASED ON WHAT COLOUR IS BEING SEARCHED FOR ETC.
                        print('The Robot is too close to the object')
                        print('CurrentLaserDistance: ' + str(self.currentForwardScanDistance))
        
                    self.cmd_vel_pub.publish(self.twist) # publish the new calculated twist to the velocity publisher
                    #cv2.imshow("window", self.global_image) # Window showing the 'robot camera image'
                    #cv2.imshow("mask", mask) # Window showing the mask
                    #cv2.waitKey(20) # Waits indefinetly for a pressed key   
            
            # If it escapes the loop and cannot find whilst roaming, then move to the next goal
            # Cannot find colour --- MOVING TO THE NEXT GOAL
            self.moveToGoal()
    
    # Method for checking whether the colour found is one currently being targetted
    def foundColour(self):
        # Check the 'found' colour against whatever the current colour target is
        if (self.currentColourTarget == 0):
            self.redFound = True
            self.currentColourTarget = self.currentColourTarget + 1 # Increment the currentColourTarget
            print ('Found the Colour Red!')
            self.moveToGoal()
        elif (self.currentColourTarget == 1):
            self.blueFound = True
            self.currentColourTarget = self.currentColourTarget + 1 # Increment the currentColourTarget
            print ('Found the Colour Blue!')
            self.moveToGoal()
        elif (self.currentColourTarget == 2):
            self.greenFound = True
            self.currentColourTarget = self.currentColourTarget + 1 # Increment the currentColourTarget
            print ('Found the Colour Green!')
            self.moveToGoal()
        elif (self.currentColourTarget == 3):
            self.yellowFound = True
            self.currentColourTarget = self.currentColourTarget + 1 # Increment the currentColourTarget
            print ('Found the Colour Yellow!')
            self.moveToGoal()
            
    # Method to call once all colours have been found
    def searchComplete(self):
        print ('All Colours have been Found')
        # Spin Robot or do something
        
    # Method to get the map POI's (Different map regions centre points)
    def getMapCentres(self, mapArray):
        # Copy the mapArray for later use
        mapArrayO = mapArray    
        height, width = mapArray.shape # Get Height and Width from mapArray
        
        # Map Image Processing (Making it easier to identify the points of interest)
        dilateSE = numpy.ones((8,8), numpy.uint8) # Dilate map to get rid of any rough edges and enlarge map points (Structuring Element)
        mapArrayD = cv2.dilate(mapArray, dilateSE, iterations=1) # Dilate the map array once using the defined structuring element
        mapCanny = cv2.Canny(mapArrayD,100,200) # Canny Edge Detector
                
        mapArrayColour = cv2.cvtColor(mapArray, cv2.COLOR_GRAY2BGR) # Convert to colour map array
        
        #Get map lines
        mapLines = cv2.HoughLinesP(mapCanny, rho=1,theta=numpy.pi/180, threshold=50,lines=numpy.array([]), minLineLength=1,maxLineGap=150) #minLineLength = 1

        # Clearer separate each section in the map by extending and thickening lines
        for line in mapLines[0]:
            x1 = line[0]
            y1 = line[1]
            x2 = line[2]
            y2 = line[3] 
            # Define the two points of the line
            point1 = (x1, y1)
            point2 = (x2, y2)
 
            if((x1 >= x2 - 10) and (x1 <= x2 + 10) and (y1 > y2)):
                point1 = (x1, 0)
                point2 = (x2, height)
            if((y1 >= y2 - 10) and (y1 <= y2 + 10) and (x1 > x2)):
                point1 = (0, y1)
                point2 = (width, y2)
            cv2.line(mapArrayColour, point1, point2, (0,0,0), thickness=5, lineType=8, shift=0)

        # Get greycsale of map
        mapArrayGrey = cv2.cvtColor(mapArrayColour, cv2.COLOR_BGR2GRAY)
        # Convert to Binary Map by thresholding with Otsu
        ret, mapArrayBinary = cv2.threshold(mapArrayGrey,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

        # Perform Opening Operation on the Binary Map
        openingSE = numpy.ones((3,3), numpy.uint8) # (Structuring Element)
        mapArrayOpen = cv2.morphologyEx(mapArrayBinary, cv2.MORPH_OPEN, openingSE, iterations = 2) # How many iterations??
        
        # FG, BG Split and then perform image subtraction
        mapArrayBG = cv2.dilate(mapArrayOpen, openingSE, iterations = 3) # Use the previously defined Opening Structuring Element #How many iterations??
        ret, mapArrayFG = cv2.threshold(mapArrayOpen, 0.2*mapArrayOpen.max(), 255, 0)
        mapArrayFG = numpy.uint8(mapArrayFG) # Conversion        
        mapArraySubtraction = cv2.subtract(mapArrayBG, mapArrayFG) # Perform the image subtraction

        # Segment to obtain contours, and centres for these contoured areas
        i, contours, h = cv2.findContours(mapArraySubtraction.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        centres = []
        points = []       
        for contour in contours:
            # If the amount of points found is at least 4 then an area has been found
            if len(contour) >= 4:
                cMoment = cv2.moments(contour)
                #Get the x and y center of the area
                centrePoint = (int(cMoment["m10"]/cMoment["m00"]), int(cMoment["m01"]/cMoment["m00"]))
                centres.append(centrePoint)

        for centre in centres:
            x = int(centre[0])
            y = int(centre[1])
            points.append(centre) #add each centre point found
            # Check that the point isn't underneath and object
            if(x < 12 or y < 22 or x > 200 or y > 240 or mapArrayO[y][x] == 0 or mapArrayO[x-10][y] == 0 or mapArrayO[x+10][y] == 0 or mapArray[x][y-10] == 10 or mapArray[x][y+10] == 0):
                pass
            else:
                points.append(centre)

            
        print "Found " + str(len(points)) + " POI's"  # Return the number of points found, should be =      
        
        return points

    # Converting Map points to World points
    def getWorldPoint(self, point, offset, resolution):
        # Set the x and y variables to the input points
        mapX = point[1]
        mapY = point[0]

        # Convert the x and y points into 'real world' points, set points as the return variable
        worldX = (mapX * resolution) + offset[0]
        worldY = (mapY * resolution) + offset[1]
        worldPoint = (worldX, worldY)

        return worldPoint

    # callback method to get image properties, now the image callback is literally just responsible for obtaining the image (The 'findingColour' method is now responsible for the identifying bounds and finding colours)
    def image_callback(self, msg):     
        image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV) # Converts the colour space from BGR to HSV
                
        # Global property for keeping track of image information and hsv information
        self.global_image = image
        self.global_hsv = hsv  
        
        # To stop hang up if there is an issue with navigating to one of the goals or it gets stuck
        #if self.move_base.get_state() == actionlib.CommState.LOST or self.move_base.get_state() == actionlib.TerminalState.ABORTED:
        #    print("Error navigating to point: ", self.counterPOI)
            # Reset by cancelling goals and then moving to the next goal
        #    self.move_base.cancel_all_goals()
        #    self.moveToGoal()

        
    # callback method to get laser properties
    def laser_callback(self, msg):
        # Range data is in metres, range data is returned as an array (Discard values outside the boundary of the range_min and range_max messages)
        self.currentForwardScanDistance = msg.ranges[len(msg.ranges) / 2] # Taking the current forward laserscan distance from the subscribed to ranges message
        self.laserDistanceArray = msg.ranges # Put all laser scan ranges into an array
        
    # callback method to get the map properties and data
    def map_callback(self, data):
        cv2.namedWindow("Map", 1)
        # Get the origin X and Y pos of the map
        xOrigin = data.info.origin.position.x
        yOrigin = data.info.origin.position.y

        # Get map width, height and resolution
        mapWidth = data.info.width
        mapHeight = data.info.height
        mapResolution = data.info.resolution
        
        mapArray = numpy.array(data.data).reshape(mapHeight, mapWidth) # Load the data into a map matrix        
        offset = (int(xOrigin), int(yOrigin)) # Apply any offset needed based on the origin position for the map

        # Reinitialise map matrix with 0s
        mapArray = numpy.zeros((mapHeight, mapWidth), dtype = "uint8")        
        # Fill Map Arrays data
        for r in range(1, mapHeight):
            for c in range(1, mapWidth):
                mapArray[r-1, c-1] = 255-int(float(data.data[(r-1)*mapWidth+c])/100*255)
        mapArray = cv2.flip(mapArray, 0)
        
        # Threshold mapArray to mapArrayBinary
        ret, mapArrayBinary = cv2.threshold(mapArray,127,255,cv2.THRESH_BINARY)
        mapCentres = self.getMapCentres(mapArrayBinary) # Find the centres of the new mapArrayBinary
        self.areaCentres = []
        
        mapArrayColour = cv2.cvtColor(mapArray, cv2.COLOR_GRAY2BGR) # Convert the normal map array to a colour one

        # Get world points
        for centre in mapCentres:
            cv2.line(mapArrayColour, centre, centre, (0,0,255), 3) # Draw the map centres
            self.areaCentres.append(self.getWorldPoint((centre[1], centre[0]), offset, mapResolution))

        #Sort the map points by the y value so the robot searches from the bottom of the map to the top
        self.areaCentres.sort(key=lambda x: x[1])
        
        cv2.imshow("Map", mapArrayColour) # Window showing the map array (Colour)
        cv2.waitKey(40)

        # Move to the first goal
        self.moveToGoal()

cv2.startWindowThread()
rospy.init_node('follow') #Initialise the Node (Class)
follow = Follow()
rospy.spin() #All user callbacks for the subscribers will be called from within spin

cv2.destroyAllWindows()