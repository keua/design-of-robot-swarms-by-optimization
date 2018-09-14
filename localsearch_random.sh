#!/usr/bin/env bash

# run BT_agg
sh submit_localsearch.sh BT_agg_random 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation_bt.argos BT /home/jkuckling/AutoMoDe-LocalSearch/controller/BT/agg/BT-agg-random.txt
# run BT_for
sh submit_localsearch.sh BT_for_random 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging_bt.argos BT /home/jkuckling/AutoMoDe-LocalSearch/controller/BT/for/BT-for-random.txt
# run FSM_agg
sh submit_localsearch.sh FSM_agg_random 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation.argos FSM /home/jkuckling/AutoMoDe-LocalSearch/controller/FSM/agg/FSM-agg-random.txt
# run BT_for
sh submit_localsearch.sh FSM_for_random 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging.argos FSM /home/jkuckling/AutoMoDe-LocalSearch/controller/FSM/for/FSM-for-random.txt
