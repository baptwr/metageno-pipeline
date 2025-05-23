#!/usr/bin/env python3

import argparse
import os
import json
import shutil
import subprocess
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tqdm import tqdm
from venn import venn

def parse_arguments():
    parser = argparse.ArgumentParser(description='Perform Skani analysis on bins.\nRetrieves info related to bins recovered from one assembly approach.')
    subparsers = parser.add_subparsers(dest = 'subparser')

    # comparing and generating Venn diagram
    compare_parser = subparsers.add_parser('compare', help="Performing genomic comparison of dereplicated bins using Skani in order to identify 'shared' bins between assembly methods")

    compare_parser.add_argument('--bins', required=True, choices=['refined', 'dereplicated'], 
                        help='Type of bins to analyze')
    compare_parser.add_argument('--drep_ani', required=False, default=97, type=int,
                                help="If selected '--bins dereplicated', it is the dereplicated ANI threshold to find the MAG to analyze. For example, if you ran dRep with ANI 97%%, use '--ani_threshold 97' (default: 97)",)
    compare_parser.add_argument('--tmp', required=True, help='Temporary directory for intermediate files')
    compare_parser.add_argument('--output_file', required=True, help='File to save the output results (Skani matrix)')
    compare_parser.add_argument('--tsv_output', required=True, help='File to save the Skani matrix in TSV format')
    compare_parser.add_argument('--ani_threshold', type=float, required=True, default=99.9, help="Minimal ANI to consider two bins as the same (default: 99.9)")
    compare_parser.add_argument('--json_output', required=True, help='File to save the bins similarity results according to assembly methods (JSON)')
    compare_parser.add_argument('--venn_diagram', required=True, help='Where to save the Venn diagram')
    compare_parser.add_argument('--cpu', type=int, required=True, help='Number of CPU cores to use')

    # checking results
    check_parser = subparsers.add_parser('check', help="Recovering the taxonomical annotation and quality of bins obtained from only one assembly approach or from a given assembly")

    check_parser.add_argument('--json_results', required=True, help='Path to the JSON produced using "skani_analysis.py compare"')
    check_parser.add_argument('--tsv_output', required=True, help='File to save the results in TSV format')
    check_parser.add_argument('--assembly', required=True, choices=['unique', 'megahit', 'metaflye', 'metaspades', 'hybridspades'], help="Choose 'unique' to get a list of bins that were not found from at least a second assembly method, at the given ANI threshold you used with the 'compare' subcommand. Chose any other possible assembly method to get a list of bins recovered from the given assembly (it won't return the redundant bins coming from other asssemblies)")
    check_parser.add_argument('--drep_ani', required=False, default=97, type=int,
                              help="If selected '--bins dereplicated', it is the dereplicated ANI threshold to find the MAG to analyze. For example, if you ran dRep with ANI 97%%, use '--ani_threshold 97' (default: 97)",)

    # checking "clusters"
    clusters_parser = subparsers.add_parser('cluster', help="Recovering the groups of bins that share a certain identity threshold")

    clusters_parser.add_argument('--tsv_results', required=True, help='Path to matrix (TSV) produced using "skani_analysis.py compare"')
    clusters_parser.add_argument('--quality', action='store_true', help='Retrieve the CheckM2 metrics for the bins')
    clusters_parser.add_argument('--threshold', type=int, required=True, default=97,
                                 help='Minimal identity to consider two bins as being in the same cluster (default: 97)')
    clusters_parser.add_argument('--tsv_output_full', required=True, help='Path to save the bin-by-bin results in TSV format')
    clusters_parser.add_argument('--tsv_output_summary', required=True, help='Path to save the summary results in TSV format')

    return parser.parse_args()

