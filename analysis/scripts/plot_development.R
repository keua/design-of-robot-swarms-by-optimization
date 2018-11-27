source(file="/home/jkuckling/AutoMoDe-LocalSearch/analysis/scripts/utilities.R")

# TODO: Normalize the plots perhaps? If so include function into utilites.R to allow the same normalization for all plots

plot_all_series_development <- function() {
  
  load_experiment_series_development <- function(series, architecture, scenario) {
    # load the ten runs
    for (i in 1:EXP_COUNT) {
      exp_name <- paste(architecture, scenario, series, i, sep="_")
      print(exp_name)
      dat <- load_score_file(exp_name, c("best"))
      if (i > 1) {
        results <- data.frame(results, dat)
      } else {
        results <- dat
      }
    }
    # subsample the runs
    subsample <- results[seq(1, nrow(results), 100), ]
    subsample <- transpose(subsample)
    # add the last value
    # TODO
  }
  
  plot_controller_development <- function(series, architecture) {
    # Aggregation
    agg_results <- load_experiment_series_development(series, architecture, "agg")
    title_agg <- paste("Aggregation ", architecture, " (", series, ")",  sep="")
    boxplot(agg_results, main=title_agg, ylab="Score", xlab="Iteration")
    # Foraging
    for_results <- load_experiment_series_development(series, architecture, "for")
    title_for <- paste("Foraging ", architecture, " (", series, ")",  sep="")
    boxplot(for_results, main=title_for, ylab="Score", xlab="Iteration")
  }
  
  plot_series_development <- function(series) {
    plot_controller_development(series, "BT")
    plot_controller_development(series, "FSM")
  }
  
  plot_series_development("minimal")
  plot_series_development("irace")
  plot_series_development("random")
}

plot_single_experiment_development <- function(series, architecture, scenario, i) {
  draw_score_history <- function(results, experiment_name, sample_frequency=1) {
    # show only a subset of every sample_frequency element
    best <- results[seq(1, length(results), sample_frequency)]
    plot_title=paste("Best Score", experiment_name, sep=" ")
    plot(best, type="l", main=plot_title, ylab="Score", xlab="Iteration")
  }
  
  exp_name <- paste(architecture, scenario, series, i, sep="_")
  best_results <- load_score_file(exp_name, c("best"))
  draw_score_history(best_results, exp_name)
}