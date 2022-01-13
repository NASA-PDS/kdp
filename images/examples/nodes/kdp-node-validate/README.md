# pds-validate 

This node contains the [PDS Validate](https://nasa-pds.github.io/validate/) tool. Use it as the base container for your own PDS validation use cases.

To include custom Local Data Dictionaries (LDDs), you will need to use this image as the base of your image then do:

```
FROM kdp-node-validate:latest

# Add LDDs (validate takes JSON LDDs)
ADD ./path/to/ldds/*.JSON /usr/opt/ldds 
```

# Environment

| Variable         | Description                   |
|------------------|-------------------------------|
| `VALIDATE_BIN`   | Path to the PDS validate bin. Use `VALIDATE_BIN/validate` for the binary. |
| `VALIDATE_LDDS`  | Path to the PDS local data dictionaries. Value: `/usr/opt/ldds`|

# More docs TODO