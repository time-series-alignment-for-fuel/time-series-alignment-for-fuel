import os
import numpy as np
import datetime
import random
import data_loader
import matplotlib.pyplot as plt

INPUT_DIR = "../enrichData-30"

def samplingSingleTime(data, sampling_rate):
    result = []
    for row in data:
        if random.random() <= sampling_rate:
            result.append(row)
    return result


def getData():
    dataloader = data_loader.DataLoader()
    files = os.listdir(INPUT_DIR)
    files.sort()
    result = [["file", "avg", "median"]]
    for file in files[4:5]:
        count = 0
        total_interval = 0
        interval_list = []
        if file.endswith(".csv"):
            data = dataloader.get_data(os.path.join(INPUT_DIR, file))
            for idx in range(1, len(data) - 1):
                delta_t1 = datetime.datetime.strptime(data[idx][1], "%Y-%m-%d %H:%M:%S")
                delta_t2 = datetime.datetime.strptime(data[idx + 1][1], "%Y-%m-%d %H:%M:%S")
                interval = (delta_t2 - delta_t1).seconds
                interval_list.append(interval)
                if interval < 1000 and interval != 0:
                    total_interval += interval
                    count += 1
            print(file, "avg:{}".format(total_interval / count), "median:{}".format(np.median(interval_list)))
            result.append([file, total_interval / count, np.median(interval_list)])
    dataloader.write_to_file(result, './exp-time-interval/interval.txt', split=' ')


def getGaussainDistribute():
    dataloader = data_loader.DataLoader()
    files = os.listdir(INPUT_DIR)
    files.sort()
    count = 0
    total_interval = 0

    for file in files[:]:
        interval_list = []
        if file.endswith(".csv"):
            data = dataloader.get_data(os.path.join(INPUT_DIR, file))
            for idx in range(1, len(data) - 1):
                delta_t1 = datetime.datetime.strptime(data[idx][1], "%Y-%m-%d %H:%M:%S")
                delta_t2 = datetime.datetime.strptime(data[idx + 1][1], "%Y-%m-%d %H:%M:%S")
                interval = (delta_t2 - delta_t1).seconds
                if interval < 200 and interval != 0:
                    total_interval += interval
                    count += 1
                    interval_list.append(interval)

            print(file, "avg:{}".format(total_interval / count), "median:{}".format(np.median(interval_list)))
            dataPlot(interval_list, total_interval / count)


def dataPlot(data, median):
    n, bins, patches = plt.hist(data, 40, density=True, facecolor='g', alpha=0.75)
    plt.xlabel('interval')
    plt.ylabel('Probability')
    plt.title('Histogram')
    plt.grid(True)
    x = np.linspace(0, 200, 40)
    tmp = 1 / median
    y = tmp * np.exp(-tmp * x)
    plt.plot(x, y, '-', lw=2)
    plt.show()
    cumu_prob = 0
    cumu_x = 0
    print(n)
    for patch in patches:
        cumu_x += patch.get_width()
        cumu_prob += patch.get_width() * patch.get_height()
        print("0-{}:{}".format(cumu_x, cumu_prob))
    # output to file
    result = [["Interval", "Probability"]]
    for i in range(0, 40):
        result.append([i*5, patches[i].get_height()])
    dataloader = data_loader.DataLoader()
    dataloader.write_to_file(result, 'interval-histogram.dat', split=' ')


if __name__ == "__main__":
    getGaussainDistribute()
