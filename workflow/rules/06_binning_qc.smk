SAMPLES_TABLE = config['samples']
SAMPLES = read_table(SAMPLES_TABLE)
SAMPLES_LR = read_table_long_reads(SAMPLES_TABLE)
ASSEMBLER = config['assembly']['assembler']
ASSEMBLER_LR = config['assembly']['long_read_assembler']
HYBRID_ASSEMBLER = config['assembly']['hybrid_assembler']

# taking into account the case where we don't have SR assembly
if ASSEMBLER == None:
       ASSEMBLER = []

# taking into account the case where we don't have hybrid assembly
if HYBRID_ASSEMBLER == None:
       HYBRID_ASSEMBLER = []

# taking into account the case where we don't have LR
if ASSEMBLER_LR == None:
       ASSEMBLER_LR = []

SHORT_READ_BINNER = config['binning']['binner']
LONG_READ_BINNER = config['binning']['long_read_binner']

# taking into account the case where we don't have SR binner
if SHORT_READ_BINNER == None:
       SHORT_READ_BINNER = []

# taking into account the case where we don't have LR binner
if LONG_READ_BINNER == None:
       LONG_READ_BINNER = []

wildcard_constraints:
    assembler_sr_hybrid = "|".join(ASSEMBLER + HYBRID_ASSEMBLER) if ASSEMBLER + HYBRID_ASSEMBLER != [] else "none",
    assembler_lr = "|".join(ASSEMBLER_LR) if ASSEMBLER_LR != [] else "none"

# download the database for CheckM2
rule checkm2_database:
    output:
        "results/06_binning_qc/checkm2/database/CheckM2_database/uniref100.KO.1.dmnd"
    conda:
        "../envs/checkm2.yaml"
    log:
        stdout = "logs/06_binning_qc/checkm2/checkm2.db.stdout",
        stderr = "logs/06_binning_qc/checkm2/checkm2.db.stderr"
    benchmark:
        "benchmarks/06_binning_qc/checkm2/checkm2.db.benchmark.txt"
    params:
        output_path = "results/06_binning_qc/checkm2/database"
    shell:
        """
        checkm2 database --download --path {params.output_path} \
            > {log.stdout} 2> {log.stderr}
        """

rule checkm2_assessment:
    input:
        # folder with bins created in step 05. One folder per binning program
        bins = "results/05_binning/{binner}/bins/{assembler_sr_hybrid}/{sample}", 
        diamond_database = "results/06_binning_qc/checkm2/database/CheckM2_database/uniref100.KO.1.dmnd"
    output:
        "results/06_binning_qc/checkm2/{binner}/{assembler_sr_hybrid}/{sample}/quality_report.tsv",
        out_dir = directory("results/06_binning_qc/checkm2/{binner}/{assembler_sr_hybrid}/{sample}")
    conda:
        "../envs/checkm2.yaml"
    log:
        stdout = "logs/06_binning_qc/checkm2/{binner}/{assembler_sr_hybrid}/{sample}.assessment.stdout",
        stderr = "logs/06_binning_qc/checkm2/{binner}/{assembler_sr_hybrid}/{sample}.assessment.stderr"
    benchmark:
        "benchmarks/06_binning_qc/checkm2/{binner}/{assembler_sr_hybrid}/{sample}.assessment.benchmark.txt"
    threads: config['checkm2']['threads']
    wildcard_constraints:
        binner = "|".join(SHORT_READ_BINNER)
    shell:
        """
        echo {input.bins} \
        && \
        checkm2 predict --input {input.bins}/bins --threads {threads} \
            -x .gz \
            --database_path {input.diamond_database} \
            --output-directory {output.out_dir} > {log.stdout} 2> {log.stderr}
        """

rule checkm2_assessment_LR:
    input:
        # folder with bins created in step 05. One folder per binning program
        bins = "results/05_binning/{long_read_binner}/bins/{assembler_lr}/{sample_lr}", 
        diamond_database = "results/06_binning_qc/checkm2/database/CheckM2_database/uniref100.KO.1.dmnd"
    output:
        "results/06_binning_qc/checkm2/{long_read_binner}/{assembler_lr}/{sample_lr}/quality_report.tsv",
        out_dir = directory("results/06_binning_qc/checkm2/{long_read_binner}/{assembler_lr}/{sample_lr}")
    conda:
        "../envs/checkm2.yaml"
    log:
        stdout = "logs/06_binning_qc/checkm2/{long_read_binner}/{assembler_lr}/{sample_lr}.assessment.stdout",
        stderr = "logs/06_binning_qc/checkm2/{long_read_binner}/{assembler_lr}/{sample_lr}.assessment.stderr"
    benchmark:
        "benchmarks/06_binning_qc/checkm2/{long_read_binner}/{assembler_lr}/{sample_lr}.assessment.benchmark.txt"
    threads: config['checkm2']['threads']
    wildcard_constraints:
        long_read_binner = "|".join(LONG_READ_BINNER)
    shell:
        """
        echo {input.bins} \
        && \
        checkm2 predict --input {input.bins}/bins --threads {threads} \
            -x .gz \
            --database_path {input.diamond_database} \
            --output-directory {output.out_dir} > {log.stdout} 2> {log.stderr}
        """

# this rule merges CheckM2 quality reports into a single table
rule checkm2_merge_results:
    input:
        expand("results/06_binning_qc/checkm2/{binner}/{assembler}/{{sample}}/quality_report.tsv",
               assembler = ASSEMBLER + HYBRID_ASSEMBLER,
               binner = config['binning']['binner']),
        # long reads based results
        expand("results/06_binning_qc/checkm2/{long_read_binner}/{assembler_lr}/{{sample}}/quality_report.tsv",
               assembler_lr = ASSEMBLER_LR if ASSEMBLER_LR != None else [],
               long_read_binner = LONG_READ_BINNER if ASSEMBLER_LR != None else []) # the conditions
                                                                                    # are for requiring such
                                                                                    # inputs
                                                                                    # only if the user has 
                                                                                    # long reads to
                                                                                    # analyze 
    output:
        "results/06_binning_qc/checkm2/samples/{sample}/all_quality_reports.tsv"
    conda:
        "../envs/python.yaml"
    log:
        stdout = "logs/06_binning_qc/checkm2/samples/{sample}/merge_reports.stdout",
        stderr = "logs/06_binning_qc/checkm2/samples/{sample}/merge_reports.stderr"
    benchmark:
        "benchmarks/06_binning_qc/checkm2/samples/{sample}/merge_reports.benchmark.txt"
    shell:
        """
        python workflow/scripts/merge_checkm2_reports.py \
            --input {input} \
            --output {output} \
        > {log.stdout} 2> {log.stderr}
        """

rule checkm2_plot_results:
    input:
        "results/06_binning_qc/checkm2/samples/{sample}/all_quality_reports.tsv"
    output:
        "results/06_binning_qc/checkm2/samples/{sample}/all_quality_reports.pdf"
    conda:
        "../envs/r.yaml"
    log:
        stdout = "logs/06_binning_qc/checkm2/samples/{sample}/plot_reports.stdout",
        stderr = "logs/06_binning_qc/checkm2/samples/{sample}/plot_reports.stderr"
    benchmark:
        "benchmarks/06_binning_qc/checkm2/samples/{sample}/plot_reports.benchmark.txt"
    shell:
        """
        Rscript workflow/scripts/checkm2_assessment_plots.R \
            {input} {output} \
        > {log.stdout} 2> {log.stderr}
        """