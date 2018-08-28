load_results <- function(file){
  dat = read.csv(file, header = FALSE)
  dat <- setNames(dat, c("best", "new", "mutation"))
  dat <- dat[,c("best","new")]
  return(dat)
}

draw_score_history <- function(results, experiment_name, sample_frequency=1) {
  best <- results[,"best"]
  # show only a subset of every sample_frequency element
  best <- best[seq(1, length(best), sample_frequency)]
  plot_title=paste("Best Score", experiment_name, sep=" ")
  plot(best, type="l", main=plot_title)
}

display_experiment <- function(result_dir, exp_name, run_count) {
  run_folder <- paste("run", run_count, sep="_")
  file_name <- paste(result_dir, exp_name, "run_0/scores/best_score.csv", sep="/")
  result_vector <- load_results(file_name)
  draw_score_history(result_vector, exp_name)
  return(result_vector)
}

draw_improvement_boxplot <- function(initial, final, exp_type) {
  plot_title <- paste("Improvement over 10",exp_type,"experiments", sep=" ")
  boxplot(initial, final, names=c("initial", "final"), main=plot_title)
}

show_experiment_series <- function(series) {
  result_dir <- "/home/jkuckling/AutoMoDe-LocalSearch/result"
  initial_results <- 1:10
  final_results <- 1:10
  for (i in 1:10) {
    exp_name <- paste(series, i, sep="_")
    exp_result <- display_experiment(result_dir, exp_name, 0)
    initial_results[i] <- exp_result[1,"best"]
    final_results[i] <- exp_result[nrow(exp_result),"best"]
  }
  draw_improvement_boxplot(initial_results, final_results, series)
}
