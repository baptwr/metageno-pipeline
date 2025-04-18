import pandas as pd 
from utils import *

SAMPLES_TABLE = config['samples']
SAMPLES = read_table(SAMPLES_TABLE)

rule fastqc_before_preprocessing:
    input: lambda wildcards: get_fastq_pair(SAMPLES_DF, wildcards.sample)
    output: directory("results/01_qc/fastqc/{sample}")
    conda: 
        "../envs/fastqc.yaml"
    log:
        stdout = "logs/01_qc/fastqc/{sample}.stdout",
        stderr = "logs/01_qc/fastqc/{sample}.stderr"   
    benchmark:
        "benchmarks/01_qc/fastqc/{sample}.benchmark.txt"
    params:
        out_dir = "results/01_qc/fastqc/{sample}"
    shell:
        """
        mkdir {params.out_dir} \
        && \
        fastqc {input[0]} -o {params.out_dir} > {log.stdout} 2> {log.stderr} \
        && \
        fastqc {input[1]} -o {params.out_dir} >> {log.stdout} 2>> {log.stderr}
        """