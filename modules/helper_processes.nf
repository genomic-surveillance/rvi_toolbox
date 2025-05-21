process COMPRESS_READS {
    tag "${meta.id}"
    label 'mem_4'
    label 'time_queue_from_small_slow2'

    publishDir "${params.results_dir}/${meta.id}/preprocessing/", mode: "copy"
    
    input:
    tuple val(meta), path(read_1), path(read_2)

    output:
    tuple val(meta), path(read_1_gz), path(read_2_gz)

    script:
    read_1_gz = "${read_1}.gz"
    read_2_gz = "${read_2}.gz"
    """
    gzip -c ${read_1} > ${read_1}.tmp.gz
    gzip -c ${read_2} > ${read_2}.tmp.gz
    mv ${read_1}.tmp.gz ${read_1_gz}
    mv ${read_2}.tmp.gz ${read_2_gz}
    """