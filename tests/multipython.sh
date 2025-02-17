#pwd
cd ..

mapfile -t PYTHON_PACKAGES < <(ls -v /usr/bin/python3.* | grep '.*\(.[0-9]\+\)$')

for p in "${PYTHON_PACKAGES[@]}"; do
  if ! "$p" -V &> /dev/null
  then
    continue
  fi

  version=$("$p" -V)
  echo "========================= $version ========================="
  "$p" -m tests.t_format

done
