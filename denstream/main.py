import pandas as pd
import sys
import os
import json

from denstream import *
from sklearn.preprocessing import MinMaxScaler
from river import stream

def set_stdout_stderr(result_dataset_path, dataset_name):
    stdout_path = os.path.join(result_dataset_path, f"stdout_{dataset_name}.txt")
    stderr_path = os.path.join(result_dataset_path, f"log_{dataset_name}.txt")
    sys.stdout  = open(stdout_path, 'w')
    sys.stderr  = open(stderr_path, 'w')

def check_dataset():
    # Checks if the dataset name was provided
    if len(sys.argv) < 2:
        print("Use: python script.py <name_of_dataset.csv>")
        sys.exit(1)

    dataset_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), "datasets/" + str(sys.argv[1]))
    dataset_name = sys.argv[1]

    if not os.path.exists(dataset_path):
        print(f"Dataset '{dataset_path}' not found.")
        sys.exit(1)

    # READING AND NORMALIZATION
    dataset = pd.read_csv(dataset_path, sep=',')

    scaler  = MinMaxScaler()
    scaler.fit(dataset)
    dataset = pd.DataFrame(data=scaler.transform(dataset)).to_numpy()
    print(len(dataset))

    return dataset_name, dataset

def check_parameters(dataset_name):
    # Read JSON with parameters from multiple datasets
    config_path = "../experiment_config.json"

    if not os.path.exists(config_path):
        print(f"Configuration file '{config_path}' not found.")
        sys.exit(1)

    with open(config_path, "r") as f:
        all_configs = json.load(f)

    if dataset_name not in all_configs:
        print(f"Parameters for dataset '{dataset_name}' not found in '{config_path}'.")
        sys.exit(1)
    
    return all_configs

def remove_keys_parameters(denstream_params):
    remove_keys = ["dataset", "mpts", "min_cluster_size", "percent", "method_summarization", "runtime", "plot", "save_partitions"]
    
    for key in remove_keys:
        denstream_params.pop(key, None)

    return denstream_params

def main():
    dataset_name, dataset    = check_dataset()
    all_configs              = check_parameters(dataset_name)
    denstream_params         = all_configs[dataset_name]
    result_dataset_path      = os.path.join("results", denstream_params['dataset']) #results/dataset_name
    
    if not os.path.exists(result_dataset_path):
        os.makedirs(result_dataset_path, exist_ok=True)

    # Redirects stdout and stderr to files
    set_stdout_stderr(result_dataset_path, denstream_params['dataset'])

    # filtro parametros denstream
    remove_keys_parameters(denstream_params)

    denstream = DenStream(**denstream_params)
    
    count_points       = 0
    objects_predict    = []

    dataset_predict            = pd.DataFrame(dataset)
    dataset_predict['cluster'] = -1

    for x, _ in stream.iter_array(dataset):
        denstream.learn_one(x)

        count_points += 1
        objects_predict.append(x)
        
        if count_points % denstream.n_samples_init == 0:
            index_p = ((count_points / denstream.n_samples_init) - 1) * denstream.n_samples_init
            for o in objects_predict:
                dataset_predict.loc[index_p, 'cluster'] = denstream.predict_one(o)
                index_p += 1
            print(dataset_predict)
            objects_predict = []

    dataset_predict.to_csv(result_dataset_path + "/dataset.csv", index=False)

if __name__ == "__main__":
    main()