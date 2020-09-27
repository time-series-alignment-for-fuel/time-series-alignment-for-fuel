import matplotlib.pyplot as plt
import data_loader
from Alignment import *

ROOT_PATH = "../enrichData-30/"
TRUTH_PATH = "../alignData/"
INITIAL_PATH = "./initialData/"
MAP_PATH = "./initialMapConstraint/"
ALIGNMENT_DATA_PATH = "./enrichmentData/"
PARAMETER_RESULT_PATH = "./parameterChosenExp/"
PARAMETER_RESULT_PATH = "./exp6-4-1/"


def map_distance_plot():
    root_path = "../enrichData-30-old/"
    alignment = Alignment()
    dirs = os.listdir(root_path)
    dirs.sort()
    dirs = [d for d in dirs if d.endswith(".csv")]
    distance_list = []
    k = 10
    for idx, d in enumerate(dirs[k:k+1]):
        if d.endswith(".csv"):
            print(d)
            alignment.mapID = idx
            alignment.preprocessing(os.path.join(root_path, d))
            alignment.map_constraint_initialization(35)
            distance_list += alignment.alignment(120)

    distance_list = [d for d in distance_list if d < 100]
    dataPlot(distance_list, np.median(distance_list))


def dataPlot(data, median):
    n, bins, patches = plt.hist(data, 45, density=True, facecolor='g', alpha=0.75)
    plt.xlabel('interval')
    plt.ylabel('Probability')
    plt.title('Histogram')
    plt.grid(True)
    x = np.linspace(0, 40, 20)
    tmp = 1 / median

    print(tmp)
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
    print(median)

    # output to file
    result = [["Distance", "Probability"]]
    cumu_x = 0
    for patch in patches:
        result.append([cumu_x, patch.get_height()])
        cumu_x += patch.get_width()
    dataloader = data_loader.DataLoader()
    dataloader.write_to_file(result, 'distance-histogram.dat', split=' ')


if __name__ == '__main__':
    map_distance_plot()
