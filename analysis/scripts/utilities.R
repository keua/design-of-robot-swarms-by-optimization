RESULT_FOLDER = "/home/jkuckling/AutoMoDe-LocalSearch/result/Version_3"
EXP_COUNT = 10

transpose <- function(df) {
  # Transpose table YOU WANT
  df.T <- t(df[,1:ncol(df)])
  
  # Set the column headings from the first column in the original table
  # colnames(df.T) <- df[,1]
  return(df.T)
}

load_score_file <- function(folder, columns=c("best", "new")) {
  file_name <- paste(RESULT_FOLDER, folder, "run_0/scores/best_score.csv", sep="/")
  print(file_name)
  dat = read.csv(file_name, header = FALSE)
  dat <- setNames(dat, c("best", "new", "mutation"))
  dat <- dat[,columns]
}