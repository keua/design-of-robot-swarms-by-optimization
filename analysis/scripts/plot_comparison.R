library(ggplot2)

source(file="/home/jkuckling/AutoMoDe-LocalSearch/analysis/scripts/utilities.R")

load_data <- function(architecture, scenario, method) {
  folder_name <- paste(architecture, scenario, method, sep="_")
  data <- load_data_score_file(folder_name)
  data <- data[c("Simulation", "Pseudo.Reality")]
  return(data)
}

load_irace <- function(scenario) {
  load_irace_bt <- function() {
    bt_df <- load_data("BT", scenario, "irace")
    return(bt_df)
  }
  load_irace_fsm <- function() {
    fsm_df <- load_data("FSM", scenario, "irace")
    return(fsm_df)
  }

  bt_results <- load_irace_bt()
  fsm_results <- load_irace_fsm()
  results_df <- data.frame(bt_results, fsm_results)
  results_df <- setNames(results_df, c("Irace BT", "Irace FSM"))
  return(results_df)
}

load_evostick <- function(scenario) {
  load_irace_fsm <- function() {

  }
  exp_folder <- paste("evostick", scenario, "50k", sep="-")
  file <- paste(RESULT_FOLDER, "evostick_runs", exp_folder, "scores.txt", sep="/")
  print(file)
  results_df = read.csv(file, header = FALSE)
  results_df <- setNames(results_df, c("Evostick"))
  return(results_df)
}

load_genetic_programming <- function(scenario) {
  folder <- paste(RESULT_FOLDER, "genetic_programming", scenario, sep="/")
  file = paste(folder, "gp100p50g_scores.txt", sep="/")
  print(file)
  results_df = read.csv(file, header = FALSE)
  results_df <- setNames(results_df, c("GP BT"))
  return(results_df)
}

load_localsearch <- function(scenario, method) {
  load_localsearch_bt <- function() {
    bt_df <- load_data("BT", scenario, method)
    return(bt_df)
  }
  load_localsearch_fsm <- function() {
    fsm_df <- load_data("FSM", scenario, method)
    return(fsm_df)
  }

  bt_results <- load_localsearch_bt()
  fsm_results <- load_localsearch_fsm()
  results_df <- data.frame(bt_results, fsm_results)
  # results_df <- setNames(results_df, c("Random BT", "Random FSM"))
  return(results_df)
}


load_all_results <- function(scenario) {
  minimal_df <- load_localsearch(scenario, "minimal")
  random_df <- load_localsearch(scenario, "random")
  improve_df <- load_localsearch(scenario, "improve")
  irace <- load_irace(scenario)
  print(irace)
  # evostick <- load_evostick(scenario)
  # gp <- load_genetic_programming(scenario)
  all_df <- data.frame(minimal_df, random_df, improve_df, irace)#, evostick, gp)
  return(all_df)
}

compare_scenario <- function(title, scenario) {
  all_df <- load_all_results(scenario)
  boxplot(all_df, main=title, ylab="Score", xlab="Method")
}

compare_all <- function() {
  compare_scenario("Foraging 250sec", "for")
  # also compare agg, AAC, SCA
}