def symlink_bins(src_dir, tmp_dir):
    """
    Create symbolic links for bin files from a source directory to a temporary directory.
    This function scans through the source directory, identifies bin files with the '.fa' extension
    within the 'final_bins' subdirectories of each sample, and creates symbolic links to these bin files
    in the temporary directory. It also generates a 'list_bins.txt' file in the temporary directory
    containing the paths to all the created symbolic links.
    """
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    list_bins = []

    print("Creating symlinks for bins files")
    for assembly in os.listdir(src_dir):
        assembly_dir = os.path.join(src_dir, assembly)
        print(f"Creating symlinks for bins from {assembly} assembly (progress bar displays samples)")
        if os.path.isdir(assembly_dir):
            for sample in tqdm(os.listdir(assembly_dir)):
                sample_dir = os.path.join(assembly_dir, sample, 'final_bins')
                if os.path.exists(sample_dir):
                    for bin_file in os.listdir(sample_dir):
                        if bin_file.endswith('.fa'):
                            src_bin = os.path.join(sample_dir, bin_file)
                            src_bin = os.path.abspath(src_bin)
                            new_bin_name = f"{assembly}.{sample}.{bin_file}"
                            dst_bin = os.path.join(tmp_dir, new_bin_name)
                            os.symlink(src_bin, dst_bin)
                            list_bins.append(dst_bin)
    
    print("Creating the list_bins.txt file")
    list_bins_path = os.path.join(tmp_dir, 'list_bins.txt')
    with open(list_bins_path, 'w') as f:
        for bin_path in list_bins:
            f.write(bin_path + '\n')
    
    return list_bins_path

def symlink_bins_dereplicated(src_dir, tmp_dir):
    """
    Symlinks and renames dereplicated bin files from source directory to a temporary directory.
    This function scans through the source directory for assemblies, finds the bin files within each assembly,
    creates symbolic links to these bin files in the temporary directory with a new naming convention, and 
    generates a list of these new paths in a text file.
    """
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    
    list_bins = []

    print("Symlinking and renaming dereplicated bins files")
    for assembly in os.listdir(src_dir):
        assembly_dir = os.path.join(src_dir, assembly, 'bins')
        if os.path.exists(assembly_dir):
            print(f"Symlinking and renaming bins from {assembly} assembly")
            for bin_file in tqdm(os.listdir(assembly_dir)):
                if bin_file.endswith('.fa'):
                    src_bin = os.path.join(assembly_dir, bin_file)
                    src_bin = os.path.abspath(src_bin)
                    new_bin_name = f"{assembly}.{bin_file}"
                    dst_bin = os.path.join(tmp_dir, new_bin_name)
                    os.symlink(src_bin, dst_bin)
                    list_bins.append(dst_bin)
    
    print("Creating the list_bins.txt file")
    list_bins_path = os.path.join(tmp_dir, 'list_bins.txt')
    with open(list_bins_path, 'w') as f:
        for bin_path in list_bins:
            f.write(bin_path + '\n')

    return list_bins_path

def run_skani(list_bins_path, output_file, cpu):
    print("Running Skani analysis")
    cmd = ['skani', 'triangle', '--medium', '-t', str(cpu), '-l', list_bins_path, '-o', output_file, '--full-matrix']
    subprocess.run(cmd, check=True)

def read_phylip_lower_triangular(filepath):
    """
    A function to read the Skani results (Phylip lower triangular matrix) into a 
    numpy matrix and to return it as a pandas dataframe for having the dimensions
    names
    """
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # get the number of elements
    num_elements = int(lines[0].strip())

    # initialize an empty numpy array
    matrix = np.zeros((num_elements, num_elements))
    bin_names = []

    # fill the numpy array with values
    for i in range(1, len(lines)):
        elements = lines[i].strip().split()
        values = list(map(float, elements[1:]))

        bin_name = os.path.basename(elements[0])
        bin_names.append(bin_name)
        
        matrix[i-1, :len(values)] = values
        matrix[:len(values), i-1] = values

    skani_results = pd.DataFrame(matrix, index=bin_names, columns=bin_names)
    return skani_results

