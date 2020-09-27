from Alignment import *

ROOT_PATH = "../enrichData-30/"
TRUTH_PATH = "../alignData/"
INITIAL_PATH = "./initialData/"
MAP_PATH = "./initialMapConstraint/"
ALIGNMENT_DATA_PATH = "./enrichmentData/"
PARAMETER_RESULT_PATH = "./exp6-4-1/"

def do_initialization(w=30):
    alignment = Alignment()
    data_loader = DataLoader()
    dirs = os.listdir(ROOT_PATH)
    dirs.sort()
    index = 0
    for d in dirs:
        if d.endswith(".csv"):
            print(d)
            alignment.preprocessing(os.path.join(ROOT_PATH, d))
            result = alignment.initialization(w)
            data_loader.write_to_file(result, os.path.join(INITIAL_PATH, str(index) + '.csv'))
            index += 1
            print(len(result))

def do_alignment(root_path="../enrichData-30/", output_path="./alignmentData/", w=100, delta=50, ignore_delta=False, length=0):
    alignment = Alignment()
    data_loader = DataLoader()
    dirs = os.listdir(root_path)
    dirs.sort()
    index = 0
    for d in dirs:
        if d.endswith(".csv"):
            alignment.mapID = index
            alignment.preprocessing(os.path.join(root_path, d), length=length)
            if not ignore_delta:
                alignment.map_constraint_initialization(delta=delta)
            result = alignment.alignment(w=w, opt=False, ignore_delta=ignore_delta)
            data_loader.write_to_file(result, os.path.join(output_path, str(index) + '.csv'))
            index += 1

def generate_alignment_data_for_exp2_1(w_fix=120, delta_fix=30, ignore_delta=False):
    root_dir = "../sampledData/"
    output_root = "../exp6-4-1data/"
    for sr in range(10, 110, 10):
        print("sr={}".format(sr))
        root_path = os.path.join(root_dir, 'sr{}'.format(sr))
        output_path = os.path.join(output_root, "sr{}w{}delta{}".format(sr, w_fix, delta_fix))
        if not os.path.exists(output_path):
            os.mkdir(output_path)
            do_alignment(root_path, output_path, w_fix, delta_fix, ignore_delta=ignore_delta)

def generate_alignment_data_for_exp2_2(w_fix = 120, delta_fix = 30, ignore_delta=False):
    root_path = "../sampledData/sr50/"
    output_root = "../exp6-4-1data/"
    for w in range(60, 180, 10):
        print("w={}".format(w))
        output_path = os.path.join(output_root, "w{}delta{}".format(w, delta_fix))
        if not os.path.exists(output_path):
            os.mkdir(output_path)
            do_alignment(root_path, output_path, w, delta_fix, ignore_delta=ignore_delta)

    # 2.adjust delta, w = 120
    for delta in range(10, 45, 5):
        print("delta={}".format(delta))
        output_path = os.path.join(output_root, "delta{}w{}".format(delta, w_fix))
        if not os.path.exists(output_path):
            os.mkdir(output_path)
            do_alignment(root_path, output_path, w_fix, delta)


def generate_alignment_data_for_exp_baseline(w_fix = 120, delta_fix = 50, ignore_delta=False):
    root_path = ROOT_PATH
    output_root = "../exp-baseline-data/"
    length_list = [100, 500, 1000, 5000, 10000]
    for length in length_list:
        print("length={}".format(length))
        output_path = os.path.join(output_root, "map-{}".format(length))
        if not os.path.exists(output_path):
            os.mkdir(output_path)
            do_alignment(root_path, output_path, w_fix, delta_fix, ignore_delta=ignore_delta, length=length)



def test_recall_precision(w=100, delta=50):
    alignment = Alignment()
    dirs = os.listdir(ROOT_PATH)
    dirs.sort()
    data_loader = DataLoader()
    index = 0
    for d in dirs:
        if d.endswith(".csv"):
            print(d)
            total_len = d[d.index("-") + 1: d.index(".")]
            print("total length: {}".format(total_len))
            # load ground truth
            truth = data_loader.get_data(os.path.join(TRUTH_PATH, d))
            truth = [row[2]+row[3]+row[4] for row in truth[1:]]
            truth_len = len(truth)
            truth = set(truth)

            # do test
            alignment.mapID = index
            alignment.preprocessing(os.path.join(ROOT_PATH, d))
            alignment.map_constraint_initialization(delta=delta)
            result = alignment.alignment(w=w, opt=False)
            result_ = []
            for row in result:
                encoding_str = ""
                for x in range(3,6):
                    if str(row[x]).endswith(".0"):
                        encoding_str += str(row[x])[:-2]
                    else:
                        encoding_str += str(row[x])
                result_.append(encoding_str)
            # result = [str(row[3]) + str(row[4]) + str(row[5]) for row in result]
            result_len = len(result)
            result = result_
            index += 1

            # compute recall and precision
            truth_positive = len([x for x in result if x in truth])
            recall = truth_positive / truth_len
            precision = truth_positive / result_len
            f1 = 2 * precision * recall / (precision + recall)
            print("recall: {}  precision: {} f1: {}".format(recall, precision, f1))

