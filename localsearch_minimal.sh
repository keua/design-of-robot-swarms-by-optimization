#!/usr/bin/env bash

# run BT_agg
sh submit_localsearch.sh BT_agg_minimal 1 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation_bt.argos BT
# run BT_for
# sh submit_localsearch.sh BT_for_minimal 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging_bt.argos BT
# run FSM_agg
# sh submit_localsearch.sh FSM_agg_minimal 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation.argos BT
# run BT_for
# sh submit_localsearch.sh FSM_for_minimal 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging.argos BT