def build_shared_bins_dictionary_dereplicated(skani_results, threshold=99.9):
    """
    Builds a dictionary with each key being a bin and the values being the 
    assemblies where a bin was found with identity >= `threshold`

    Will only work on dereplicated bins set
    """
    # initialize an empty dictionary to store shared bins
    shared_bins_dict = {}

    # iterate over rows (bins)
    for i in range(skani_results.shape[0]):
        bin_name = skani_results.index[i]
        shared_with = []

        print(f"Current bin {bin_name}")

        # iterate over columns (bins)
        for j in range(skani_results.shape[1]):
            if i != j:
                percentage_identity = skani_results.iloc[i, j]
                if percentage_identity >= threshold:
                    print(f"Found identity of {percentage_identity}% between {bin_name} and {skani_results.columns[j]}")
                    other_bin_name = skani_results.columns[j].split('.')[0]  # Get the bin name with assembly prefix
                    shared_with.append(other_bin_name)

        # add the original assembly (index name) to the list
        original_assembly = bin_name.split('.')[0]
        shared_with.append(original_assembly)

        # convert the list to a sorted unique list of strings
        shared_with = sorted(set(shared_with))

        # add to the dictionary with the bin name as key
        shared_bins_dict[bin_name] = shared_with

    return shared_bins_dict

def build_assembly_bins_dictionary_dereplicated(shared_bins_dict):
    """
    Builds a dictionary of set with each key being an assembly method
    and the value the bins identified as the same

    Will only work on dereplicated bins set
    """
    assembly_bins_dict = {}

    # iterate over each bin number and its shared assemblies
    for bin_name, shared_assemblies in shared_bins_dict.items():
        for assembly in shared_assemblies:
            if assembly not in assembly_bins_dict:
                assembly_bins_dict[assembly] = set()
            assembly_bins_dict[assembly].add(bin_name)

    return assembly_bins_dict

def build_clusters_bins_dictionary(skani_results: pd.DataFrame, threshold=99.9):
    """
    Builds a dictionary with each key being a "cluster" and the values being a list of bins that share >= `threshold` identity
    The idea is to iterate over `skani_results`'s bins, and for each bin not already assigned in a cluster check if it shares identity with other bins,
    if so, add them to the same cluster
    """

    already_checked_bins =[]
    # of the form: {'1': ['bin1', 'bin2', 'bin3'], '2: ['bin4', 'bin5']}
    clusters_dict = {}
    # dictionary to quiclky find the cluster of a bin
    # of the form: {'bin1': '1', 'bin2': '1', 'bin3': '1', 'bin4': '2', 'bin5': '2'}
    clusters_index = {}

    for idx, row in skani_results.iterrows():
        if idx not in already_checked_bins:
            for col, value in row.items():
                # those two bins share identity, so they are in the same cluster
                if value >= threshold:
                    if idx != col:
                        # if col has already been added to a cluster, we add idx to the same cluster
                        if col in clusters_index:
                            cluster = clusters_index[col]
                            clusters_dict[cluster].append(idx)
                            clusters_index[idx] = cluster
                            already_checked_bins.append(idx)
                        # if idx has not been added to any cluster, we create a new one and add it to it
                        elif idx not in clusters_index:
                            new_cluster = str(len(clusters_dict) + 1)
                            clusters_dict[new_cluster] = [idx, col]
                            clusters_index[idx] = new_cluster
                            clusters_index[col] = new_cluster
                            already_checked_bins.append(idx)
                            already_checked_bins.append(col)
                        # if idx has been added to a cluster, but col has not, we add col to the same cluster
                        else:
                            cluster = clusters_index[idx]
                            clusters_dict[cluster].append(col)
                            clusters_index[col] = cluster
                            already_checked_bins.append(col)

            # if idx has not been added to any cluster, we create a new one and add it to it
            if idx not in clusters_index:
                new_cluster = str(len(clusters_dict) + 1)
                clusters_dict[new_cluster] = [idx]
                clusters_index[idx] = new_cluster
                already_checked_bins.append(idx)

    assert len(clusters_index) == skani_results.shape[0], "The number of clusters does not match the number of bins in the Skani results"

    return clusters_dict

