#!/bin/python
import sys
try:
    racekilometers=int(raw_input("Enter the race length in KM's :"))
except:
      print "Please enter the km's numeric"
      sys.exit()


timesec=0



try:
     timemin,timesec=map(int,raw_input("Enter the time you taken Minutes: Seconds: ").split())
     miles=racekilometers*0.621371
     pace=float(miles/(timemin+timesec))
     print "pace in mph/sec is %f" %pace
except ValueError:
                   print "Enter the values in numeric"
