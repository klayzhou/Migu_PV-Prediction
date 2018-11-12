import os
import json


def flatten():
    input_path = '../dataset/'
    data_path = '../dataset_actors/data/'
    target_path = '../dataset_actors/target/'
    files = os.listdir(input_path)
    for iter in files:
        file = os.path.join(input_path, iter)
        print(file)
        with open(file, 'r') as fread:
            res = fread.read()
            res = json.loads(res)
            flatten_data = []
            flatten_target = []
            for item in res:
                flatten_data.append(item[9])
                flatten_target.append(item[10])

            data_output = os.path.join(data_path, iter)
            target_output = os.path.join(target_path, iter)
            with open(data_output, 'w') as fwrite:
                fwrite.write(json.dumps(flatten_data, ensure_ascii=False))
            with open(target_output, 'w') as fwrite:
                fwrite.write(json.dumps(flatten_target, ensure_ascii=False))


if __name__ == '__main__':
    flatten()

