SAMPLES = config['samples']

# download the database for CheckM2
rule checkm2_database:
    output:
        "results/06_binning_qc/checkm2/database/CheckM2_database/uniref100.KO.1.dmnd"
    conda:
        "../envs/checkm2.yaml"
    log:
        stdout = "logs/06_binning_qc/checkm2/checkm2.db.stdout",
        stderr = "logs/06_binning_qc/checkm2/checkm2.db.stderr"
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
        bins = "results/05_binning/{binner}/bins/{assembler}/{sample}", 
        diamond_database = "results/06_binning_qc/checkm2/database/CheckM2_database/uniref100.KO.1.dmnd"
    output:
        "results/06_binning_qc/checkm2/{binner}/{assembler}/{sample}/quality_report.tsv",
        out_dir = directory("results/06_binning_qc/checkm2/{binner}/{assembler}/{sample}")
    conda:
        "../envs/checkm2.yaml"
    log:
        stdout = "logs/06_binning_qc/checkm2/{binner}/{assembler}/{sample}.assessment.stdout",
        stderr = "logs/06_binning_qc/checkm2/{binner}/{assembler}/{sample}.assessment.stderr"
    params:
        binner = config['binning']['binner'],
        assembler = config['assembly']['assembler'],
        threads = config['checkm2']['threads']
    wildcard_constraints:
        sample="|".join(config['samples'])
    threads: 1
    shell:
        """
        echo {input.bins} \
        && \
        checkm2 predict --input {input.bins} --threads {params.threads} \
            -x .gz \
            --database_path {input.diamond_database} \
            --output-directory {output.out_dir} > {log.stdout} 2> {log.stderr}
        """

# this rule merges CheckM2 quality reports into a single table
rule checkm2_merge_results:
    input:
        expand("results/06_binning_qc/checkm2/{binner}/{assembler}/{sample}/quality_report.tsv",
               assembler = config['assembly']['assembler'],
               binner = config['binning']['binner'],
               sample = config['samples'])
    output:
        "results/06_binning_qc/checkm2/all_quality_reports.tsv"
    conda:
        "../envs/python.yaml"
    log:
        stdout = "logs/06_binning_qc/checkm2/merge_reports.stdout",
        stderr = "logs/06_binning_qc/checkm2/merge_reports.stderr"
    shell:
        """
        python workflow/scripts/merge_checkm2_reports.py \
            --input {input} \
            --output {output} \
        > {log.stdout} 2> {log.stderr}
        """

rule checkm2_plot_results:
    input:
        "results/06_binning_qc/checkm2/all_quality_reports.tsv"
    output:
        "results/06_binning_qc/checkm2/all_quality_reports.pdf"
    conda:
        "../envs/r.yaml"
    log:
        stdout = "logs/06_binning_qc/checkm2/plot_reports.stdout",
        stderr = "logs/06_binning_qc/checkm2/plot_reports.stderr"
    shell:
        """
        Rscript workflow/scripts/checkm2_assessment_plots.R \
            {input} {output} \
        > {log.stdout} 2> {log.stderr}
        """