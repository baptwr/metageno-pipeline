#!/usr/bin/env bash 

# retrieving the reads from the ENA
RUN=ERR1855257
RUN2=ERR1855263

wget -nc ftp://ftp.sra.ebi.ac.uk/vol1/fastq/ERR185/007/${RUN}/${RUN}_1.fastq.gz
wget -nc ftp://ftp.sra.ebi.ac.uk/vol1/fastq/ERR185/007/${RUN}/${RUN}_2.fastq.gz

wget -nc ftp://ftp.sra.ebi.ac.uk/vol1/fastq/ERR185/003/${RUN2}/${RUN2}_1.fastq.gz
wget -nc ftp://ftp.sra.ebi.ac.uk/vol1/fastq/ERR185/003/${RUN2}/${RUN2}_2.fastq.gz

# sampling the sequences to reduce the size
seqkit sample -p 0.8 --rand-seed 202400 ${RUN}_1.fastq.gz \
    | gzip -c > ${RUN}_1_subsampled.fastq.gz
seqkit sample -p 0.8 --rand-seed 202400 ${RUN}_2.fastq.gz \
    | gzip -c > ${RUN}_2_subsampled.fastq.gz

seqkit sample -p 0.8 --rand-seed 202400 ${RUN2}_1.fastq.gz \
    | gzip -c > ${RUN2}_1_subsampled.fastq.gz
seqkit sample -p 0.8 --rand-seed 202400 ${RUN2}_2.fastq.gz \
    | gzip -c > ${RUN2}_2_subsampled.fastq.gz

# removing original .fastq.gz
rm ${RUN}_1.fastq.gz ${RUN}_2.fastq.gz
rm ${RUN2}_1.fastq.gz ${RUN2}_2.fastq.gz

# moving the reads in the data folder
mkdir -p data
mv *_subsampled.fastq.gz data/

# renaming them as original .fastq.gz
mv data/${RUN}_1_subsampled.fastq.gz data/${RUN}_1.fastq.gz
mv data/${RUN}_2_subsampled.fastq.gz data/${RUN}_2.fastq.gz

mv data/${RUN2}_1_subsampled.fastq.gz data/${RUN2}_1.fastq.gz
mv data/${RUN2}_2_subsampled.fastq.gz data/${RUN2}_2.fastq.gz