#pwd
cd ..

PYTHON_PACKAGES=("python3.7" "python3.8" "python3.9" "python3.10" "python3.11" "python3.12" "python3.13" "python3.14")

for p in "${PYTHON_PACKAGES[@]}"; do
  if ! "$p" -V &> /dev/null
  then
    continue
  fi

  version=$("$p" -V)
  echo "========================= $version ========================="
  "$p" -m tests.t_format

done
