source(file="/home/jkuckling/AutoMoDe-LocalSearch/analysis/scripts/utilities.R")

display_comparison <- function() {
  
  get_best_values <- function(controller, scenario, initial) {
    final_results <- 1:EXP_COUNT
    for (i in 1:EXP_COUNT) {
      exp_name <- paste(controller, scenario, initial, i, sep="_")
      data <- load_score_file(exp_name)
      final_results[i] <- data[nrow(data),"best"]
    }
    return(final_results)
  }
  
  load_minimal <- function(scenario) {
    load_minimal_bt <- function() {
      best <- get_best_values("BT", scenario, "minimal")
      return(best)
    }
    load_minimal_fsm <- function() {
      best <- get_best_values("FSM", scenario, "minimal")
      return(best)
    }
    bt_results <- load_minimal_bt()
    fsm_results <- load_minimal_fsm()
    results_df <- data.frame(bt_results, fsm_results)
    results_df <- setNames(results_df, c("Minimal BT", "Minimal FSM"))
    return(results_df)
  }
  
  load_irace_localsearch <- function(scenario) {
    load_improving_bt <- function() {
      best <- get_best_values("BT", scenario, "irace")
      return(best)
    }
    load_improving_fsm <- function() {
      best <- get_best_values("FSM", scenario, "irace")
      return(best)
    }
    bt_results <- load_improving_bt()
    fsm_results <- load_improving_fsm()
    results_df <- data.frame(bt_results, fsm_results)
    results_df <- setNames(results_df, c("Irace+LS BT", "Irace+LS FSM"))
    return(results_df)
  }
  
  load_random <- function(scenario) {
    load_random_bt <- function() {
      best <- get_best_values("BT", scenario, "random")
      return(best)
    }
    load_random_fsm <- function() {
      best <- get_best_values("FSM", scenario, "random")
      return(best)
    }
    bt_results <- load_random_bt()
    fsm_results <- load_random_fsm()
    results_df <- data.frame(bt_results, fsm_results)
    results_df <- setNames(results_df, c("Random BT", "Random FSM"))
    return(results_df)
  }
  
  load_irace_localsearch <- function(scenario) {
    load_improving_bt <- function() {
      best <- get_best_values("BT", scenario, "irace")
      return(best)
    }
    load_improving_fsm <- function() {
      best <- get_best_values("FSM", scenario, "irace")
      return(best)
    }
    bt_results <- load_improving_bt()
    fsm_results <- load_improving_fsm()
    results_df <- data.frame(bt_results, fsm_results)
    results_df <- setNames(results_df, c("Irace+LS BT", "Irace+LS FSM"))
    return(results_df)
  }
  
  load_irace <- function(scenario) {
    load_irace_bt <- function() {
      folder <- paste(RESULT_FOLDER, "BT", sep="/")
      file = paste(folder, scenario, "irace50k/scores.txt", sep="_")
      dat = read.csv(file, header = FALSE)
      return(dat)
    }
    load_irace_fsm <- function() {
      folder <- paste(RESULT_FOLDER, "BT", sep="/")
      file = paste(folder, scenario, "irace50k/scores.txt", sep="_")
      dat = read.csv(file, header = FALSE)
      return(dat)
    }
    bt_results <- load_irace_bt()
    fsm_results <- load_irace_fsm()
    results_df <- data.frame(bt_results, fsm_results)
    results_df <- setNames(results_df, c("Irace BT", "Irace FSM"))
    return(results_df)
  }
  
  load_all_results <- function(scenario) {
    minimal_df <- load_minimal(scenario)
    # random_df <- load_random(scenario)
    improving <- load_irace_localsearch(scenario)
    # irace <- load_irace(scenario)
    # evostick <- load_evostick(scenario)
    all_df <- data.frame(minimal_df, improving)
    # all_df <- data.frame(minimal_df, random_df, improving, irace)
    return(all_df)
  }
  
  display_comparison_agg <- function() {
    all_df <- load_all_results("agg")
    boxplot(all_df, main="Aggregation", ylab="Score", xlab="Controller")
  }
  
  display_comparison_for <- function() {
    all_df <- load_all_results("for")
    boxplot(all_df, main="Foraging", ylab="Score", xlab="Controller")
  }
  
  # display_comparison_agg()
  display_comparison_for()
}