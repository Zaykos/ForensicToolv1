import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Extract interesting files from an EWF disk image.')
    parser.add_argument('image', type=str, help='Path to the EWF disk image')
    parser.add_argument('output_dir', type=str, help='Path to the output directory')
    parser.add_argument('yaml_file', type=str, help='Path to the YAML file containing files to extract')
    return parser.parse_args()