def checkm_metrics_bins_clusters(clusters_dict: dict, ani_threshold=97):
    """
    Retrieves the CheckM metrics for each bin in a cluster and returns a DataFrame with the metrics
    """
    # dictionary to store paths for corresponding name files based on assembly method
    corresponding_names_paths = {
        'hybridspades': "results/08_bins_postprocessing/genomes_list/hybridspades/unduplicated.tsv",
        'metaflye': "results/08_bins_postprocessing/genomes_list/metaflye/unduplicated.tsv",
        'megahit': "results/08_bins_postprocessing/genomes_list/megahit/unduplicated.tsv",
        'metaspades': "results/08_bins_postprocessing/genomes_list/metaspades/unduplicated.tsv"
    }

    for method, path in corresponding_names_paths.items():
        if os.path.isfile(path):
            corresponding_names_paths[method] = pd.read_csv(path, sep="\t")

    checkm_results_dir = f"results/08_bins_postprocessing/dereplicated_genomes_filtered_by_quality/{ani_threshold}"

    # preparing a dictionary to store the results
    results = {
        'cluster': [],
        'assembly': [],
        'bin': [],
        'contamination': [],
        'completeness': [],
        'contig_n50': [],
        'genome_size': []
    }

    for cluster, bins in tqdm(clusters_dict.items()):
        for bin in bins:
            # extracting the method from the bin name using regex
            method_match = re.match(r'^(hybridspades|metaflye|metaspades|megahit)', bin)
            if method_match:
                method = method_match.group(1)
            else:
                raise ValueError(f"Could not identify the assembly method from bin name: {bin}")

            bin = bin.replace(f"{method}.", "")
            bin = bin.replace(".fa", "")

            # constructing the path to the CheckM2 results table and loading it
            checkm2_quality_report = os.path.join(checkm_results_dir, method, "checkm2", "quality_report.tsv")
            checkm2_results_df = pd.read_csv(checkm2_quality_report, sep="\t")[['Name', 'Completeness', 'Contamination', 'Contig_N50', 'Genome_Size']]

            # filtering the results to keep only the rows related to this bin
            checkm2_results_df = checkm2_results_df[checkm2_results_df['Name'] == bin]

            # storing the results
            results['cluster'].append(cluster)
            results['assembly'].append(method)
            results['bin'].append(bin)
            results['contamination'].append(checkm2_results_df['Contamination'].values[0])
            results['completeness'].append(checkm2_results_df['Completeness'].values[0])
            results['contig_n50'].append(checkm2_results_df['Contig_N50'].values[0])
            results['genome_size'].append(checkm2_results_df['Genome_Size'].values[0])

    # returning the results as a DataFrame
    results_df = pd.DataFrame(results)

    # summarize the results by cluster
    summary_df = results_df.groupby('cluster').agg(
            num_bins=('bin', 'count'),  # number of bins in each cluster
            mean_contamination=('contamination', 'mean'),  # mean contamination for bins in each cluster
            mean_completeness=('completeness', 'mean'),  # mean completeness for bins in each cluster
            mean_contig_n50=('contig_n50', 'mean'),  # mean contig N50 for bins in each cluster
            mean_genome_size=('genome_size', 'mean'),  # mean genome size for bins in each cluster
            best_contamination=('contamination', lambda x: results_df.loc[x.idxmin(), 'assembly']),  # assembly method with the best (lowest) contamination
            best_completeness=('completeness', lambda x: results_df.loc[x.idxmax(), 'assembly']),  # assembly method with the best (highest) completeness
            best_contig_n50=('contig_n50', lambda x: results_df.loc[x.idxmax(), 'assembly']),  # assembly method with the best (highest) contig N50
        ).reset_index()
    summary_df['cluster'] = summary_df['cluster'].astype(int)
    summary_df = summary_df.set_index('cluster').sort_index()

    return results_df, summary_df

