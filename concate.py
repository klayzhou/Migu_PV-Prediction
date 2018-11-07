from get_id import get_all_information
from extra_feature import process_time, calculate_releasetime_interval, calculate_createtime_interval
import os
import json

def concate_feature():

    init_feature = get_all_information()
    filePath = os.path.join(os.path.abspath('..'), 'dat', 'result.csv')

    dataset = []
    count = 0
    dataset_dir = os.path.join(os.path.abspath('..'), 'dataset')
    Click = {}
    time = ''

    with open(filePath, 'r', encoding='UTF-8') as fread:

        line = fread.readline()
        tmp = line.strip().split('|')
        time = tmp[0]
        Click[tmp[2]] = int(tmp[3])
        count = 1
        file_count = 1
        for line in fread.readlines():
            count = count + 1
            tmp = line.strip().split('|')
            if tmp[0]!= time:
                for key in Click:
                    if key in init_feature:
                        Item = init_feature[key]
                        weekday_vector,time_vector = process_time(time)
                        releasetime_interval = calculate_releasetime_interval(time, Item[7])
                        createtime_interval = calculate_createtime_interval(time, Item[1])
                        dataset.append([weekday_vector, time_vector, createtime_interval, releasetime_interval, Item[2],Item[3],
                                       Item[4], Item[8], Item[9],Item[10],Click[key]])
                Click.clear()
                if count>50000*file_count:
                    print('file ' + str(int(count / 50000)) + ' is processing')
                    with open(os.path.join(dataset_dir, str(int(count / 50000)) + '.txt'), 'w', encoding='UTF-8') as fwrite:
                        fwrite.write(json.dumps(dataset, ensure_ascii=False))
                        dataset.clear()
                    time = tmp[0]
                    file_count = file_count + 1

            if tmp[2] in Click:
                Click[tmp[2]] = Click[tmp[2]] + int(tmp[3])
            else:
                Click[tmp[2]] = int(tmp[3])

    for key in Click:
        if key in init_feature:
            Item = init_feature[key]
            weekday_vector, time_vector = process_time(time)
            releasetime_interval = calculate_releasetime_interval(time, Item[7])
            createtime_interval = calculate_createtime_interval(time, Item[1])
            dataset.append([weekday_vector, time_vector, createtime_interval, releasetime_interval, Item[2], Item[3], Item[4], Item[8],
                           Item[9], Item[10], Click[key]])

    print('file ' + str(int(count / 50000)) + ' is processing')
    with open(os.path.join(dataset_dir, str(int(count / 50000)) + '.txt'), 'w', encoding='UTF-8') as fwrite:
        fwrite.write(json.dumps(dataset, ensure_ascii=False))
        dataset.clear()
        Click.clear()
    print(count)
    print(count)


if __name__ == '__main__':
    concate_feature()
