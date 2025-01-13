import pytest
import os
from rmRepeatFromFq import remove_repeats_from_fastq, read_file_n_lines

@pytest.fixture
def create_test_files(tmp_path):
    """
    Fixture to create temporary test files for input FASTQ, TRF output, and output FASTQ.
    """
    # Input FASTQ content
    input_fastq_content = (
        "@SEQ_ID_1\n"
        "ACGTACGTACGT\n"
        "+\n"
        "IIIIIIIIIIII\n"
        "@SEQ_ID_2\n"
        "TGCATGCATGCA\n"
        "+\n"
        "IIIIIIIIIIII\n"
        "@SEQ_ID_3\n"
        "GATCGATCGATC\n"
        "+\n"
        "IIIIIIIIIIII\n"
    )
    
    # TRF output content
    trf_output_content = (
        "@SEQ_ID_1\n"
        "@SEQ_ID_3\n"
    )
    
    # Paths to test files
    input_fastq = tmp_path / "input.fastq"
    trf_output = tmp_path / "trf_output.txt"
    output_fastq = tmp_path / "output.fastq"
    
    # Write test files
    input_fastq.write_text(input_fastq_content)
    trf_output.write_text(trf_output_content)
    
    return str(input_fastq), str(trf_output), str(output_fastq)

def test_remove_repeats_from_fastq(create_test_files):
    """
    Test the remove_repeats_from_fastq function with valid input.
    """
    input_fastq, trf_output, output_fastq = create_test_files
    
    # Call the function
    removed_count = remove_repeats_from_fastq(input_fastq, trf_output, output_fastq)
    
    # Check the number of removed sequences
    assert removed_count == 2, "Expected 2 sequences to be removed."
    
    # Check the output FASTQ content
    with open(output_fastq, "r") as f:
        output_content = f.read()
    
    expected_output = (
        "@SEQ_ID_2\n"
        "TGCATGCATGCA\n"
        "+\n"
        "IIIIIIIIIIII\n"
    )
    assert output_content == expected_output, "Output FASTQ file content does not match the expected content."

def test_empty_fastq_file(tmp_path):
    """
    Test with an empty FASTQ file.
    """
    input_fastq = tmp_path / "empty.fastq"
    trf_output = tmp_path / "trf_output.txt"
    output_fastq = tmp_path / "output.fastq"
    
    # Create empty FASTQ and TRF output files
    input_fastq.write_text("")
    trf_output.write_text("")
    
    # Call the function
    removed_count = remove_repeats_from_fastq(str(input_fastq), str(trf_output), str(output_fastq))
    
    # Check the number of removed sequences
    assert removed_count == 0, "Expected 0 sequences to be removed for an empty input."
    
    # Check the output FASTQ content
    with open(output_fastq, "r") as f:
        output_content = f.read()
    assert output_content == "", "Output FASTQ file should be empty."

def test_missing_trf_file(tmp_path):
    """
    Test with a missing TRF output file.
    """
    input_fastq = tmp_path / "input.fastq"
    output_fastq = tmp_path / "output.fastq"
    
    # Create a valid input FASTQ file
    input_fastq.write_text(
        "@SEQ_ID_1\n"
        "ACGTACGTACGT\n"
        "+\n"
        "IIIIIIIIIIII\n"
    )
    
    # Call the function and check for the expected exception
    with pytest.raises(FileNotFoundError):
        remove_repeats_from_fastq(str(input_fastq), "missing_trf.txt", str(output_fastq))

def test_missing_fastq_file(tmp_path):
    """
    Test with a missing input FASTQ file.
    """
    trf_output = tmp_path / "trf_output.txt"
    output_fastq = tmp_path / "output.fastq"
    
    # Create a valid TRF output file
    trf_output.write_text("@SEQ_ID_1\n")
    
    # Call the function and check for the expected exception
    with pytest.raises(FileNotFoundError):
        remove_repeats_from_fastq("missing_input.fastq", str(trf_output), str(output_fastq))

def test_read_file_n_lines():
    """
    Test the read_file_n_lines generator.
    """
    # Create a mock file content
    mock_file_content = (
        "Line 1\n"
        "Line 2\n"
        "Line 3\n"
        "Line 4\n"
        "Line 5\n"
        "Line 6\n"
    )
    mock_file = "mock_file.txt"
    
    # Write the mock content to a temporary file
    with open(mock_file, "w") as f:
        f.write(mock_file_content)
    
    # Read the file in batches of 2 lines
    expected_batches = [["Line 1\n", "Line 2\n"], ["Line 3\n", "Line 4\n"], ["Line 5\n", "Line 6\n"]]
    actual_batches = list(read_file_n_lines(mock_file, 2))
    
    # Clean up the temporary file
    os.remove(mock_file)
    
    assert actual_batches == expected_batches, "The read_file_n_lines function did not return the expected batches."

