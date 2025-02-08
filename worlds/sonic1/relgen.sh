#! /bin/sh

cd tracker
zip ../sonic1.poptracker -r * -x images/raw/\*
cd ../..
zip sonic1/sonic1.apworld -r sonic1 -x \*/__pycache__/\* sonic1/archived/\* sonic1/tracker/images/raw/\* sonic1/sonic1.apworld sonic1/sonic1.poptracker sonic1/relgen.sh sonic1/.gitignore
