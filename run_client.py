from detector.detector import CDetector
from tcp.communicator import CClient

def main():
    client = CClient("192.168.137.1", 20000) #"192.168.137.1"

    detector = CDetector([19,4,6,17,22], client)

    #detector.sending_test_data()
    detector.calibrate()
    detector.detect(min_gesture_size=15, max_gesture_size = 50, lives=10, refresh_time=0.04)




if __name__ == '__main__':
    main()