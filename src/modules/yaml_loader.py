import yaml


def load_yaml(yaml_file):
    with open(yaml_file) as file:
        files = yaml.load(file, Loader=yaml.FullLoader)
        targets = set()

        for target in files["Targets"]:
            path = target["Path"]
            file_mask = target["FileMask"]
            target_path = path + file_mask
            target_path = target_path.replace("C:", "")
            target_path = target_path.replace("\\", "/")
            target_path = target_path.rstrip("/")
            targets.add(target_path.strip())
        return targets
    