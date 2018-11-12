import os
import json
import math

def flatten():
    input_path = '../dataset/'
    data_path = '../dataset_3.0/data/'
    target_path = '../dataset_3.0/target/'
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
                tmp = item[0]#0-6
                tmp.extend(item[1])#7-30
                tmp.append(math.exp(-1*item[2]))#31
                tmp.append(math.exp(-1*item[3]))#32
                tmp.extend(item[4])#33-
                tmp.extend(item[5])#
                tmp.append(math.exp(-1*int(item[6])))#
                tmp.extend(item[7])
                tmp.extend(item[8])
                flatten_data.append(tmp)
                flatten_target.append(item[10])

            data_output = os.path.join(data_path, iter)
            target_output = os.path.join(target_path, iter)
            with open(data_output, 'w') as fwrite:
                fwrite.write(json.dumps(flatten_data, ensure_ascii=False))
            with open(target_output, 'w') as fwrite:
                fwrite.write(json.dumps(flatten_target, ensure_ascii=False))


if __name__ == '__main__':
    flatten()

