# spark-submit EleventhCol.py /user/ly976/NYPD_Complaint_Data_Historic.csv EleventhCol.txt                                                                                                                      
# hfs -getmerge EleventhCol.txt EleventhCol.txt                                                                                                                                                                 

import sys
import os
from pyspark import SparkContext
from operator import add
import csv


def readfile(input):
    csvreader = csv.reader(input)
    next(csvreader)
    return csvreader

def fun(input):
    if input[10] == "":
        return "999\tText\tState\tNULL\t"
    elif (input[10] == "COMPLETED" or input[10] == "ATTEMPTED" or input[10] == "FAILED" or input[10] == "INTERRUPTED"):
        return "%s\tText\tState\tVALID\t" % (input[10])
    else:
        return "%s\tText\tState\tINVALID\t" % (input[10])


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print "usage: inputfile outputfile"
        exit(-1)
    sc = SparkContext()
    crime_data = sc.textFile(sys.argv[1])
    crime_data = crime_data.mapPartitions(readfile).map(fun)
    valid_count = crime_data.filter(lambda x: x.split("\t")[3] == "VALID").map(lambda x : ("Total number of VALID", 1)).reduceByKey(add).map(lambda x: "%s\t%s" % (x[0], x[1]))
    result = crime_data.union(valid_count)
    invalid_count = crime_data.filter(lambda x: x.split("\t")[3] == "INVALID").map(lambda x : ("Total number of INVALID", 1)).reduceByKey(add).map(lambda x: "%s\t%s" % (x[0], x[1]))
    result = result.union(invalid_count)
    null_count = crime_data.filter(lambda x: x.split("\t")[3] == "NULL").map(lambda x : ("Total number of NULL",  1)).reduceByKey(add).map(lambda x: "%s\t%s" % (x[0], x[1]))
    result = result.union(null_count)
    result.saveAsTextFile(sys.argv[2])
    sc.stop()
