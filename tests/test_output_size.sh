#/bin/bash

# Maximum size in KB
MAXSIZE=100000000
DEFAULT_OUTPUT_LOC=test_output

if [ "$#" -eq 1 ]; then
  OUTPUT_LOC=$1
else
  OUTPUT_LOC=$DEFAULT_OUTPUT_LOC
fi

SIZE=`du -d0 data | awk '{print $1}'`

if [ $? -ne 0 ]; then
  echo "ERROR: Could not check size of output files against size limit."
  exit 1
fi

if [ $SIZE -gt $MAXSIZE ]; then
  echo "FAILED: Size of output data ($SIZE) exceeds maximum allowed size ($MAXSIZE)."
  exit 1
fi

echo "SUCCESS: Size of output data is $SIZE, which is <= maximum size ($MAXSIZE)"
exit 0
