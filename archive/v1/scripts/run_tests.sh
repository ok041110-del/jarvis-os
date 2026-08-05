#!/usr/bin/env bash
set -e
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$ROOT/packages/core/src:$ROOT/packages/shared/src:$ROOT/adapters/policy-inmemory/src:$ROOT/adapters/connector-mock/src:$ROOT/apps/poc-runner/src:$ROOT"
python3 -m unittest tests.e2e.test_walking_skeleton -v
