import pandas as pd
from sklearn.preprocessing import MinMaxScaler

tt      = 600
dataset = 'poker_hand'

df_dataset = pd.read_csv('datasets/' + str(dataset) + '.csv')

scaler = MinMaxScaler()
scaler.fit(df_dataset)
df_dataset = pd.DataFrame(data=scaler.transform(df_dataset))

df_parquet    = pd.read_parquet('results/' + str(dataset) + '/datasets/data_t' + str(tt) + '.parquet')
df_parquet_mc = pd.read_parquet('results/' + str(dataset) + '/flat_solutions/flat_solution_partitions_t' + str(tt) + '/partitions_mcs/partitions_mpts_20.parquet')

df_parquet_mc.drop('partition_mpts', axis=1, inplace=True)
df_parquet_mc.columns    = df_parquet_mc.columns.astype(int)
map_mc_to_cluster        = df_parquet_mc.iloc[0].to_dict()  # {1: 10, 2: 11, 3: 10}
df_parquet["id_cluster"] = df_parquet["id_mc"].map(map_mc_to_cluster)

print(df_dataset.head())
print(df_parquet.head(20))
print(df_parquet.groupby('id_cluster').size())
#print("Cluster: ", df_parquet_mc.iloc[0][1131]) #pegar o ID do cluster no qual o MC é

print("partition_mpts:")
print(df_parquet_mc)

#print(df_dataset[((df_dataset == df_parquet.iloc[1][df_dataset.columns].to_numpy()).all(axis=1))])