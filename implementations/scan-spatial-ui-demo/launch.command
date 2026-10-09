#!/bin/zsh
cd "${0:A:h}"
if [ ! -d node_modules ]; then npm ci || exit 1; fi
open http://127.0.0.1:8813
node server.mjs
