#!/usr/bin/env bash

# run BT_agg
sh submit_localsearch.sh BT_agg_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation_bt.argos BT /home/jkuckling/AutoMoDe-LocalSearch/controller/BT/agg-50k/BT-agg-50k.txt
# run BT_for
#sh submit_localsearch.sh BT_for_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging_bt.argos BT /home/jkuckling/AutoMoDe-LocalSearch/controller/BT/for-50k/BT-for-50k.txt
# run FSM_agg
sh submit_localsearch.sh FSM_agg_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation.argos FSM /home/jkuckling/AutoMoDe-LocalSearch/controller/FSM/agg-50k/FSM-agg-50k.txt
# run BT_for
#sh submit_localsearch.sh FSM_for_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging.argos FSM /home/jkuckling/AutoMoDe-LocalSearch/controller/FSM/for-50k/FSM-for-50k.txt
