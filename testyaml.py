import yaml

with open("popeye.yaml") as stream:
    try:
        yaml1= yaml.load(stream)
        print(yaml1)
    except yaml.YAMLError as exc:
        print(exc)