def save_assembly_bins_dict_to_json(assembly_bins_dict, output_path):
    with open(output_path, 'w') as json_file:
        json.dump(assembly_bins_dict, json_file, indent=4, default=list)

def identify_unique_bins(assembly_bins_dict):
    """
    Takes in input a dictionary of compared bins and returns a dictionary of bins that
    were recovered from an assembly approach only
    """

    # creating a set of bins , using all data
    all_values = set()
    for values in assembly_bins_dict.values():
        all_values.update(values)

    value_count = {value: 0 for value in all_values}

    # counting the occurrence of bins in each list
    for values in assembly_bins_dict.values():
        for value in values:
            value_count[value] += 1

    # identifying bins recovered only from an assembly approach 
    unique_values = {}
    for key, values in assembly_bins_dict.items():
        unique_values[key] = [value for value in values if value_count[value] == 1]

    return unique_values

def get_bins_by_assembly_method(assembly_bins_dict, assembly: str):
    """
    Takes in input a dictionary of compared bins and returns a dictionary of bins that
    were recovered from the given assembly method
    """
    if assembly not in assembly_bins_dict:
        raise ValueError(f"No assembly method '{assembly}' in the results.")

    return {assembly: assembly_bins_dict[assembly]}

def get_original_bin_name(corresponding_df: pd.DataFrame, bin_name: str):
    return corresponding_df[corresponding_df['unambiguous_filename'] == bin_name]['filename'].values[0]

def get_original_bin_path(corresponding_df: pd.DataFrame, bin_name: str):
    return corresponding_df[corresponding_df['unambiguous_filename'] == bin_name]['path'].values[0]

def get_sample_name_from_bins_refinement_path(path):
    pattern = re.compile("(megahit|metaspades|hybridspades|metaflye)\/(.*)\/final")
    match = pattern.search(path)

    if match:
        sample_name = match.group(2)
        return sample_name
    
def get_gtdb_taxo_from_bin_name(gtdb_tk_res: pd.DataFrame, bin: str):
    bin_without_extension = bin.replace(".fa", "")
    
    try:
        taxonomical_classification = gtdb_tk_res[gtdb_tk_res["user_genome"] == bin_without_extension]["classification"].values[0]
        return taxonomical_classification
    except IndexError:
        # if nothing was found, it returns None
        return None

