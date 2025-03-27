# RVI TOOLBOX

This repository provides a set of workflows and modules which can be imported by multiple pipelines used by the [RVI project](https://www.sanger.ac.uk/group/respiratory-virus-and-microbiome-initiative/).

## PREREQUISITES
- Nextflow (≥22.04.0)
- iRODS client (`baton-do`)
- `Trimmomatic`, `TRF` and `sra-human-scrubber`

## IRODS WORKFLOW

The `combined_input.nf` and `irods.nf` provide workflows to fetch data from [IRODS](https://irods.org/).


## PREPROCESSING

The `PREPROCESSING.nf` workflow remove adapters (via `trimmomatic`), tandem repeats (via `TRF`) and remove human reads (via `sra-human-scrubber`) from fastq files.