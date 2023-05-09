setwd("/home/drazan/myproject")

library(stringi)
library(data.table)
library(ggplot2)

## Text-Datei des C++-Outputs transformieren für ggplot
extract_cluster <- function(file_path) {
  require(stringi)
  outfile <- file(file_path, "r")
  clust_no <- as.integer(readLines(outfile, n = 1))
  clust_path <- readLines(outfile, n = 1)
  clust_center <- list()
  clust_elem <- list()
  clust_coord <- list()
  for (i in 1:clust_no) {
    clust_center[i] <- readLines(outfile, n = 1)
    clust_center[i] <- as.data.frame(as.numeric(stri_extract_all_words(clust_center[i], simplify = FALSE)[[1]]))
    clust_center[[i]] <- data.frame(x = clust_center[[i]][seq(1, length(clust_center[[i]]), 2)],
                                    y = clust_center[[i]][seq(2, length(clust_center[[i]]), 2)])
    
    clust_elem[i] <- readLines(outfile, n = 1)
    clust_elem[i] <- stri_replace_all_regex(clust_elem[i], pattern = c('id_', '.txt'), 
                                            replacement = c('', ''), vectorise_all = F)
    clust_elem[i] <- as.data.frame(as.numeric(stri_extract_all_words(clust_elem[i], simplify = FALSE)[[1]]))
  }
  close(outfile)
  
  result <- list("centers" = clust_center, "clusters" = clust_elem)
  return(result)
}

## Angepasste Plotfunktion aus dem Paket klcluster
my_plot_grid_no_points <- function(all_paths, out_dt, name_plot = "") {
  paths <- as.data.frame(data.table::rbindlist(all_paths, idcol = TRUE))
  nr_clusts <- length(out_dt$clusters)
  paths$clust <- 0
  
  for(j in 1:nr_clusts) {
    cluster <- out_dt$clusters[[j]]
    paths$clust[(paths$`.id` %in% cluster)] <- j
  }
  
  counter <- 1
  fp <- data.frame(matrix(0, 0, 3))
  names(fp) <- c("x", "y", "id")
  clusts <- out_dt$clusters
  
  for(j in 1:nr_clusts) {
    paths_in_clust <- clusts[[j]]
    for(i in 1:length(paths_in_clust)) {
      if(dim(all_paths[[i]])[2] > 2){
        all_paths[[i]] <- all_paths[[i]][, 2:3]
      }
      fp[counter, 1:2] <- all_paths[[i]][1,]
      fp[counter, 3] <- j
      counter <- counter + 1
    }
  }
  
  col_pallete <- colorspace::rainbow_hcl(nr_clusts)
  plot_clust <- ggplot()
  grid_plot <- list()
  for(i in 1:nr_clusts) {
    paths_used <- paths[(paths$clust == i), ]
    path_plot <- geom_path(data = paths_used, alpha = 0.8,
                           aes(x = x, y = y, group = .id, col = clust), color = col_pallete[i])
    center_plot <- geom_path(data = out_dt$centers[[i]],
                             aes(x = x, y = y), col = "black")
    center_points <- geom_point(data = out_dt$centers[[i]],
                                aes(x = x, y = y), col = "black", shape = ".")
    # fp_plot <- geom_point(data = fp[fp$id == i,], aes(x = x, y = y),
    #                       shape = 23, fill="red", color="black", size=2)
    # 
    plot_clust <- plot_clust + path_plot + center_plot + center_points 
    # fp_plot
    
    grid_plot[[i]] <- ggplot() + path_plot + center_plot + center_points +
      # fp_plot +
      theme_bw() +
      theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank()) +
      theme(axis.title=element_blank(),
            axis.text=element_blank(),
            axis.ticks=element_blank())
  }
  
  plot_clust <- plot_clust +
    theme_bw() +
    theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank()) +
    theme(axis.title=element_blank(),
          axis.text=element_blank(),
          axis.ticks=element_blank()) +
    ggtitle(name_plot)
  
  grid1 <- cowplot::plot_grid(plotlist = grid_plot, align = 'h', nrow = 1)
  final_grid <- cowplot::plot_grid(grid1, plot_clust, align = 'v', nrow = 2,
                                   rel_heights = c(1, 3))
  
  return(final_grid)
}

