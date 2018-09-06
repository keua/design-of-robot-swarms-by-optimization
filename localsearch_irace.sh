#!/usr/bin/env bash

# run BT_agg
sh RunLocalSearch.sh BT_agg_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation_bt.argos BT /home/jkuckling/AutoMoDe-LocalSearch/controller/BT/agg-50k/BT-agg-50k.txt
# run BT_for
sh RunLocalSearch.sh BT_for_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging_bt.argos BT /home/jkuckling/AutoMoDe-LocalSearch/controller/BT/for-50k/BT-for-50k.txt
# run FSM_agg
sh RunLocalSearch.sh FSM_agg_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/aggregation.argos BT /home/jkuckling/AutoMoDe-LocalSearch/controller/FSM/agg-50k/FSM-agg-50k.txt
# run BT_for
sh RunLocalSearch.sh FSM_for_irace 10 ./config/config.ini /home/jkuckling/AutoMoDe-LocalSearch/experiments/vanilla/foraging.argos BT /home/jkuckling/AutoMoDe-LocalSearch/controller/FSM/for-50k/FSM-for-50k.txt
