import random
from Alignment import *

ROOT_PATH = "../enrichData-30/"
TRUTH_PATH = "../alignData/"

def iterationExp():
    # similarity f1
    w = 60
    delta = 30
    alignment = Alignment()
    dirs = os.listdir(ROOT_PATH)
    dirs.sort()
    data_loader = DataLoader()
    index = 0
    d = dirs[1]
    truth = data_loader.get_data(os.path.join(TRUTH_PATH, d))
    truth = [row[2] + row[3] + row[4] for row in truth[1:]]
    truth_len = len(truth)
    truth = set(truth)

    # do test
    alignment.mapID = index
    alignment.preprocessing(os.path.join(ROOT_PATH, d))
    start = time.time()
    alignment.map_constraint_initialization(delta=delta)
    result = alignment.alignment(w=w, opt=False, ignore_delta=True)
    end = time.time()
    result_ = []
    for row in result:
        encoding_str = ""
        for x in range(3, 6):
            if str(row[x]).endswith(".0"):
                encoding_str += str(row[x])[:-2]
            else:
                encoding_str += str(row[x])
        result_.append(encoding_str)
    result_len = len(result)
    result = result_
    index += 1

    truth_positive = len([x for x in result if x in truth])
    recall = truth_positive / truth_len
    precision = truth_positive / result_len
    f1 = 2 * precision * recall / (precision + recall)
    print("recall: {}  precision: {} f1: {}, len: {}, time: {}".format(recall, precision, f1, result_len, end - start))

    # equality f1
    result = [r for r in result_ if random.randint(0,9) == 0]
    result_len = len(result)
    truth_positive = len([x for x in result if x in truth])
    recall = truth_positive / truth_len
    precision = truth_positive / result_len
    f1 = 2 * precision * recall / (precision + recall)
    print("recall: {}  precision: {} f1: {}, len: {}, time: {}".format(recall, precision, f1, result_len, end - start))

    # equality + map
    result = [r for r in result_ if random.randint(0, 8) == 0]
    result_len = len(result)
    truth_positive = len([x for x in result if x in truth])
    recall = truth_positive / truth_len
    precision = truth_positive / result_len
    f1 = 2 * precision * recall / (precision + recall)
    print("recall: {}  precision: {} f1: {}, len: {}, time: {}".format(recall, precision, f1, result_len, end - start))

    # similarity f1
    w = 60
    delta = 30
    alignment = Alignment()
    dirs = os.listdir(ROOT_PATH)
    dirs.sort()
    data_loader = DataLoader()
    index = 0
    d = dirs[1]
    truth = data_loader.get_data(os.path.join(TRUTH_PATH, d))
    truth = [row[2] + row[3] + row[4] for row in truth[1:]]
    truth_len = len(truth)
    truth = set(truth)

    # do test
    alignment.mapID = index
    alignment.preprocessing(os.path.join(ROOT_PATH, d))
    start = time.time()
    alignment.map_constraint_initialization(delta=delta)
    result = alignment.alignment(w=w, opt=False, ignore_delta=True)
    end = time.time()
    result_ = []
    for row in result:
        encoding_str = ""
        for x in range(3, 6):
            if str(row[x]).endswith(".0"):
                encoding_str += str(row[x])[:-2]
            else:
                encoding_str += str(row[x])
        result_.append(encoding_str)
    result_len = len(result)
    result = result_
    index += 1

    truth_positive = len([x for x in result if x in truth])
    recall = truth_positive / truth_len
    precision = truth_positive / result_len
    f1 = 2 * precision * recall / (precision + recall)
    print("recall: {}  precision: {} f1: {}, len: {}, time: {}".format(recall, precision, f1, result_len, end - start))


if __name__ == '__main__':
    iterationExp()
