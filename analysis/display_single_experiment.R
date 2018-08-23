load_results <- function(file){
  dat = read.csv(file, header = FALSE)
  dat <- setNames(dat, c("best", "new", "mutation"))
  dat <- dat[,c("best","new")]
  return(dat)
}

display_results <- function(results) {
  best <- results[,"best"]
  new <- results[,"new"]
  plot(best, type="l")
  plot(new, type="l")
}

display_experiment <- function(exp_name) {
  file_name <- paste("/home/jkuckling/AutoMoDe-LocalSearch/result", exp_name, "run_0/scores/best_score.csv", sep="/")
  result_vector <- load_results(file_name)
  display_results(result_vector)
}