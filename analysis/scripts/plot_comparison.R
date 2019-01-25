library(ggplot2)

source(file="/home/jkuckling/AutoMoDe-LocalSearch/analysis/scripts/utilities.R")

copy_results_together <- function(list_of_names, list_of_scores) {
  # takes c(name1, name2) and c(scores1, scores2) where scores is again an array
  tmp_names <- list()
  tmp_scores <- list()
  for (i in 1:length(list_of_names)) {
    name <- list_of_names[[i]]
    scores <- list_of_scores[[i]]
    for (score in scores) {
      tmp_names <- unlist(list(tmp_names, name))
      tmp_scores <- unlist(list(tmp_scores, score))
    }
  }
  tmp_df <- data.frame(method=tmp_names, score=tmp_scores)
  return(tmp_df)
}

split_dataframe <- function(df) {
  n = length(df[[1]])
  architecture = character(n)
  method = character(n)
  source = character(n)
  score = numeric(n)
  for (i in 1:n) {
    #print(df[[1]][i])
    #print(df[[2]][i])
    tmp_str = strsplit(as.character(df[[1]][i]), ".", fixed=TRUE)
    architecture[i] = tmp_str[[1]][1]
    method[i] = tmp_str[[1]][2]
    print(class(tmp_str[[1]][3]))
    source[i] = tmp_str[[1]][3]
    score[i] = df[[2]][i]
  }
  df <- data.frame(architecture, method, source, score)
  return(df)
}


load_data <- function(architecture, scenario, method) {
  folder_name <- paste(architecture, scenario, method, sep="_")
  data <- load_data_score_file(folder_name)
  data <- data[c("Simulation", "Pseudo.Reality")]
  return(data)
}

load_evostick <- function(scenario) {
  nn_results <- load_data("NN", scenario, "evostick")
  nn_id = paste("NN", "evostick", sep=".")
  results_df <- copy_results_together(
    c(paste(nn_id, "simulation", sep="."), paste(nn_id, "pseudoreality", sep=".")),
      list(nn_results[[1]], nn_results[[2]]))
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
  bt_id = paste("BT", method, sep=".")
  fsm_id = paste("FSM", method, sep=".")
  results_df <- copy_results_together(
    c(paste(bt_id, "simulation", sep="."), paste(bt_id, "pseudoreality", sep="."),
      paste(fsm_id, "simulation", sep="."), paste(fsm_id, "pseudoreality", sep=".")),
      list(bt_results[[1]], bt_results[[2]], fsm_results[[1]], fsm_results[[2]]))
  return(results_df)
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
  bt_id = paste("BT", "irace", sep=".")
  fsm_id = paste("FSM", "irace", sep=".")

  bt_results <- load_irace_bt()
  fsm_results <- load_irace_fsm()

  results_df <- copy_results_together(
    c(paste(bt_id, "simulation", sep="."), paste(bt_id, "pseudoreality", sep="."),
      paste(fsm_id, "simulation", sep="."), paste(fsm_id, "pseudoreality", sep=".")),
      list(bt_results[[1]], bt_results[[2]], fsm_results[[1]], fsm_results[[2]]))

  return(results_df)
}

load_all_results <- function(scenario) {
  minimal_df <- load_localsearch(scenario, "minimal")
  random_df <- load_localsearch(scenario, "random")
  improve_df <- load_localsearch(scenario, "improve")
  irace_df <- load_irace(scenario)
  evostick_df <- load_evostick(scenario)
  # gp <- load_genetic_programming(scenario)
  #print(minimal_df)
  #print(random_df)
  #print(improve_df)
  #print(irace_df)
  methods <- unlist(list(minimal_df[[1]], random_df[[1]], improve_df[[1]], irace_df[[1]], evostick_df[[1]]))
  scores <-  unlist(list(minimal_df[[2]], random_df[[2]], improve_df[[2]], irace_df[[2]], evostick_df[[2]]))
  all_df = copy_results_together(methods, scores)
  all_df <- split_dataframe(all_df)
  #print(all_df)
  return(all_df)
}

compare_scenario <- function(title, scenario) {
  all_results <- load_all_results(scenario)
  plot_scenario(title, all_results)
}

plot_scenario <- function(title, results) {
  #preprocess results and make factors
  #results$architecture <- factor(results$architecture, levels = results$architecture)
  #results$method <- factor(results$method, levels = results$method)
  #results$source <- factor(results$source, levels = results$source)
  p <- ggplot(results, aes(architecture, score, notch=TRUE)) +
       geom_boxplot(aes(fill=source)) +
       ggtitle(title) + xlab("") + ylab("Score") +
       theme_grey() +
       facet_grid(. ~ method)

  plot(p)
  # boxplot(results, main=title, ylab="Score", xlab="Method")
}

compare_all <- function() {
  compare_scenario("Foraging 250sec", "for")
  compare_scenario("Aggregation 250sec", "agg")
  compare_scenario("AAC 60sec", "AAC")
  compare_scenario("SCA 60sec", "SCA")
}
