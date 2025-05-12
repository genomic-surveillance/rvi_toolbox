process SRA_HUMAN_SCRUBBER {
    tag "${meta.id}"
    label "sra_human_scrubber"
    publishDir "${params.results_dir}/${meta.id}/preprocessing/", mode: "copy"

    container "quay.io/gsu-pipelines/rvi-pp-sra-human-scrubber:v1.0"
    input:
        tuple val(meta), path(fastq_1), path(fastq_2)

    output:
        tuple val(meta), path("${meta.id}_1_clean.fastq"), path("${meta.id}_2_clean.fastq")

    script:
    // TODO check scrubber parameters to add
    """
    n=0
    for fastq in ${fastq_1} ${fastq_2} ; do
      n=\$(( \${n} + 1 ))
      if [[ "\${fastq}" == *.gz ]] ; then 
        fq=\${fastq%.gz}
        gzip -cd \${fastq} > \${fq}
      else
        fq=\${fastq}
      fi
      scrub.sh -i \${fq} -o ${meta.id}_\${n}_clean.fastq
    done
    """
}