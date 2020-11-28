from uu import test

import lmdb
import numpy as np
import caffe
import json
import os
import copy
import random


class CDataset:
    def __init__(self):
        pass


    def load_json_data(self, train_file_path, size=50):
        file_exists = os.path.isfile(train_file_path)
        if not file_exists:
            print("Error: File {0} not exists.".format(train_file_path))
            exit(1)
        json_data = json.load(open(train_file_path))
        return json_data

    def normalize_train_data(self, json_data, size=50):

        for label, values in json_data.items():
            for index, value in enumerate(values):
                start_pos = (size - len(value)) / 2
                new_list = [[0 for j in range(5)] for i in range(size)]
                new_list[start_pos:start_pos+len(value)] = value
                values[index] = new_list
        return json_data

    def extend_dataset(self, json_data, extend_sizes=[-5,-3,-1,1,3,5]):
        copy_json_data = copy.deepcopy(json_data)

        for label, values in json_data.items():
            new_values = []
            for index, value in enumerate(values):
                for extend_size in extend_sizes:
                    extend_value = copy.deepcopy(value)

                    for i, lasers_stat in enumerate(extend_value):
                        for j, laser_value in enumerate(lasers_stat):
                            if laser_value == 0 or laser_value == 100:
                                continue
                            extend_value[i][j] = min(max(laser_value + extend_size, 0), 100)

                    new_values.append(extend_value)
            copy_json_data[label] += new_values

        return copy_json_data


    def extend_dataset_move(self, json_data, move_by=[-3,-2,-1,1,2,3]):

        def _move_right(scan):
            test_value = scan[0]
            if not any(test_value):
                #all zeros
                scan.insert(0, scan.pop())

                return True
            return False

        def _move_left(scan):
            last_index = len(scan)-1

            test_value = scan[last_index]
            if not any(test_value):
                #all zeros
                scan.append(scan.pop(0))
                return True
            return False


        copy_json_data = copy.deepcopy(json_data)

        for label, values in json_data.items():
            new_values = []
            for index, value in enumerate(values):
                for move in move_by:
                    extend_value = copy.deepcopy(value)

                    save_it = True
                    for i in range(0, abs(move)):
                        if move > 0:
                            correct = _move_right(extend_value)
                        else:
                            correct = _move_left(extend_value)
                        if not correct:
                            save_it = False
                            break

                    if save_it:
                        new_values.append(extend_value)
            copy_json_data[label] += new_values

        return copy_json_data

    def reformat_dataset(self, json_data):
        flatten = []
        for label, values in json_data.items():
            for value in values:
                flatten.append({"label": str(label), "data": value})

        random.shuffle(flatten)

        split_index = int(len(flatten)*4/5.0)
        train_dataset = flatten[0:split_index]
        test_dataset = flatten[split_index:]

        return train_dataset, test_dataset


    def prepare_dataset(self, train_file_path):
        json_data = self.load_json_data(train_file_path)
        json_data = self.normalize_train_data(json_data)
        json_data = self.extend_dataset(json_data)
        json_data = self.extend_dataset_move(json_data)
        train_dataset, test_dataset = self.reformat_dataset(json_data)
        return train_dataset, test_dataset

    def create_lmdb(self, lmdb_name, data):

        N = len(data)

        # Let's pretend this is interesting data

        features_data = np.zeros((N, 1, 50, 5), dtype=np.uint8)
        labels = np.zeros(N, dtype=np.int64)

        for i, feature in enumerate(data):

            # concatenate images into 6 channel image
            np_feature = np.asarray(feature["data"])
            np_feature = np.expand_dims(np_feature, axis=0)
            features_data[i] = np_feature
            labels[i] = feature["label"]



        map_size = features_data.nbytes * 10

        env = lmdb.open(lmdb_name, map_size=map_size)

        with env.begin(write=True) as txn:
            # txn is a Transaction object
            for i in range(N):
                datum = caffe.proto.caffe_pb2.Datum()
                datum.channels = features_data.shape[1]
                datum.height = features_data.shape[2]
                datum.width = features_data.shape[3]
                datum.data = features_data[i].tobytes()  # or .tostring() if numpy < 1.9
                datum.label = int(labels[i])
                str_id = '{:08}'.format(i)

                # The encode is only essential in Python 3
                txn.put(str_id.encode('ascii'), datum.SerializeToString())

if __name__ == '__main__':
    dataset = CDataset()
    train_dataset, test_dataset = dataset.prepare_dataset("../classifier/train.json")


    dataset.create_lmdb("train", train_dataset)
    dataset.create_lmdb("test", test_dataset)

