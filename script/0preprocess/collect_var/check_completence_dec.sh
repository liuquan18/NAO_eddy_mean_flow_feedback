#!/usr/bin/env bash

BASE_DIR=$1
var=$2
missing=0

# Check subfolders
for i in {1..50}; do
  dir="r${i}i1p1f1"
  if [ ! -d "${BASE_DIR}/${dir}" ]; then
    echo "Missing subfolder: ${dir}"
    missing=1
    continue
  fi

  # Check for files for each decade from 1850 to 2090
  missing_years=()
  for year in $(seq 1850 10 2090); do
    if ! ls "${BASE_DIR}/${dir}"/*${year}*.nc 1>/dev/null 2>&1; then
      missing_years+=("$year")
    fi
  done

  if [ "${#missing_years[@]}" -ne 0 ]; then
    echo "Folder ${BASE_DIR}/${dir} is missing files for years: ${missing_years[*]}"
    missing=1
  fi
done

if [ $missing -eq 0 ]; then
  echo "All files are present."
else
  echo "Some files are missing."
fi