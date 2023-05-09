setwd("/home/drazan/Dokumente/TU Dortmund/Datenanalyse TU DO/Veranstaltungen/9_WiSe2022_23/Bachelorarbeit")

library(data.table)
library(ggplot2)
library(tidyverse)

dt_studVle <- fread("../Bachelorarbeit/Data_Sets/Student_Asses/studentVle.csv")

dt_aaa2013j <- dt_studVle[code_module == "AAA" & code_presentation == "2013J",
                          ][, "day_click" := sum(sum_click), by = .(id_student, date)
                            ][, c("code_module", "code_presentation", "id_site", "sum_click") := NULL
                              ][, .SD[1], by = .(id_student, date)
                                ][, week := ifelse(date < 0, 0, date)
                                  ]

setcolorder(dt_aaa2013j, c("id_student", "week", "date", "day_click"))

## Hilfsmatrix
x <- matrix(0:272, nrow = 7)

for (i in 1:ncol(x)) {
  dt_aaa2013j[date %in% x[,i], "week"] <- i
}
rm(i, x)

dt_week <- dt_aaa2013j[, "date" := NULL
                       ][, "week_click" := sum(day_click), by = .(id_student, week)
                         ][, .SD[1], by = .(id_student, week)
                           ][, "day_click" := NULL
                             ][order(rank(id_student))
                               ][, "week_click" := scale(week_click)]


# setnames(dt_week, c("week", "week_click"), c("lat", "long")) 
# ## oder fuer den C++-Code 
# setnames(dt_week, c("week", "week_click"), c("x", "y"))

my_list_week <- split(dt_week, f = dt_week$id_student)
my_list_week <- lapply(my_list_week, function(x) x[data.frame("week" = 0:39), on = c(week = "week")
                                            ][, c("id_student", "week_click") := .(ifelse(is.na(id_student), 
                                                                                          mean(id_student, na.rm = TRUE), id_student),
                                              ifelse(is.na(week_click), 0, week_click))])

#saveRDS(my_list_week, "/home/drazan/myproject/week_list")

# lapply(my_list_week, function(x) write.table(x[, 2:3],
#                                              paste0("/home/drazan/myproject/experiment_week_zero/id_", unique(x$id_student), ".txt"),
#                                              sep = " \t", row.names = F)
# )

my_list_week_klclust <- lapply(my_list_week, function(x)  {setnames(x, c("week", "week_click"), c("long", "lat")); x[,2:3]}) 

library(klcluster)

all_paths <- list()
for (j in 1:length(my_list_week_klclust)) {
  all_paths[[j]] <- my_list_week_klclust[[j]]
}

clust <- k_l_cluster(all_paths, k = 5, l=39)
klcluster::plot_all_clust_grid(all_paths, clust, "k=5, l=39")
klcluster::plot_grid_no_points(all_paths, clust, "k=5, l=39")

clust20 <- k_l_cluster(all_paths, k=20, l=10)
plot_grid_no_points(all_paths, clust20, "k=20, l=10")

p1 <- ggplot()
for (i in 1:length(liste)) {
  p1 <- p1 + geom_path(data = liste[[i]], aes(x = week, y = week_click))
}
p1

ggplot() +
  geom_path(data = my_list_week[[1]], aes(x = week, y = week_click)) +
  geom_path(data = dt_week[id_student == 11391], aes(x = week, y = week_click), col = "red") +
  geom_point(data = data.frame(x = c(4,9,17,20,21,24,25,26,29,30,33,38,39),
                               y = 0), 
             aes(x=x, y=y), col="green")

