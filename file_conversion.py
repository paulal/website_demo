"""Fineli Latin-1 to UTF-8 converter

This script allows you to change the character encoding of Fineli csv files
in preparation for importing them into an Sqlite database.

It assumes the csv files to be processed to be one level below the directory where
this script is, in 'db/'. It will not overwrite the old files but creates new
copies with '_import' in their names.

The script also removes the first row (column names) from all files and changes
the decimal separator in component_values.csv into a decimal point.
"""

import glob

source_names = glob.iglob('db/*.csv')


for source_filename in source_names:
    target_filename = source_filename[:-4] + '_import' + source_filename[-4:]
    
    with open(source_filename, encoding='latin-1') as source_file:
        with open(target_filename, mode='w', encoding='utf-8') as target_file:
            contents = list(source_file)
            for line in contents[1:]:
                # change decimal separator to full stop to avoid problems with sqlite
                if source_filename == "db/component_value.csv":
                    line = line.replace(",", ".")
                target_file.write(line.lower())
