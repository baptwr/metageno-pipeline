Ongoing implementation of several metagenomic tools into a single pipeline.

# Roadmap

## Quality control, preprocessing

| Tool   | Original year                                         | Conda available?                            | Link                                                      | Implemented? |
| :----- | :---------------------------------------------------- | :------------------------------------------ | :-------------------------------------------------------- | :----------- |
| fastp  | [2018](https://doi.org/10.1093/bioinformatics/bty560) | [Yes](https://anaconda.org/bioconda/fastp)  | https://github.com/OpenGene/fastp                         | Yes          |
| fastQC | 2010                                                  | [Yes](https://anaconda.org/bioconda/fastqc) | http://www.bioinformatics.babraham.ac.uk/projects/fastqc/ | Yes          |

### Human decontamination

| Tool    | Original year                              | Conda available?                             | Link                                   | Implemented? |
| :------ | :----------------------------------------- | :------------------------------------------- | :------------------------------------- | :----------- |
| bowtie2 | [2012](https://doi.org/10.1038/nmeth.1923) | [Yes](https://anaconda.org/bioconda/bowtie2) | https://github.com/BenLangmead/bowtie2 | Yes          |

Human assembly for mapping: 

* GRCh38. [Link](https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_000001405.40/)

## Asssembly

| Tool         | Original year                                                  | Conda available?                                | Link                                                          | Implemented? |
| :----------- | :------------------------------------------------------------- | :---------------------------------------------- | :------------------------------------------------------------ | :----------- |
| MEGAHIT      | [2015](https://doi.org/10.1093/bioinformatics/btv033)          | [Yes](https://anaconda.org/bioconda/megahit)    | https://github.com/voutcn/megahit                             | Yes          |
| (Meta)SPAdes | [2017](https://doi.org/10.1101/gr.213959.116)                  | [Yes](https://anaconda.org/bioconda/spades)     | https://github.com/ablab/spades                               | Yes          |
| IDBA-UD      | [2012](https://doi.org/10.1093/bioinformatics/bts174)          | [Yes](https://anaconda.org/bioconda/idba)       | https://github.com/loneknightpy/idba                          | No           |
| MetaVelvet   | [2012](https://doi.org/10.1093/nar/gks678)                     | [Yes](https://anaconda.org/bioconda/metavelvet) | https://github.com/hacchy/MetaVelvet                          | No           |
| MetaCompass  | [2024](https://arxiv.org/ftp/arxiv/papers/2403/2403.01578.pdf) | No                                              | https://gitlab.umiacs.umd.edu/mpop/metacompass (can't access) | No           |

## Assembly quality assessment

| Tool  | Original year                                         | Conda available?                           | Link                           | Implemented? |
| :---- | :---------------------------------------------------- | :----------------------------------------- | :----------------------------- | :----------- |
| QUAST | [2013](https://doi.org/10.1093/bioinformatics/btt086) | [Yes](https://anaconda.org/bioconda/quast) | https://github.com/ablab/quast | Yes          |

## Binning

| Tool      | Original year                                          | Conda available?                              | Link                                                  | Implemented? |
|:--------- |:------------------------------------------------------ |:--------------------------------------------- |:----------------------------------------------------- |:------------ |
| MetaBAT 2 | [2019](https://doi.org/10.7717%2Fpeerj.7359)           | [Yes](https://anaconda.org/bioconda/metabat2) | https://bitbucket.org/berkeleylab/metabat/src/master/ | Yes          |
| SemiBin2  | [2023](https://doi.org/10.1093/bioinformatics/btad209) | [Yes](https://anaconda.org/bioconda/semibin)  | https://github.com/BigDataBiology/SemiBin             | Yes          |
| VAMB      | [2019](https://doi.org/10.1038/s41587-020-00777-4)     | [Yes](https://anaconda.org/bioconda/vamb)     | https://github.com/RasmussenLab/vamb                  | Yes          |
| COMEBin   | [2024](https://doi.org/10.1038/s41467-023-44290-z)     | [Yes](https://anaconda.org/bioconda/comebin)  | https://github.com/ziyewang/COMEBin                   | No           |

## Bins quality assessment

| Tool    | Original year                                      | Conda available?                             | Link                                 | Implemented? |
| :------ | :------------------------------------------------- | :------------------------------------------- | :----------------------------------- | :----------- |
| CheckM2 | [2023](https://doi.org/10.1038/s41592-023-01940-w) | [Yes](https://anaconda.org/bioconda/checkm2) | https://github.com/chklovski/CheckM2 | Yes          |

## Bins refinement

| Tool    | Original year                                     | Conda available?                             | Link                                        | Implemented? |
|:------- |:------------------------------------------------- |:-------------------------------------------- |:------------------------------------------- |:------------ |
| Binette | [2024](https://doi.org/10.1101/2024.04.20.585171) | [Yes](https://anaconda.org/bioconda/binette) | https://github.com/genotoul-bioinfo/Binette | Yes           |

## Bins post-processing(gene prediction, functional annotation and taxonomy classification)

### Taxonomic annotation

| Tool    | Original year                                          | Conda available?                            | Link                                  | Implemented? |
|:------- |:------------------------------------------------------ |:------------------------------------------- |:------------------------------------- |:------------ |
| GTDB-Tk | [2022](https://doi.org/10.1093/bioinformatics/btac672) | [Yes](https://anaconda.org/bioconda/gtdbtk) | https://github.com/Ecogenomics/GTDBTk | Yes          |

### Dereplication

| Tool | Original year                                  | Conda available?                          | Link                          | Implemented? |
|:---- |:---------------------------------------------- |:----------------------------------------- |:----------------------------- |:------------ |
| dRep | [2017](https://doi.org/10.1038/ismej.2017.126) | [Yes](https://anaconda.org/bioconda/drep) | https://github.com/MrOlm/drep | Yes          |

## Taxonomic profiling

| Tool      | Original year                                      | Conda available?                               | Link                                   | Implemented? |
|:--------- |:-------------------------------------------------- |:---------------------------------------------- |:-------------------------------------- |:------------ |
| MetaPhlAn | [2023](https://doi.org/10.1038/s41587-023-01688-w) | [Yes](https://anaconda.org/bioconda/metaphlan) | https://github.com/biobakery/MetaPhlAn | Yes          |

## Strains profiling

| Tool     | Original year                                          | Conda available?                              | Link                                    | Implemented?      |
|:-------- |:------------------------------------------------------ |:--------------------------------------------- |:--------------------------------------- |:----------------- |
| inStrain | [2021](https://doi.org/10.1038/s41587-020-00797-0)     | [Yes](https://anaconda.org/bioconda/instrain) | https://github.com/MrOlm/inStrain       | Yes (for SR only) |
| Floria   | [2024](https://doi.org/10.1093/bioinformatics/btae252) | [Yes](https://anaconda.org/bioconda/floria)   | https://github.com/bluenote-1577/floria | Yes (for SR only) |

## More scripts

You can find in [`workflow/scripts/other_scripts`](workflow/scripts/other_scripts/) scripts made for processing some results produced by this pipeline.

`skani_analysis.py` performs bins pairwise comparison using Skani (https://doi.org/10.1038/s41592-023-02018-3). It can also produce a Venn diagram for results derived from dereplicated bins.

```
usage: skani_analysis.py [-h] --bins {refined,dereplicated} --tmp TMP --output_file OUTPUT_FILE --tsv_output TSV_OUTPUT --ani_threshold ANI_THRESHOLD --json_output JSON_OUTPUT --venn_diagram VENN_DIAGRAM --cpu CPU

Perform Skani analysis on bins.

options:
  -h, --help            show this help message and exit
  --bins {refined,dereplicated}
                        Type of bins to analyze
  --tmp TMP             Temporary directory for intermediate files
  --output_file OUTPUT_FILE
                        File to save the output results (Skani matrix)
  --tsv_output TSV_OUTPUT
                        File to save the Skani matrix in TSV format
  --ani_threshold ANI_THRESHOLD
                        Minimal ANI to consider two bins as the same
  --json_output JSON_OUTPUT
                        File to save the bins similarity results according to assembly methods (JSON)
  --venn_diagram VENN_DIAGRAM
                        Where to save the Venn diagram
  --cpu CPU             Number of CPU cores to use
```
