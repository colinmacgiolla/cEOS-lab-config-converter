# cEOS-lab Configuration Converter
A simple script to either strip or adjust "real" device configs to something that can reliably run on cEOS.

## How to use
`cEOS-lab_convert.py` accepts two arguments, an input directory (`-i` / `--input`) and an output directory (`-o` / `-output`). Any file in the input directory will be parsed, adjusted, and a file with the same name will be written to the output directory.

By default we assume an `input` and an `output` directory.