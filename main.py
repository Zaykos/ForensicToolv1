from modules.ewf_extractor import EwfExtractor
from modules.yaml_loader import load_yaml
from modules.arg_parser import parse_args


def main():
    args = parse_args()

    files_to_extract = load_yaml(args.yaml_file)

    extractor = EwfExtractor(args.image, args.output_dir, files_to_extract)
    extractor.open()
    extractor.extract_files()
    extractor.close()


if __name__ == "__main__":
    main()