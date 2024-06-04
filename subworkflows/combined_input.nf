//include { IRODS_MANIFEST_PARSE } from './irods_manifest_parse.nf'
//include { INPUT_CHECK } from './input_check.nf'

//
// SUBWORKFLOW: Read in study, run, etc. parameters and pull data from iRODS
//

//
// Check input samplesheet and get read channels
//

// --- SAMPLESHEET ---
// Function to get list of [ meta, fastq_1, fastq_2 ]
def create_fastq_channels(LinkedHashMap row) {
    def meta = [:]
    meta.ID = row.ID

    def array = []
    // check short reads
    if ( !(row.R1 == 'NA') ) {
        if ( !file(row.R1).exists() ) {
            exit 1, "ERROR: Please check input samplesheet -> Read 1 FastQ file does not exist!\n${row.R1}"
        }
        fastq_1 = file(row.R1)
    } else { fastq_1 = 'NA' }
    if ( !(row.R2 == 'NA') ) {
        if ( !file(row.R2).exists() ) {
            exit 1, "ERROR: Please check input samplesheet -> Read 2 FastQ file does not exist!\n${row.R2}"
        }
        fastq_2 = file(row.R2)
    } else { fastq_2 = 'NA' }
    array = [ meta, fastq_1, fastq_2 ]
    return array
}

workflow INPUT_CHECK {
    take:
    samplesheet // file: /path/to/samplesheet.csv

    main:
    Channel
        .fromPath( samplesheet )
        .ifEmpty {exit 1, "Cannot find path file ${samplesheet}"}
        .splitCsv ( header:true, sep:',' )
        .map { create_fastq_channels(it) }
        // shoudn't the map operation bellow be redundant?
        .map { meta, reads_1, reads_2 -> [ meta, fastq_1, fastq_2 ] }
        .filter{ meta, reads_1, reads_2 -> reads_1 != 'NA' || reads_2 != 'NA' }  // Single end not supported
        .set { shortreads }

    emit:
    shortreads // channel: [ val(meta), file(reads_1), file(reads_2) ]
}

// --- IRODS_MANIFEST ---

//
// Check input manifest and assign idenifier channels
// Expected to be used as submodule to input data to IRODS extractor
//

workflow IRODS_MANIFEST_PARSE {

    take:
    lane_manifest // file: /path/to/manifest_of_lanes.csv

    main:
    Channel
        .fromPath( lane_manifest )
        .ifEmpty {exit 1, "File is empty / Cannot find file at ${lane_manifest}"}
        .splitCsv ( header:true, strip:true, sep:',' )
        .map { create_channel(it) }
        .set { meta }

    emit:
    meta
}

def create_channel(LinkedHashMap row) {
    def meta = [:]
    meta.studyid = ((! row.studyid) || ("${row.studyid}" == "")) ? -1 : "${row.studyid}".toInteger()
    meta.runid = ((! row.runid) || ("${row.runid}" == "")) ? -1 : "${row.runid}".toInteger()
    meta.laneid = ((! row.laneid) || ("${row.laneid}" == "")) ? -1 : "${row.laneid}".toInteger()
    meta.plexid = ((! row.plexid) || ("${row.plexid}" == "")) ? -1 : "${row.plexid}".toInteger()
    if (((meta.studyid == -1) && (meta.runid == -1)) && ((meta.laneid != -1) || (meta.plexid != -1))) {
        log.warn ("Cannot submit an iRODS query based on laneid or plexid metadata tags where neither studyid or runid are specified, as this query would catch too many file objects.\nThe row ${row} in the input manifest is ignored")
        return "none"
    }
    def extraFields = row.keySet().minus(['studyid', 'runid', 'laneid', 'plexid', 'target', 'type'])
    extraFields.each { key ->
        if ("${row[key]}" != "") {
            meta[key] = "${row[key]}"
        }
    }
    if ((meta.studyid != -1) || (meta.runid != -1) || (extraFields.any { "${row[it]}" != "" })) {
        meta.target = ((! row.target) || ("${row.target}" == "")) ? "1" : "${row.target}"
        meta.type = ((! row.type) || ("${row.type}" == "")) ? "cram" : "${row.type}"
    }
    else if ((row.target && ("${row.target}" != "")) || (row.type && (row.type != ""))) {
        log.warn ("Cannot submit an iRODS query solely based on target or type metadata tags, as this query would catch too many file objects.\nThe row ${row} in the input manifest is ignored")
        return "none"
    }
    return meta
}

// --- Pulling from irods


workflow IRODS_CLI {
    main:
    param_input = Channel.of(["${params.studyid}", "${params.runid}", "${params.laneid}", "${params.plexid}", "${params.target}", "${params.type}"])
    
    param_input.map{ studyid, runid, laneid, plexid, target, type ->
        if (studyid > 0 || runid > 0) {
            meta = [:]
            if (studyid > 0) {meta.studyid = studyid}
            if (runid > 0) {meta.runid = runid}
            if (laneid > 0 ) {meta.laneid = laneid}
            if (plexid > 0 ) {meta.plexid = plexid}
            meta.target = target
            meta.type = type
            return meta
        } else {
            if ((laneid > 0) || (plexid > 0)) {
                log.warn ("Cannot submit an iRODS query where neither studyid or runid are specified, as this query would catch too many file objects.\nThe requested input as specified through the CLI options '--studyid ${studyid}, --runid ${runid}, --laneid ${laneid}, --plexid ${plexid}, --target ${target}, --type ${type}' is ignored")
                }
            return "none"
        }
    }.set{ input_irods_from_opt_ch } 

    emit:
    input_irods_from_opt_ch
}

// workflow COMBINE_IRODS 
workflow PARSE_IRODS_INPUT {
    main:
    // take iRODS dataset specification from CLI options
    IRODS_CLI()
    | set{ input_irods_from_opt_ch }

    // take iRODS dataset specification from manifest of lanes
    if (params.manifest_of_lanes) {
        IRODS_MANIFEST_PARSE(params.manifest_of_lanes)
        | set{ input_irods_from_man_ch }
    } else {
        Channel.of("none").set{ input_irods_from_man_ch}
    }

    // combine iRODS specs input channels
    input_irods_from_opt_ch.mix(input_irods_from_man_ch)
    | filter{ it != "none"}
    | set{ input_irods_ch }

    emit:
    input_irods_ch
}

workflow COMBINE_READS {
    take:
    irods_reads_ch // [meta, read_1, read_2] as from IRODS_EXTRACTOR

    main:
    // Read in samplesheet, validate and stage input files
    if (params.manifest_of_reads) {
        input_reads_ch = file(params.manifest_of_reads)
        INPUT_CHECK (input_reads_ch)
        | set{ ch_reads_from_manifest }
    } else {
        Channel.of("none").set{ ch_reads_from_manifest }
    }  // ch_reads_from_manifest [meta, read_1, read_2]

    // combine reads input channels
    irods_reads_ch.mix(ch_reads_from_manifest.filter{ it != "none"}).set{ all_reads_ready_to_map_ch }

    emit:
    all_reads_ready_to_map_ch  // [meta, read_1, read_2]

}
