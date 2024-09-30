# Fetch Manifest Resources

Given a valid hardening manifest:

## Hardening Manifest Build

Within [utils/get_sha256sum.sh](./utils/get_shasum256.sh)

```yaml
resources:
- filename: "v0.13.1.tar.gz"
  url: "https://github.com/defenseunicorns/leapfrogai/archive/refs/tags/v0.13.1.tar.gz"
  validation:
    type: sha256
    value: "FILL ME PLEASE"
- filename: "andale32.exe"
  url: "https://downloads.sourceforge.net/corefonts/andale32.exe"
  validation:
    type: sha256
    value: "SOME WRONG SHA256SUM"
```

This tool parses the hardening_manifest.yaml and for each URL in `resources` and attempts to:

- Download the resource defined at the `url` as named file `filename`
- Grabs the sha256sum of the downloaded resource
- Injects the sha256sum into the `validation.value` field
- Removes the downloaded resource

### Usage

1. `chmod +x ./utils/get_sha256sum.sh`
2. `./utils/get_sha256sum.sh ../path/to/hardening_manifest.yaml`

### Testing

1. `make test`

## Hardening Manifest Fetch

Within [fetch.py](./fetch.py)

```yaml
resources:
  # Example https resource
  - url: "https://s3.amazonaws.com/ops-manager-kubernetes-build/releases/mongodb-enterprise-operator-binaries-release-1.4.2.tar.gz"
    filename: "mongodb-files1.tar.gz" # [required field] desired staging name for the build context
    validation:
      type: "sha256" # supported: sha256, sha512
      value: "3d6b4cfca92067edd5c860c212ff5153d1e162b8791408bc671900309eb555ec" # must be lowercase
```

This tool parses the hardening_manifest.yaml and for each URL in `resources` and attempts to:

- Validate the `url`
- Fetch the `url` with retries and support for large file streaming
- Rename the file to `filename` and store in the same directory as `hardening_manifest.yaml`
- Validates the checksum `value`

### Usage

1. `make build`
2. `docker run --rm -v ${DIRECTORY}:/work -it fetch-resources:latest` where `DIRECTORY` is the local directory where your hardening_manifest.yaml lives.

### Testing

1. `make test`