def get_bins_taxo(assembly_bins_dict):
    """
    Gets the bin taxonomy using the GTDB-Tk annotation obtained by the pipeline.
    The function is generalized to handle any assembly method provided in assembly_bins_dict.
    """
    gtdb_tk_results_dir = "results/08_bins_postprocessing/gtdb_tk/"
    
    # dictionary to store paths for corresponding name files based on assembly method
    corresponding_names_paths = {
        'hybridspades': "results/08_bins_postprocessing/genomes_list/hybridspades/unduplicated.tsv",
        'metaflye': "results/08_bins_postprocessing/genomes_list/metaflye/unduplicated.tsv",
        'megahit': "results/08_bins_postprocessing/genomes_list/megahit/unduplicated.tsv",
        'metaspades': "results/08_bins_postprocessing/genomes_list/metaspades/unduplicated.tsv"
    }

    # checking if the GTDB-Tk results directory exists
    if not os.path.isdir(gtdb_tk_results_dir):
        raise FileNotFoundError(f"Folder '{gtdb_tk_results_dir}' does not exist.")
    
    # checking if the corresponding name files exist for the provided assembly methods
    for method in assembly_bins_dict.keys():
        if method in corresponding_names_paths:
            file_path = corresponding_names_paths[method]
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File '{file_path}' does not exist.")
            # load the corresponding names DataFrame for the current method
            corresponding_names_paths[method] = pd.read_csv(file_path, sep="\t")
        else:
            raise ValueError(f"No corresponding name file defined for assembly method '{method}'.")

    # preparing a dictionary to store the results
    results = {
        'assembly': [],
        'original_bin_name': [],
        'renamed_bin': [],
        'gtdb_classification': []
    }

    # looping over each assembly method in the dictionary
    for method, bins in tqdm(assembly_bins_dict.items()):
        for bin in bins:
            if method in bin:
                bin = bin.replace(f"{method}.", "")

                # getting the original name of the bin before renaming
                original_name = get_original_bin_name(corresponding_names_paths[method], bin)
                # getting the original path to determine the sample name
                path = get_original_bin_path(corresponding_names_paths[method], bin)
                # extracting the sample name from the bin's path
                sample_name = get_sample_name_from_bins_refinement_path(path)

                # constructing the path to the GTDB-Tk bacterial summary file and loading it
                gtdb_taxo_annotation_bact = os.path.join(gtdb_tk_results_dir, method, sample_name, "gtdbtk.bac120.summary.tsv")
                gtdb_taxo_annotation_bact_df = pd.read_csv(gtdb_taxo_annotation_bact, sep="\t")

                # trying to retrieve the taxonomy using the bacterial GTDB-Tk output
                taxonomy = get_gtdb_taxo_from_bin_name(gtdb_taxo_annotation_bact_df, original_name)
                # if no taxonomy was found, check if the bin might be archaeal
                if taxonomy is None:
                    gtdb_taxo_annotation_arch = os.path.join(gtdb_tk_results_dir, method, sample_name, "gtdbtk.ar53.summary.tsv")
                    gtdb_taxo_annotation_arch_df = pd.read_csv(gtdb_taxo_annotation_arch, sep="\t")
                    taxonomy = get_gtdb_taxo_from_bin_name(gtdb_taxo_annotation_arch_df, original_name)

                # storing the results
                results['assembly'].append(method)
                results['original_bin_name'].append(original_name)
                results['renamed_bin'].append(bin)
                results['gtdb_classification'].append(taxonomy)

    # returning the results as a DataFrame
    return pd.DataFrame(results)

def get_bins_quality(bins_taxonomy: pd.DataFrame, ani_threshold: int):
    """
    Gets the bin quality check using the CheckM2 results obtained by the pipeline

    `bins_taxonomy` is the DataFrame returned by the `get_bins_taxo` function
    """

    # ensuring we have the folder containing the CheckM2 results for dereplicated bins
    dereplication_checkm_qc_dir = f"results/08_bins_postprocessing/dereplicated_genomes_filtered_by_quality/{ani_threshold}"
    
    if not os.path.isdir(dereplication_checkm_qc_dir):
        raise FileNotFoundError(f"Folder '{dereplication_checkm_qc_dir}' does not exist.")
    
    # removing the ".fa" extension in bins name, since these are absent in the CheckM2 results
    bins_taxonomy['original_bin_name'] = bins_taxonomy['original_bin_name'].str.replace(".fa", "")
    bins_taxonomy['renamed_bin'] = bins_taxonomy['renamed_bin'].str.replace(".fa", "")

    # getting the type of assembly we have in bins_taxonomy
    assembly_type = bins_taxonomy['assembly'].unique().tolist()

    processed_dataframes = []
    for assembly in assembly_type:
        # filtering the results to keep only the rows related to this assembly method
        taxonomy_df_filtered = bins_taxonomy[bins_taxonomy['assembly'] == assembly]

        # loading the corresponding results table into a DataFrame
        checkm2_results = os.path.join(dereplication_checkm_qc_dir, assembly, "checkm2", "quality_report.tsv")
        checkm2_results_df = pd.read_csv(checkm2_results, sep="\t")[['Name', 'Completeness', 'Contamination']]
                
        # joining it on the GTDB taxonomy we recovered
        taxonomy_df_filtered = pd.merge(taxonomy_df_filtered, checkm2_results_df, how="left",
                                        left_on="renamed_bin", right_on="Name").drop(columns=["Name"])
        
        processed_dataframes.append(taxonomy_df_filtered)

    # concatenating all DataFrames to have the final results, containing both GTDB-Tk annotation and CheckM2 bins results
    # for each assembly method tested
    return pd.concat(processed_dataframes, ignore_index=True).rename(columns={"Contamination": "contamination", "Completeness": "completeness"})

