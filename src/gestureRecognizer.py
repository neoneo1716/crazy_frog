#!/usr/bin/env python
# license removed for brevity
import rospy
import pickle
import sklearn
from std_msgs.msg import String
from leap_motion.msg import leapros
from std_msgs.msg import Int32
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from sklearn import neighbors, datasets

pub = None

classifier = None
circular_buffer = np.empty([300], dtype=float)
previous_gesture = None

def shift(arr, num, fill_value=np.nan):
    result = np.empty_like(arr)
    if num > 0:
        result[:num] = fill_value
        result[num:] = arr[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = arr[-num:]
    else:
        result = arr
    return result


def callback(data):
    global classifier
    global pub
    global circular_buffer
    global previous_gesture
    X = np.empty([87], dtype=float)
    X = [data.direction.x, data.direction.y, data.direction.z,
                data.normal.x, data.normal.y, data.normal.z,
                data.palmpos.x, data.palmpos.y, data.palmpos.z,
                data.ypr.x, data.ypr.y, data.ypr.z,
                data.thumb_metacarpal.x,    data.thumb_metacarpal.y,   data.thumb_metacarpal.z,
                data.thumb_proximal.x,      data.thumb_proximal.y,     data.thumb_proximal.z,
                data.thumb_intermediate.x,  data.thumb_intermediate.y, data.thumb_intermediate.z,
                data.thumb_distal.x,        data.thumb_distal.y,       data.thumb_distal.z,
                data.thumb_tip.x,           data.thumb_tip.y,          data.thumb_tip.z,
                data.index_metacarpal.x,    data.index_metacarpal.y,   data.index_metacarpal.z,
                data.index_proximal.x,      data.index_proximal.y,     data.index_proximal.z,
                data.index_intermediate.x,  data.index_intermediate.y, data.index_intermediate.z,
                data.index_distal.x,        data.index_distal.y,       data.index_distal.z,
                data.index_tip.x,           data.index_tip.y,          data.index_tip.z,
                data.middle_metacarpal.x,    data.middle_metacarpal.y,   data.middle_metacarpal.z,
                data.middle_proximal.x,      data.middle_proximal.y,     data.middle_proximal.z,
                data.middle_intermediate.x,  data.middle_intermediate.y, data.middle_intermediate.z,
                data.middle_distal.x,        data.middle_distal.y,       data.middle_distal.z,
                data.middle_tip.x,           data.middle_tip.y,          data.middle_tip.z,
                data.ring_metacarpal.x,    data.ring_metacarpal.y,   data.ring_metacarpal.z,
                data.ring_proximal.x,      data.ring_proximal.y,     data.ring_proximal.z,
                data.ring_intermediate.x,  data.ring_intermediate.y, data.ring_intermediate.z,
                data.ring_distal.x,        data.ring_distal.y,       data.ring_distal.z,
                data.ring_tip.x,           data.ring_tip.y,          data.ring_tip.z,
                data.pinky_metacarpal.x,    data.pinky_metacarpal.y,   data.pinky_metacarpal.z,
                data.pinky_proximal.x,      data.pinky_proximal.y,     data.pinky_proximal.z,
                data.pinky_intermediate.x,  data.pinky_intermediate.y, data.pinky_intermediate.z,
                data.pinky_distal.x,        data.pinky_distal.y,       data.pinky_distal.z,
                data.pinky_tip.x,           data.pinky_tip.y,          data.pinky_tip.z,]

    
    
    circular_buffer = shift(circular_buffer, 1, classifier.predict([X])[0])
    mode = stats.mode(circular_buffer, axis=None)
    rospy.loginfo(np.array_str(circular_buffer))
    rospy.loginfo(classifier.predict([X])[0])
    rospy.loginfo(str(mode[0][0]) + " " + str(previous_gesture))
    if mode[0][0] != previous_gesture:
        pub.publish(mode[0][0])
        previous_gesture = mode[0][0]


def recording():
        global classifier 
        global pub
        classifier = pickle.load(open("../classification_data/classifier_output/classifier.pkl"))
        rospy.init_node('gestureRecognizer', anonymous=True)
        sub = rospy.Subscriber('leapmotion/data', leapros , callback)
        pub = rospy.Publisher('crazyFrog/current_gesture', Int32, queue_size = 10)
        rospy.spin()

if __name__ == '__main__':
    try:
        recording()
    except rospy.ROSInterruptException:
        pass