## Gespeicherte Liste von data.frame-Objekten laden, week
my_list_week <- readRDS("my_list_week.rds")

## Clustering mit k=3 und l=10, ClusterAlg = Gonzalez, CenterAlg = FSA, week
clust_out <- extract_cluster("out.clustering")
my_plot_grid_no_points(my_list_week, clust_out, "Week, k=3 und l=10")
ggsave("first_clust_week.pdf")

## Gespeicherte Liste von data.frame-Objekten laden, day
my_list_day <- readRDS("my_list_day.rds")
## Clustering mit k=20 und l=10, ClusterAlg = Gonzalez, CenterAlg = FSA, day ohne einen Ausreisser
clust_out2 <- extract_cluster("out2.clustering")
my_plot_grid_no_points(my_list_day, clust_out2, "Day, k=20 und l=10")
ggsave("first_clust_day.pdf")

## Clustering mit k=6 und l=5, ClusterAlg = Gonzalez, CenterAlg = FSA, day ohne einen Ausreisser
clust_out3 <- extract_cluster("out3.clustering")
my_plot_grid_no_points(my_list_day, clust_out3, "Day, k=6 und l=5")
ggsave("first_clust_day_l5.pdf")

## Clustering mit k=5 und l=39, ClusterAlg = Gonzalez, CenterAlg = FSA, day ohne einen Ausreisser
clust_out4 <- extract_cluster("out4.clustering")
my_plot_grid_no_points(my_list_day, clust_out4, "Day, k=5 und l=39")
ggsave("first_clust_day_l39.pdf")

## Clustering mit k=10 und l=20, ClusterAlg = Gonzalez, CenterAlg = kCenter, day nicht zentriert
clust_out_nn <- extract_cluster("out_nn.clustering")
my_plot_grid_no_points(my_list_day_nn, clust_out_nn, "Day nicht-zentriert, k=10 und l=20")
ggsave("first_clust_day_nn.pdf")

## Clustering mit k=10 und l=20, ClusterAlg = SingleLinkage, CenterAlg = kCenter, week
clust_out_vgl <- extract_cluster("out_vgl.clustering")
my_plot_grid_no_points(my_list_week, clust_out_vgl, "Week, Single linkage, kCenter, k=10 und l=20")
ggsave("first_clust_week_vgl.pdf")



## Verschiedene Kurse
setwd("/home/drazan/myproject/Labor/Labordaten/")
## FFF2014J
my_list_week <- readRDS("../Labordaten/Courses_list/FFF2014J_wlist.rds")
clustFFF2014J <- extract_cluster("../../Labor/klcluster-sigspatial19/build/out.clustering")
my_plot_grid_no_points(my_list_week, clustFFF2014J, "Course FFF2014J, week. k = 5, l = 20")
ggsave("../Labordaten/Results/Plots/FFF2014J_k5l20.pdf")


## Nochmal AAA2013J, diesmal nur Pass und Fail, k=2, l=10
my_list_week <- readRDS("Labor/Labordaten/Test/Courses_list/AAA2013J_wlist.rds")
clust <- extract_cluster("Labor/Experimente/clustering_cpp/k2l10.clustering")
my_plot_grid_no_points(my_list_week, clust, "Course AAA2013J, week, k=2, l=10")
ggsave("Labor/Experimente/clustering_cpp/plots/AAA2013J.pdf")


c1 <- clust$clusters[[1]]
c2 <- clust$clusters[[2]]

dt1 <- exam %>% dplyr::filter(id_student %in% c1)
dt2 <- exam %>% dplyr::filter(id_student %in% c2)
prop.table(table(dt1$final_result))
##     Fail     Pass 
## 0.159375 0.840625 
prop.table(table(dt2$final_result))
##       Fail       Pass 
## 0.03448276 0.96551724 