def subcommand_compare(args):
    """
    Handling `skani_analysis.py compare ...`
    """
    if args.bins == 'refined':
        src_dir = 'results/07_bins_refinement/binette'
        list_bins_path = symlink_bins(src_dir, args.tmp)
    elif args.bins == 'dereplicated':
        src_dir = f'results/08_bins_postprocessing/dereplicated_genomes_filtered_by_quality/{args.drep_ani}'
        list_bins_path = symlink_bins_dereplicated(src_dir, args.tmp)

    run_skani(list_bins_path, args.output_file, args.cpu)

    # Read the Skani result and save as TSV
    skani_matrix = read_phylip_lower_triangular(args.output_file)
    skani_matrix.to_csv(args.tsv_output, sep='\t', index=True, header=True)

    print(f"Skani matrix saved to {args.tsv_output}")

    print(f"Now drawing a Venn diagram if possible")
    if args.bins == 'dereplicated':
        shared_bins = build_shared_bins_dictionary_dereplicated(skani_matrix, args.ani_threshold)
        bins_by_assembly = build_assembly_bins_dictionary_dereplicated(shared_bins)

        # exporting the bins_by_assembly into a JSON
        save_assembly_bins_dict_to_json(bins_by_assembly, args.json_output)
        
        # plotting the data using a Venn diagram
        venn(bins_by_assembly)
        plt.savefig(args.venn_diagram)

        print(f"Venn diagram saved to {args.venn_diagram}")
    else:
        print(f"Venn diagram for refined bins identity was not implemented")

def subcommand_check(args):
    """
    Handling `skani_analysis.py check ...`  
    """

    # reading the JSON as a dictionary
    with open(args.json_results) as json_file:
        data = json.load(json_file)

        if args.assembly == 'unique':
            # bins that could be recovered using one assembly approach only
            bins = identify_unique_bins(data)
        else:
            # if not, the user wants to get the bins identified from a given assembly approach,
            # so including similar bins identified from other assembly approaches
            bins = get_bins_by_assembly_method(data, args.assembly)

        # getting the taxonomy of these bins
        bins_taxonomy = get_bins_taxo(bins)
        
        # getting the quality of these bins
        bins_taxonomy_quality = get_bins_quality(bins_taxonomy, args.drep_ani)

        # saving the results
        bins_taxonomy_quality.to_csv(args.tsv_output, sep="\t", index=False)

def subcommand_cluster(args):
    """
    Handling `skani_analysis.py cluster ...`
    """

    # reading the TSV file as a DataFrame
    skani_results = pd.read_csv(args.tsv_results, sep="\t", index_col=0)

    # building the clusters dictionary
    clusters_dict = build_clusters_bins_dictionary(skani_results, args.threshold)

    # getting the quality of the bins in each cluster
    bins_quality, summary_quality = checkm_metrics_bins_clusters(clusters_dict, args.threshold)

    # saving the quality results
    bins_quality.to_csv(args.tsv_output_full, sep="\t", index=False)
    summary_quality.to_csv(args.tsv_output_summary, sep="\t", index=False)

def main():
    args = parse_arguments()

    # skani_analysis.py compare ...
    if args.subparser == 'compare':
        subcommand_compare(args)
    elif args.subparser == 'check':
        subcommand_check(args)
    elif args.subparser == 'cluster':
        subcommand_cluster(args)

if __name__ == "__main__":
    main()
