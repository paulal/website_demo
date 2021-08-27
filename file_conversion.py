"""This script converts the original fineli latin-1 csv files into utf-8 and removes the first row"""

import glob

source_names = glob.iglob('db/*.csv')


for source_filename in source_names:
    target_filename = source_filename[:-4] + '_import' + source_filename[-4:]
    
    with open(source_filename, encoding='latin-1') as source_file:
        with open(target_filename, mode='w', encoding='utf-8') as target_file:
            contents = list(source_file)
            for line in contents[1:]:
                target_file.write(line)
