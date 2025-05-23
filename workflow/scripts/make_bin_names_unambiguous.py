"""
This script is used before the dRep step. Bins should
be copied in another folder to use this script and dRep. 
It will allows to rename
bins that have the same filename in order to use dRep, but in 
keeping track of the changes in a table
"""

import pandas as pd
import sys
import os
import shutil
import gzip

def get_bin_filename(bins_df: pd.DataFrame):
    """
    Will extract the bin filename from the path and add it
    to a new column
    """

    bins_df["filename"] = bins_df["path"].apply(lambda x: os.path.basename(x))
    
    return bins_df.sort_values(by="filename")

def make_unduplicated_filenames(bins_df: pd.DataFrame):
    """
    Will check if there are duplicated bins name and, if it the
    case, it will rename the duplicated ones. Also, it will ensure
    that the unambiguous filenames do not have .fa.gz extension.
    """

    # count the number of each filename
    bins_df['filename_count'] = bins_df.groupby('filename').cumcount() + 1
    # adding a new column unambiguous_filename for unduplicated bins name
    def generate_unambiguous_filename(row):
        filename, ext = os.path.splitext(row['filename'])
        if row['filename'].endswith('.fa.gz'):
            filename, ext2 = os.path.splitext(filename)
            ext = ext2 + ext  # preserve the original extension
        if row['filename_count'] > 1:
            return f"{filename}_{row['filename_count'] - 1}{ext}"
        return filename + ext

    bins_df['unambiguous_filename'] = bins_df.apply(generate_unambiguous_filename, axis=1)
    # clean by removing the temporary column
    bins_df.drop('filename_count', axis=1, inplace=True)
    
    return bins_df.sort_values(by=["filename", "unambiguous_filename"])

def copy_rename(bins_df: pd.DataFrame, destination_folder: str):
    """
    Will copy the bins located at "path" and rename them if needed as indicated
    in "unambiguous_filename". If the files are gzipped, they will be uncompressed
    after being copied.
    """

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    for index, row in bins_df.iterrows():
        source_path = row['path']
        dest_path = os.path.join(destination_folder, row['unambiguous_filename'])
        print(f"Copying {source_path} to {dest_path}")
        shutil.copy(source_path, dest_path)
        
        # check if the file is gzipped and uncompress it
        if source_path.endswith('.gz'):
            with gzip.open(dest_path, 'rb') as f_in:
                with open(dest_path[:-3], 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(dest_path)  # remove the .gz file after uncompressing
            dest_path = dest_path[:-3]  # update dest_path to the uncompressed file path


if __name__ == "__main__":
    # path to a table that contain the original path to bins
    bins_path = sys.argv[1]
    bins_df = pd.read_csv(bins_path, names=["path"])

    bins_df = get_bin_filename(bins_df)
    bins_df = make_unduplicated_filenames(bins_df)

    print(bins_df)

    # export path
    export_path = sys.argv[2]
    bins_df.to_csv(export_path, index=False, sep="\t")

    # copying bins
    dest_path = sys.argv[3]
    copy_rename(bins_df, dest_path)