def test_single_file(w=120, delta=50, length=300):
    alignment = Alignment()
    dirs = os.listdir(ROOT_PATH)
    dirs.sort()
    data_loader = DataLoader()
    index = 0
    d = "1001162201-19590.csv"
    truth = data_loader.get_data(os.path.join(TRUTH_PATH, d))
    truth = [row[2]+row[3]+row[4] for row in truth[1:1+length]]
    truth_len = len(truth)
    truth = set(truth)

    # do test
    alignment.mapID = index
    alignment.preprocessing(os.path.join(ROOT_PATH, d), length=length)
    start = time.time()
    alignment.map_constraint_initialization(delta=delta)
    result = alignment.alignment(w=w, opt=False)
    end = time.time()
    result_ = []
    for row in result:
        encoding_str = ""
        for x in range(3,6):
            if str(row[x]).endswith(".0"):
                encoding_str += str(row[x])[:-2]
            else:
                encoding_str += str(row[x])
        result_.append(encoding_str)
    result_len = len(result)
    result = result_
    index += 1

    # compute recall and precision
    truth_positive = len([x for x in result if x in truth])
    recall = truth_positive / truth_len
    precision = truth_positive / result_len
    f1 = 2 * precision * recall / (precision + recall)
    print("recall: {}  precision: {} f1: {}, len: {}, time: {}".format(recall, precision, f1, result_len, end - start))
    return precision, recall, f1, result_len, end - start

def test_single_file2(filename, w=100, delta=50):
    alignment = Alignment()
    data_loader = DataLoader()
    index = 0
    truth_file = "1001162201-19590.csv"
    truth = data_loader.get_data(os.path.join(TRUTH_PATH, truth_file))
    truth = [row[2]+row[3]+row[4] for row in truth[1:]]
    truth_len = len(truth)
    truth = set(truth)

    # do test
    alignment.mapID = index
    alignment.preprocessing(filename)
    start = time.time()
    alignment.map_constraint_initialization(delta=delta)
    result = alignment.alignment(w=w, opt=False)
    end = time.time()
    result_ = []
    for row in result:
        encoding_str = ""
        for x in range(3,6):
            if str(row[x]).endswith(".0"):
                encoding_str += str(row[x])[:-2]
            else:
                encoding_str += str(row[x])
        result_.append(encoding_str)
    result_len = len(result)
    result = result_
    index += 1

    # compute recall and precision
    truth_positive = len([x for x in result if x in truth])
    recall = truth_positive / truth_len
    precision = truth_positive / result_len
    f1 = 2 * precision * recall / (precision + recall)
    print("recall: {}  precision: {} f1: {}, len: {}, time: {}".format(recall, precision, f1, result_len, end - start))
    return precision, recall, f1, result_len, end - start

def parameterChosenExp():
    # this is the old parameter sensitivity exp, we have deleted it
    dataloader = DataLoader()
    for delta in range(10, 100, 5):
        filename = "delta{}.dat".format(delta)
        record = [["w", "recall", "precision", "f1"]]
        for w in range(20, 140, 10):
            print("w: {} delta: {}".format(w, delta))
            precision, recall, f1, result_amount, time_cost = test_single_file(w=w, delta=delta)
            record.append([w, round(recall, 3), round(precision, 3), round(f1, 3)])
        dataloader.write_to_file(record, os.path.join(PARAMETER_RESULT_PATH, filename), split=' ')

def exp1_parameter_chosen():
    # this is the exp 6.4-1, we test the w and delta
    dataloader = DataLoader()
    filename1 = "f1.dat"
    filename2 = "amount.dat"
    filename3 = "time.dat"

    title = ["w"]
    for delta in range(10, 40, 5):
        title.append("delta={}".format(delta))

    record1 = [title]
    record2 = [title]
    record3 = [title]

    for w in range(20, 140, 10):
        single_row1 = [w]
        single_row2 = [w]
        single_row3 = [w]
        for delta in range(10, 40, 5):
            print("w: {} delta: {}".format(w, delta))
            precision, recall, f1, result_amount, time_cost = test_single_file(w=w, delta=delta)
            single_row1.append(f1)
            single_row2.append(result_amount)
            single_row3.append(time_cost)
        record1.append(single_row1)
        record2.append(single_row2)
        record3.append(single_row3)
    dataloader.write_to_file(record1, os.path.join(PARAMETER_RESULT_PATH, filename1), split=' ')
    dataloader.write_to_file(record2, os.path.join(PARAMETER_RESULT_PATH, filename2), split=' ')
    dataloader.write_to_file(record3, os.path.join(PARAMETER_RESULT_PATH, filename3), split=' ')

def time_interval_parameter_chosen():
    my_root = './exp-time-interval/data'
    files = os.listdir(my_root)
    dataloader = DataLoader()
    files.sort()
    learning_rate = 5
    result = [["file", "w", "best_f1"]]
    for f in files[:10]:
        if f.endswith('.csv'):
            print(f)
            w = 130
            best_f1 = 0
            while True:
                precision, recall, f1, result_amount, time_cost = test_single_file2(filename=os.path.join(my_root, f), w=w, delta=35)
                if f1 >= best_f1:
                    w += learning_rate
                    best_f1 = f1
                else:
                    break
                print(w, f1)
            result.append([f, w, best_f1])
    dataloader.write_to_file(result, os.path.join('./exp-time-interval/', 'result.txt'), split=' ')


if __name__ == '__main__':
    test_single_file(120,30,19500)

