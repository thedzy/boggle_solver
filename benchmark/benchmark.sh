#!/usr/bin/env zsh

################################################################################
# benchmark.sh
# Author: Shane Young
# Date: 2025-11-27
# Revision:	1.0
# Platform: MacOS
#
# Description
#
#
# Versions
# 1.	Features
#
################################################################################
# Exit Codes
#
################################################################################

################################################################################
# Environment setup
################################################################################

script=${1:-../boggle_solver.py}
loops=${2:-64}
iterations=${3:-10}

threaded=false

################################################################################
# Functions
################################################################################


function do_run() {
    local size=$1
    local iterations=$2

    time=0.0
    word_counts=0.0
    word_lookups=0.0
    for _ in $(/usr/bin/seq 1 $iterations); do
        result=$(python3 "$script" -s $size --json 2>/dev/null)
        run=$(echo "$result" | jq '.stats.total_time')
        word_lookup=$(echo "$result" | jq '.stats.word_lookups')
        word_count=$(echo "$result" | jq '.stats.word_count')
        ((time += run))
        ((word_lookups += word_lookup))
        ((word_counts += word_count))
    done
    echo "${size}\t$((time / iterations))\t$((word_lookups / iterations))\t$((word_counts / iterations))"
}

################################################################################
# Main
################################################################################

echo "Size\tTime\tLookups\tWords"
for size in $(/usr/bin/seq 2 $loops); do
    if $threaded; then
        do_run $size $iterations &
    else
        do_run $size $iterations
    fi
done

wait

exit 0
