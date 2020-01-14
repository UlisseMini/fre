## Its free real estate

Store files safely in the cloud for free :)


## Examples

```sh
# fileinfo will contain a set of links to encrypted versions of file.txt
./main.py put file.txt > fileinfo.json

# now we retrieve file.txt, if one of our storage links goes down we'll use another.
./main.py get fileinfo.json
```
