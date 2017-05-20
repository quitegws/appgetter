#encoding=utf8

import os
import re


def find_diff_between_latest_and_2latest(root_dir):

    for parent, dirnames, filenames in os.walk(root_dir):
        target_files = []
        create_time_dic = {}
        for filename in filenames:
            if re.match(r'\d{8}_\d{2}-\d{2}-\d{2}.csv', filename):
                target_files.append(filename)
                full_dir = os.path.join(parent, filename)
                create_time = os.path.getctime(full_dir)
                create_time_dic[create_time] = filename

        ordered_create_time = sorted(create_time_dic.keys())

        if len(ordered_create_time) >= 2:
            latest_file = create_time_dic[ordered_create_time[len(ordered_create_time) - 1]]
            latest_file2 = create_time_dic[ordered_create_time[len(ordered_create_time) - 2]]

            diff_file = latest_file[:-4] + "_diff_" + latest_file2[:-4] + ".csv"

            full_dir = os.path.join(parent, latest_file)
            full_dir2 = os.path.join(parent, latest_file2)
            diff_dir = os.path.join(parent, diff_file)

            latest_file_data = set()
            latest_file_data2 = set()

            with open(full_dir) as f1:
                for line in f1:
                    latest_file_data.add(line)

            with open(full_dir2) as f2:
                for line in f2:
                    latest_file_data2.add(line)
            diff_data = latest_file_data.difference(latest_file_data2)

            f = open(diff_dir, "w")
            for app in diff_data:
                f.writelines(app)
            f.close()

if __name__ == "__main__":
    cwd = os.getcwd()
    find_diff_between_latest_and_2latest(cwd)
