#!/bin/zsh
cd "${0:A:h}"
open http://127.0.0.1:8816
python3 -m http.server 8816 --bind 127.0.0.1 --directory dist
