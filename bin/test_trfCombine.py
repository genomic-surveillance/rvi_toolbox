import pytest
import os

from trfCombine import generate_combined_trf

@pytest.fixture
def create_temp_trf_files(tmp_path):
    """Fixture to create temporary TRF files for testing."""
    trf1_content = (
        "@SEQ_ID_1/1\n"
        "1 76 1 76.0 1 100 0 152 0 0 0 100 0.00 T TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT . .\n"
        "@SEQ_ID_2/1\n"
        "1 75 1 75.0 1 100 0 150 100 0 0 0 0.00 A AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA . .\n"
        "@SEQ_ID_4/1\n"
        "1 75 1 75.0 1 100 0 150 100 0 0 0 0.00 A AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA . .\n"

    )
    trf2_content = (
        "@SEQ_ID_1/2\n"
        "1 74 1 74.0 1 100 0 148 100 0 0 0 0.00 A AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA . .\n"
        "@SEQ_ID_2/2\n"
        "1 75 1 75.0 1 100 0 150 100 0 0 0 0.00 A AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA . .\n"
        "@SEQ_ID_3/2\n"
        "1 76 1 76.0 1 100 0 152 0 0 0 100 0.00 T TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT . .\n"
    )
    
    trf1_file = tmp_path / "trf1.trf"
    trf2_file = tmp_path / "trf2.trf"
    output_file = tmp_path / "combined.trf"
    unpaired_file = tmp_path / "unpaired.trf"
    
    trf1_file.write_text(trf1_content)
    trf2_file.write_text(trf2_content)
    
    return str(trf1_file), str(trf2_file), str(output_file), str(unpaired_file)

def test_successful_combination(create_temp_trf_files):
    """Test successful combination of two TRF files."""
    trf1, trf2, output, unpaired = create_temp_trf_files

    generate_combined_trf(trf1, trf2, output, unpaired)
    
    assert(os.path.exists(output))
    assert(os.path.exists(unpaired))
    
    # Check the content of the combined TRF file
    expected_combined_content = (
    "@SEQ_ID_1/1\n"
    "@SEQ_ID_1/2\n"
    "@SEQ_ID_2/1\n"
    "@SEQ_ID_2/2\n"
    "@SEQ_ID_3/2\n"
    "@SEQ_ID_3/1\n"
    "@SEQ_ID_4/1\n"
    "@SEQ_ID_4/2\n"
    )
    
    with open(output, 'r') as f:
        combined_content = f.read()

    assert combined_content == expected_combined_content



def test_unpaired_reads(create_temp_trf_files):
    """Test that unpaired reads are correctly identified and written to the unpaired file."""
    trf1, trf2, output, unpaired = create_temp_trf_files
    
    # Call the function to generate the combined and unpaired TRF files
    generate_combined_trf(trf1, trf2, output, unpaired)
    
    assert os.path.exists(output)
    assert os.path.exists(unpaired)
    
    # Check the content of the unpaired TRF file
    expected_unpaired_content = (
    "@SEQ_ID_1/2\n"
    "@SEQ_ID_2/2\n"
    "@SEQ_ID_3/1\n"
    "@SEQ_ID_4/2\n"
    )
    
    with open(unpaired, 'r') as f:
        unpaired_content = f.read()
    print(unpaired_content)
    assert unpaired_content == expected_unpaired_content

if __name__ == "__main__":
    pytest.main()