#!/usr/bin/env bash


error() {
    echo "$@"
    exit 1
}

preconditions() {
    [[ -f scripts/runner.sh ]] || error "Run from off root"
}

_build() {
    docker build -q -t off:latest -f docker/app.Dockerfile .
}

_run() {
    docker run --rm -it -p $DEBUG_PORT_1:$DEBUG_PORT_1 -p $DEBUG_PORT_2:$DEBUG_PORT_2 -p $LISTENING_PORT:$LISTENING_PORT -v `pwd`:/off off:latest "$@"
}

shell() {
    _build && _run /bin/bash
}

start() {
    _build && _run python manage.py runserver 0.0.0.0:$LISTENING_PORT
}

main() {
    preconditions
    source scripts/constants
    local cmd="$1" ; shift || error "Missing command"
    
    $cmd "$@"
}

main "$@"