import caffe
import numpy as np
import json


class CClassifier:
    def __init__(self, server):
        self._server = server

    def start(self):
        self._server.ethernet_start_recv()

        while True:
            data = self._server.get_recv_data()
            self.classify(data)

    def normalize_test_data(self, data, size=50):

        start_pos = (size - len(data)) / 2
        new_list = [[0 for j in range(5)] for i in range(size)]
        new_list[start_pos:start_pos+len(data)] = data

        return new_list

    def classify(self, data):
        #TODO: classify using neural network
        caffe.set_mode_gpu()

        print("recv data to classify: {0}".format(data))

        data = self.normalize_test_data(data)
        net = caffe.Net('../net/deploy.prototxt',
                        '../net/models/darkwolfnet/net_iter_300.caffemodel',caffe.TEST)
        np_feature = np.asarray(data)
        np_feature = np.expand_dims(np_feature, axis=0)
        np_feature = np.expand_dims(np_feature, axis=0)

        # load input and configure preprocessing
        transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})

        # note we can change the batch size on-the-fly
        # since we classify only one image, we change batch size from 10 to 1
        net.blobs['data'].reshape(1, 1, 50, 5)
        net.blobs['data'].data[...] = np_feature

        # compute
        out = net.forward()

        # predicted predicted class
        print out['prob'].argmax()

        pass


