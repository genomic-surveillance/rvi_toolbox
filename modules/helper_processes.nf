process COMPRESS_READS {
    tag "${meta.id}"
    label 'mem_4'
    label 'time_queue_from_small_slow2'

    publishDir "${params.results_dir}/${meta.id}/preprocessing/", mode: "copy"
    
    input:
    tuple val(meta), path(read_1), path(read_2)
    val(suffix)

    output:
    tuple val(meta), path("${meta.id}_1_${suffix}.fq.gz"), path("${meta.id}_2_${suffix}.fq.gz")

    script:
    """
    gzip -c ${read_1} > ${read_1}.tmp.gz
    gzip -c ${read_2} > ${read_2}.tmp.gz
    mv ${read_1}.tmp.gz ${meta.id}_1_${suffix}.fq.gz
    mv ${read_2}.tmp.gz ${meta.id}_2_${suffix}.fq.gz
    """
}