import pytest
import os

from fastq2fasta import fastq_to_fasta

@pytest.fixture
def create_temp_fastq_file(tmp_path):
    """Fixture to create a temporary FASTQ file for testing."""
    fastq_content = (
        "@SEQ_ID_1\n"
        "GATTTGGGGTTTAAAGGGTTT\n"
        "+\n"
        "IIIIIIIIIIIIIIIIIIII\n"
        "@SEQ_ID_2\n"
        "GATTTGGGGTTTAAAGGGTTT\n"
        "+\n"
        "IIIIIIIIIIIIIIIIIIII\n"
    )
    fastq_file = tmp_path / "test.fastq"
    fastq_file.write_text(fastq_content)
    return str(fastq_file)

def test_successful_conversion(create_temp_fastq_file, tmp_path):
    """Test successful conversion from FASTQ to FASTA."""
    fasta_file = tmp_path / "output.fasta"
    result = fastq_to_fasta(create_temp_fastq_file, str(fasta_file))
    
    assert result is True
    assert fasta_file.exists()
    
    # Check the content of the output FASTA file
    expected_fasta_content = (
        ">SEQ_ID_1\n"
        "GATTTGGGGTTTAAAGGGTTT\n"
        ">SEQ_ID_2\n"
        "GATTTGGGGTTTAAAGGGTTT\n"
    )
    assert fasta_file.read_text() == expected_fasta_content

def test_conversion_to_stdout(create_temp_fastq_file, capsys):
    """Test conversion from FASTQ to FASTA with output to stdout."""
    result = fastq_to_fasta(create_temp_fastq_file)
    
    assert result is True
    
    # Capture the output
    captured = capsys.readouterr()
    expected_stdout = (
        ">SEQ_ID_1\n"
        "GATTTGGGGTTTAAAGGGTTT\n"
        ">SEQ_ID_2\n"
        "GATTTGGGGTTTAAAGGGTTT\n"
    )
    assert captured.out == expected_stdout

def test_invalid_fastq_format(tmp_path):
    """Test handling of an invalid FASTQ format."""
    invalid_fastq_file = tmp_path / "invalid.fastq"
    invalid_content = (
        "SEQ_ID_1\n"  # Missing '@'
        "GATTTGGGGTTTAAAGGGTTT\n"
        "+\n"
        "IIIIIIIIIIIIIIIIIIII\n"
    )
    invalid_fastq_file.write_text(invalid_content)
    
    result = fastq_to_fasta(str(invalid_fastq_file))
    
    assert result is False

def test_file_not_found():
    """Test handling of a file not found error."""
    result = fastq_to_fasta("non_existent_file.fastq")
    
    assert result is False

if __name__ == "__main__":
    pytest.main()
