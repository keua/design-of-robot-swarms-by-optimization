result_folder <- "/home/jkuckling/AutoMoDe-LocalSearch/result"
file_location <- "run_0/scores/best_score.csv"
exp_count <- 10 # the number of experiments per scenario

load_from_file <- function(file){
  dat = read.csv(file, header = FALSE)
  dat <- setNames(dat, c("best", "new", "mutation"))
  dat <- dat[,c("best","new")]
  return(dat)
}

build_file_name <- function(controller, scenario, initial, count) {
  folder_name <- paste(controller, scenario, initial, count, sep="_")
  file_name <- paste(result_folder, folder_name, file_location, sep="/")
  return(file_name)
}

get_best_values <- function(controller, scenario, initial) {
  final_results <- 1:exp_count
  for (i in 1:exp_count) {
    data <- load_from_file(build_file_name(controller, scenario, initial, i))
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

display_random <- function(scenario) {
  
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
    file = paste("/home/jkuckling/AutoMoDe-LocalSearch/result/BT", scenario, "irace50k/scores.txt", sep="_")
    dat = read.csv(file, header = FALSE)
    return(dat)
  }
  load_irace_fsm <- function() {
    file = paste("/home/jkuckling/AutoMoDe-LocalSearch/result/FSM", scenario, "irace50k/scores.txt", sep="_")
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
  # display_random(scenario)
  improving <- load_irace_localsearch(scenario)
  irace <- load_irace(scenario)
  all_df <- data.frame(minimal_df, improving, irace)
  return(all_df)
}

display_comparison_agg <- function() {
  all_df <- load_all_results("agg")
  boxplot(all_df)
}

display_comparison_for <- function() {
  all_df <- load_all_results("for")
  boxplot(all_df)
}

display_comparison <- function() {
  display_comparison_agg()
  display_comparison_for()
}