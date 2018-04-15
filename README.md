# 863-finalproj

To parse morphemes:

```python generate_morphemes.py -n names_short.txt -o morphemes.txt -l 3```

To generate names:

```python randname.py morphemes.txt```


TODO:

compress morphemes with only one next step
eg
DON	[blahblah...]
**DO	[N: 1]**
N 	[DON: 1, DO: 1]

should compress to
DON	[blahblah...]
N 	[DON: 1]