#!/usr/bin/env bash

set -u

script_path=${BASH_SOURCE[0]}
case "$script_path" in
  */*) script_directory=${script_path%/*} ;;
  *) script_directory=. ;;
esac
repository_root=$(cd -P -- "$script_directory/.." && pwd) || exit 1

exec python3 -B "$repository_root/scripts/lib/install_ai_workflow.py" "$@"
