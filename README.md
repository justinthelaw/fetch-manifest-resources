# fetch-manifest-resources
Parses the IB hardening_manifest.yaml and for each URL in `resources` attempts to:
- Validate the `url`
- Fetch the `url` with retries and support for large file streaming
- Rename the file to `filename` and store in the same directory as `hardening_manifest.yaml`
- Validates the `checksum`

## Usage
```python
pip3 install -r requirements.txt
fetch.py --hm-path <local-path-to>/hardening_manifest.yaml
```