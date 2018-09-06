#!/usr/bin/env bash

# run BT_agg
sh RunLocalSearch.sh BT_agg_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation_bt.argos BT
# run BT_for
sh RunLocalSearch.sh BT_for_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging_bt.argos BT
# run FSM_agg
sh RunLocalSearch.sh FSM_agg_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation.argos BT
# run BT_for
sh RunLocalSearch.sh FSM_for_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging.argos BT
