#!/bin/bash
# Bash strict mode: http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail

rm out/ -rf

USER_ID="$(id -u "$USER")"
GROUP_ID="$(id -g "$USER")"
docker run -it --rm \
    -v "$(pwd)":/workspace/src \
    -u "$USER_ID":"$GROUP_ID" \
    "$(docker build -q --build-arg UID="$USER_ID" --build-arg GID="$GROUP_ID" . )" sh -c "
        cd src
        java -jar ../antlr.jar -Dlanguage=JavaScript -o out/frontend_parser -visitor -listener BaserowFormulaLexer.g4
        java -jar ../antlr.jar -Dlanguage=JavaScript -o out/frontend_parser -visitor -listener BaserowFormula.g4
        java -jar ../antlr.jar -Dlanguage=Python3 -o out/backend_parser -visitor -listener BaserowFormulaLexer.g4
        java -jar ../antlr.jar -Dlanguage=Python3 -o out/backend_parser -visitor -listener BaserowFormula.g4
    "

rm -f ./../web-frontend/modules/database/formula/parser/BaserowFormula*
cp out/frontend_parser/* ./../web-frontend/modules/database/formula/parser/

rm -f ./../backend/src/baserow/contrib/database/formula/parser/generated/BaserowFormula*
cp out/backend_parser/* ./../backend/src/baserow/contrib/database/formula/parser/generated/

cp out/backend_parser/*.tokens .

rm out/ -rf