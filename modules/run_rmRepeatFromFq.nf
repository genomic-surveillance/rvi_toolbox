process run_rmRepeatFromFq {
    tag "${meta.id}"
    publishDir "${params.results_dir}/${meta.id}/preprocessing/", mode: "copy", pattern:"*.trf"

    input:
        tuple val(meta), path(fastq_1), path(fastq_2), path(trf_out_1), path(trf_out_2)

    output:
        tuple val(meta), path("${meta.id}_trf_1.fastq"), path("${meta.id}_trf_2.fastq"), emit: fastqs
        tuple path("combined.trf"), path("unpaired.trf"), emit: combined_trfs

    script:
    """
    ${projectDir}/rvi_toolbox/bin/trfCombine.py --trf1 ${trf_out_1} --trf2 ${trf_out_2} -o combined.trf -u unpaired.trf
    ${projectDir}/rvi_toolbox/bin/rmRepeatFromFq.py -i ${fastq_1} -t combined.trf -o ${meta.id}_trf_1.fastq
    ${projectDir}/rvi_toolbox/bin/rmRepeatFromFq.py -i ${fastq_2} -t combined.trf -o ${meta.id}_trf_2.fastq
    """
}