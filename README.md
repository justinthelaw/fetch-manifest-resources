# fetch-manifest-resources
Given a valid hardening manifest:
```yaml
resources:
  # Example https resource
  - url: "https://s3.amazonaws.com/ops-manager-kubernetes-build/releases/mongodb-enterprise-operator-binaries-release-1.4.2.tar.gz"
    filename: "mongodb-files1.tar.gz" # [required field] desired staging name for the build context
    validation:
      type: "sha256" # supported: sha256, sha512
      value: "3d6b4cfca92067edd5c860c212ff5153d1e162b8791408bc671900309eb555ec" # must be lowercase
```
This tool parses the hardening_manifest.yaml and for each URL in `resources` attempts to:
- Validate the `url`
- Fetch the `url` with retries and support for large file streaming
- Rename the file to `filename` and store in the same directory as `hardening_manifest.yaml`
- Validates the checksum `value`

## Usage
```python
pip3 install -r requirements.txt
fetch.py --hm-path <local-path-to>/hardening_manifest.yaml
```