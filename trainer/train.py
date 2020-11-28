import json
import os.path
from termios import tcflush, TCIFLUSH
import sys
import select

class CTrain:

    def __init__(self, server, train_file="train.json"):
        self._server = server
        self._train_file = train_file

        file_exists = os.path.isfile(train_file)
        if not file_exists:
            with open(train_file, 'w') as outfile:
                json.dump({}, outfile)

        self.json_data = json.load(open(train_file))

    def start(self):
        self._server.ethernet_start_recv()

        while True:
            data = self._server.get_recv_data()
            self.save(data)

    def flush_input(self):
        while select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            sys.stdin.read(1)

    def save(self, data):

        print("recv data to save: {0}".format(data))
        self.flush_input()

        answer = raw_input("Save? (y/n) ")
        if answer.lower() == "y":
            label = raw_input("Input label: ")
            print ("saving data... (label: {0})".format(label))
            if label not in self.json_data:
                self.json_data[label] = []
            self.json_data[label].append(data)

            #update file
            with open(self._train_file, 'w') as outfile:
                json.dump(self.json_data, outfile)




    def lmdb_save(self):
        pass