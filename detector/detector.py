from gpiozero import LightSensor
import time
import random
import select
import sys

class CDetector:
    def __init__(self, pins, client):
        self._min_value = 0
        self._max_value = 100

        self._light_sensors = [LightSensor(int(pin)) for pin in pins ]
        self._threshold = 50 #default
        self._client = client

    def flush_input(self):
        while select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            sys.stdin.read(1)
    def calibrate(self):

        while True:
            raw_input("Light off all lasers")
            min_values = self.get_sensor_values()
            print("Min values: {0}".format(min_values))

            raw_input("Light on all lasers")
            max_values = self.get_sensor_values()
            print("Max values: {0}".format(max_values))

            self.flush_input()
            answer = raw_input("done, again? (y/n)")

            if answer == "n":
                print ("GJ, values are set")
                break

        self._max_value = sum(max_values) / len(max_values)
        self._min_value = sum(min_values) / len(min_values)
        self._threshold = ((self._max_value - self._min_value) * 0.75) + self._min_value 
        print("Min: {0}, Max: {1},  Threshold: {2}".format( self._min_value, self._max_value, self._threshold))


    def normalize_values(self, values):
        # print("Before norm: {0}".format(values))
        result = [int(((value - self._min_value) / float(self._max_value - self._min_value))*100.0) for value in values]
        return [min(max(value, 0),100) for value in result]


    def get_sensor_values(self):
        return [int(round(sensor.value,2)*100) for sensor in self._light_sensors]

    def scan(self):
        values = self.get_sensor_values()

        activated_sensors = [value < self._threshold for value in values]
        if any(activated_sensors):
            return values
        return []

    def sending_test_data(self):
        while True:
            values = []
            for i in range(0, random.randint(3,10)):
                values.append([x for x in range(5)])
                random.shuffle(values[i])
            print ("sending data: {0}".format(values))
            self._client.ethernet_send(values)
            time.sleep(2.5)


    def detect(self, min_gesture_size, max_gesture_size, lives, refresh_time=0.02):
        gesture = []
        bDetecting = False
        _lives = lives
        while True:

            values = self.scan()

            if values:
                bDetecting = True
                values = self.normalize_values(values)
                gesture.append(values)
                print ("Sensor values: {0}".format(values))

            else:
                if bDetecting:
                    _lives -= 1
                    print("Lifes: {0}".format(_lives))
                    if _lives < 0:
                        print ("len(gesture): {0}".format(len(gesture)))
                        if len(gesture) > min_gesture_size:
                            #Send it to pc for classification throught ethernet.

                            if len(gesture) > max_gesture_size:
                                print ("Warning: Gesture was cut on size: {0}".format(max_gesture_size))
                                gesture = gesture[:max_gesture_size]

                            print ("Sending data: {0}".format(gesture))
                            self._client.ethernet_send(gesture)

                        _lives = lives
                        gesture = [] #delete old gesture from list
                        bDetecting = False

            time.sleep(refresh_time)







