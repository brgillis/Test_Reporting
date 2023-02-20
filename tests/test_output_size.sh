#/bin/bash

MAXSIZE=100000000
DEFAULT_OUTPUT_LOC=test_output

if [ "$#" -eq 1 ]; then
  OUTPUT_LOC=$1
else
  OUTPUT_LOC=$DEFAULT_OUTPUT_LOC
fi

SIZE=`du -d0 data | gawk '{print $1}'`

if [ $SIZE -gt $MAXSIZE ]; then
  echo "Size of output data ($SIZE) exceeds maximum allowed size ($MAXSIZE)."
  exit 1
fi

echo "Size of output data is $SIZE, which is <= maximum size ($MAXSIZE)"
exit 0
