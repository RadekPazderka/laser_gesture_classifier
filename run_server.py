from trainer.train import CTrain


from classifier.classifier import CClassifier

from tcp.communicator import CServer


MODE = "CLASSIFY" #TRAIN / CLASSIFY
CALIBRATION = True


def main():
    server = CServer("192.168.137.1", 20000)

    if CALIBRATION:
        pass

    if MODE == "TRAIN":
        trainer = CTrain(server, "train.json")
        trainer.start()

    elif MODE == "CLASSIFY":
        classifier = CClassifier(server)
        classifier.start()




if __name__ == '__main__':
    main()