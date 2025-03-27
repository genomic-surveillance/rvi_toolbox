# RVI TOOLBOX

This repository provides a set of workflows and modules which can be imported by multiple pipelines used by the [RVI project](https://www.sanger.ac.uk/group/respiratory-virus-and-microbiome-initiative/).

## PREREQUISITES
- Nextflow (≥22.04.0)
- iRODS client (`baton-do`)
- `Trimmomatic`, `TRF` and `sra-human-scrubber`

## IRODS WORKFLOW

The `combined_input.nf` and `irods.nf` provide workflows to fetch data from [IRODS](https://irods.org/).

### COMBINED_INPUT.nf Workflow

The `combined_input.nf` workflow consolidates and validates input data from two sources:

    - Local Samplesheets: Validates FASTQ paths (via `INPUT_CHECK`).

    - iRODS Metadata: Fetches sequencing data from iRODS using study/run/lane IDs (via `IRODS_MANIFEST_PARSE` and `IRODS_CLI`).

### IRODS.nf Workflow

IRODS WORKFLOW

The irods.nf workflow fetches and processes sequencing data from iRODS, converting CRAMs to FASTQs while preserving metadata. It consists of two main sub-workflows:

1. `QUERY_IRODS_METADATA`

    Purpose: Queries iRODS for metadata (study, run, lane, etc.) using baton-do and parses JSON results.

    Key Steps:

    - Generates iRODS queries from input parameters (`studyid`, `runid`) or manifests.
    - Filters results (e.g., skips subsets like phix via params.irods_subset_to_skip).
    - Outputs tuples of (metadata, cram_path).

2. `CRAM_EXTRACT`

    Purpose: Retrieves CRAMs from iRODS, converts to FASTQs, and combines subsets (e.g., target + phix = total).

    Key Steps:

    - Skip Existing Files: Checks params.outdir for pre-existing FASTQs.

    - CRAM Conversion: Uses samtools collate (via `COLLATE_FASTQ`) to generate paired FASTQs.

    - Combine Subsets: Merges FASTQs from multiple subsets (e.g., target + phix) if `combine_same_id_crams=true`.

    - Cleanup: Removes intermediate files (`cleanup_intermediate_files_irods_extractor=true`).

## PREPROCESSING Workflow

The `PREPROCESSING.nf` workflow processes raw FASTQ files through a modular pipeline:

    - Trimmomatic: Removes adapters (configurable via `adapter_fasta` parameter).

    - Tandem Repeat Finder (`TRF`): Masks tandem repeats by converting FASTQ to FASTA, running `TRF`, and filtering repeats from the original reads.

    - Human Read Removal: Uses sra-human-scrubber to exclude human-derived sequences.

Each step is toggleable via parameters (`run_trimmomatic`, `run_trf`, `run_hrr`). Inputs are paired-end FASTQs (provided as channel of the following structure `tuples (meta, [read1, read2]`), and outputs are cleaned FASTQs in the same format. The workflow validates paths (e.g., adapter files) and warns if all modules are disabled.

To run the workflow in isolation, use the following command:

```{bash}
nextflow run PREPROCESSING.nf -c PREPROCESSING.config \
  --preprocessing_mnf samples.csv \
  --adapter_fasta adapters.fa \
  --run_trimmomatic true
```

> the csv (`preprocessing_mnf`) must have the following columns: `sample_id`,`reads_1`,`reads_2`.
