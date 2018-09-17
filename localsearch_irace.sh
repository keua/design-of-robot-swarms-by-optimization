#!/usr/bin/env bash

# run BT_agg
sh submit_localsearch.sh BT_agg_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation_bt.argos BT /home/jkuckling/AutoMoDe-LocalSearch/controller/BT/agg/BT-agg-25k.txt
# run BT_for
sh submit_localsearch.sh BT_for_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging_bt.argos BT /home/jkuckling/AutoMoDe-LocalSearch/controller/BT/for/BT-for-25k.txt
# run FSM_agg
sh submit_localsearch.sh FSM_agg_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation.argos FSM /home/jkuckling/AutoMoDe-LocalSearch/controller/FSM/agg/FSM-agg-25k.txt
# run BT_for
sh submit_localsearch.sh FSM_for_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging.argos FSM /home/jkuckling/AutoMoDe-LocalSearch/controller/FSM/for/FSM-for-25k.txt
