#!/usr/bin/env bash

# run BT_agg
sh RunLocalSearch.sh BT_agg 10 ./config/minimal
# run BT_for
sh RunLocalSearch.sh BT_for 10 ./config/minimal/
# run FSM_agg
sh RunLocalSearch.sh FSM_agg 10 ./config/minimal/
# run BT_for
sh RunLocalSearch.sh FSM_for 10 ./config/minimal/
