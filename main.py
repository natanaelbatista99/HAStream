import json
import time
import pandas as pd
import sys
import os
import duckdb

from hastream import *
from river import stream
from sklearn.preprocessing import MinMaxScaler
from checkpoint_utils import get_next_version, save_checkpoint, load_checkpoint, remove_checkpoint

def check_dataset():
    # Checks if the dataset name was provided
    if len(sys.argv) < 2:
        print("Use: python script.py <name_of_dataset.csv>")
        sys.exit(1)

    dataset_path = os.path.join("datasets", sys.argv[1])
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
    config_path = "experiment_config.json"

    if not os.path.exists(config_path):
        print(f"Configuration file '{config_path}' not found.")
        sys.exit(1)

    with open(config_path, "r") as f:
        all_configs = json.load(f)

    if dataset_name not in all_configs:
        print(f"Parameters for dataset '{dataset_name}' not found in '{config_path}'.")
        sys.exit(1)
    
    return all_configs

def set_stdout_stderr(result_dataset_path, dataset_name):
    stdout_path = os.path.join(result_dataset_path, f"stdout_{dataset_name}.txt")
    stderr_path = os.path.join(result_dataset_path, f"log_{dataset_name}.txt")
    sys.stdout  = open(stdout_path, 'w')
    sys.stderr  = open(stderr_path, 'w')

def main():

    # Checking dataset file and experiement_config.json file
    dataset_name, dataset = check_dataset()
    all_configs           = check_parameters(dataset_name)
    hastream_params       = all_configs[dataset_name]

    # Verifica checkpoint
    result_dataset_path = os.path.join("results", hastream_params['dataset']) #results/dataset_name
    checkpoint_path     = os.path.join(result_dataset_path, "checkpoints")    #results/dataset_name/checkpoints
    os.makedirs(checkpoint_path, exist_ok=True)

    evaluation = Evaluation(hastream_params['dataset'], hastream_params['mpts'])
    evaluation.evaluation_mensure()
    sys.exit(1)

    hastream, start_index, version = load_checkpoint(checkpoint_path)

    # Redirects stdout and stderr to files
    set_stdout_stderr(result_dataset_path, hastream_params['dataset'])
    
    # HASTREAM OBJECT
    if hastream is None:
        hastream    = HAStream(**hastream_params)
        start_index = 0
        version     = get_next_version(checkpoint_path)

        print("New model started.")

    # Starting Model
    count_points = start_index
    start        = time.time()
    dataset      = dataset[start_index:]

    for x, _ in stream.iter_array(dataset):
        hastream.learn_one(x)
        
        count_points += 1
        
        if  count_points % hastream.n_samples_init == 0:
            hastream.predict_one()

            if (count_points / hastream.n_samples_init) % 2 == 1:
                save_checkpoint(hastream, count_points, version, checkpoint_path)
                version += 1

        #if count_points == 14000:
        #    break

    hastream.save_runtime_final()

    print("Time Total: ", time.time() - start)    

    # ASSESSMENT
    evaluation = Evaluation(hastream_params['dataset'], hastream_params['mpts'])
    evaluation.evaluation_mensure()

if __name__ == "__main__":
    main()