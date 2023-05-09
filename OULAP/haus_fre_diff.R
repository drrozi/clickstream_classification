
library(klcluster)
library(TSdist)
library(dtw)

setwd("/home/drazan/myproject/Labor/Labordaten/Courses_list/")
my_list_week <- readRDS("AAA2013J_wlist.rds")

pz1 <- my_list_week$`238007`[, 2:3]
pz2 <- my_list_week$`2182846`[, 2:3]

plot(range(0:40), range(-1:4), type = "n", xlab ="week")
lines(pz1, col="blue", type="l")
lines(pz2, col="magenta", type="l")

klcluster::dtw_dist(pz1, pz2, sqr_dist = F, normalize_dist = F)
## 34.25577

TSdist::DTWDistance(pz1, pz2)
## [1] 62.51876

x <- dtw::dtw(pz1, pz2, keep.iternals = TRUE)
x$distance
## 62.51876

oi <- function(a, b) sqrt(sum((a-b)^2))
oi(pz1[,2], pz2[,2])
## [1] 7.286358
man <- function(a, b) sum(abs(a-b))
man(pz1[,2], pz2[,2])

x <- as.matrix(pz1[,2])
y <- as.matrix(pz2[,2])
mat <- rbind(x,y)


## Abstand des "Traversal"
## Variante frechetartig:
trafre <- function(a, b) max(abs(a - b))
trafre(x,y)
## 3.102458

tradtw <- function(a, b, w = length(a)) {
  n <- length(a)
  result <- sum((abs(a - b))[1:w]) / w
  return(result)
}
tradtw(x, y, w =3)
# [1] 1.143609

tradtw(x, y, w = length(x))
# [1] 0.9525605


########################



plot(dtw(pz1[,2], pz2[,2], keep.internals = T,
         step.pattern = rabinerJuangStepPattern(6, "c")),
     type="twoway",
     col=c('blue', 'magenta'),
     match.lty=3,
     lty=1)


klcluster::discrete_frechet(pz1, pz2)
## [1] 1.91313
klcluster::frechet_distance(pz1, pz2, 0.01)
## [1] 2.111418


library(dtwclust)
library(BBmisc)

clust <- dtwclust::tsclust(my_list_week, type = "h", k=5L, 
                           distance = "dtw_basic",
                           control = hierarchical_control(method = "centroid")
                           )

plot(clust, type = "series", clus = 1L)
plot(clust, type = "centroids", clus = 1L)

dt <- reinterpolate(my_list_week, new.length = max(lengths(my_list_week)))

######################

library(pracma)
library(klcluster)
library(SimilarityMeasures)
library(progress)
library(beepr)

## Vergleich der beiden Distanzen anhand der Kursdaten
hausFre_dif <- function(liste) {
  require(progress)
  require(beepr)
  
  n <- length(liste)
  erg_fre <- matrix(0, ncol = n, nrow = n)
  erg_haus <-  matrix(0, ncol = n, nrow = n)
  
  pb <- progress::progress_bar$new(format = "(:spin) [:bar] :percent [Elapsed time: :elapsedfull || Estimated time remaining: :eta]",
                                   total = n, 
                                   complete = "=",
                                   incomplete = "-",
                                   current = ">",
                                   clear = FALSE,
                                   width = 100)
  
  for(i in 1:(n-1)) {
    pz1 <- liste[[i]][, 2:3]
    pb$tick()
    ## Matrix symmetrisch, daher muss nur obere bzw. untere Dreiecksmatrix berechnet werden
    for (j in (i+1):n) {
      pz2 <- liste[[j]][, 2:3]
      
      # Fuer pracma und SimilarityMeasures werden Matrizen benoetigt
      pm1 <- as.matrix(pz1)
      pm2 <- as.matrix(pz2)
      
      erg_fre[i,j] <- klcluster::frechet_distance(pz1, pz2, 0.001)
      erg_haus[i,j] <- pracma::hausdorff_dist(pm1, pm2)
      #erg_fre[i,j] <- SimilarityMeasures::Frechet(pm1, pm2) ## Irrsinnig langsam
    }
    
  }
  
  diff_matrix <- abs(erg_fre - erg_haus)
  
  beepr::beep(1)
  return(list("Hausdorff" = erg_haus, 
              "Frechet" = erg_fre, 
              "Abs. Fehler" = diff_matrix)
         )
  
}

diff_mat <- hausFre_dif(my_list_week) ## frechet precision 0.001


sum(diff_mat$`Abs. Fehler` == 0) /(378*378)

which(diff_mat$`Abs. Fehler` == max(diff_mat$`Abs. Fehler`), arr.ind = T)
##      row col
## [1,]  79 377

SimilarityMeasures::Frechet(as.matrix(my_list_week[[79]][, 2:3]), as.matrix(my_list_week[[377]][, 2:3]))
## 9.62942 

pracma::hausdorff_dist(as.matrix(my_list_week[[79]][, 2:3]), as.matrix(my_list_week[[377]][, 2:3]))
## [1] 4.810189

klcluster::frechet_distance(my_list_week[[79]][, 2:3], my_list_week[[377]][, 2:3], 0.001)
## [1] 9.62942


max_mat <-  function(plist) {
  n <- length(plist)
  pb <- progress::progress_bar$new(format = "(:spin) [:bar] :percent [Elapsed time: :elapsedfull || Estimated time remaining: :eta]",
                                   total = n, 
                                   complete = "=",
                                   incomplete = "-",
                                   current = ">",
                                   clear = FALSE,
                                   width = 100)
  
  
  mat <- matrix(0,  nrow = n, ncol = n)
  
  for (i in 1:(n-1)) {
    pb$tick()
    pz1 <- plist[[i]][, 3]
    
    for (j in (i+1):n) {
      pz2 <- plist[[j]][, 3]
      
      mat[i,j] <- max(abs(pz1 - pz2))
    }
  }
  beep(9)
  return(mat)
}

max_mat <- max_mat(my_list_week)

max_mat[79,377]

sum(round(max_mat,4) != round(diff_mat$Frechet,4))
### [1] 15416
mean((max_mat - diff_mat$Frechet)[round(max_mat,4) != round(diff_mat$Frechet,4)])
## [1] 0.4057278
sum(round(diff_mat$`Abs. Fehler`,4) = 0)

which((max_mat - diff_mat$Frechet) == max((max_mat - diff_mat$Frechet)), arr.ind = T)
##      row col
## [1,] 263 356

pz1 <- my_list_week[[263]][, 2:3]
pz2 <- my_list_week[[356]][, 2:3]

plot(range(0:40), range(-1:20),  pty = "s", type = "n", xlab ="Week",  ylab="Scaled click-count")
axis(side = 1, at = seq(0,40, by = 1), tck = 1, lty = 2, col = "lightgrey")
axis(side = 2, at = seq(-1,10, by = 1), tck = 1, lty = 2, col = "lightgrey")
lines(pz1, col="blue", type="l")
lines(pz2, col="magenta", type="l")
points(pz1, col="blue", pch=20)
points(pz2, col="magenta", pch=20)



pz1 <- my_list_week[[79]][, 2:3]
pz2 <- my_list_week[[377]][, 2:3]

plot(range(0:40), range(-1:10), type = "n", xlab ="Week", ylab="Scaled click-count")
lines(pz1, col="blue", type="l")
lines(pz2, col="magenta", type="l")
abline(h = 0, lty =2)
abline(v = c(0,2), lty = 2)
diff_rund <- round(diff_mat$`Abs. Fehler`, 2)

x <- my_list_week[[79]][3:40, 2:3]
y <- my_list_week[[377]][3:40, 2:3]


Frechet(as.matrix(x), as.matrix(y))
hausdorff_dist(as.matrix(x), as.matrix(y))

## Test fuer SimilarityMeasures::Frechet. Funktion hausFre_dif entsprechend geaendert
system.time(test <- hausFre_dif(my_list_week[1:20]))
##   User      System verstrichen 
## 96.963       0.000      96.942 

## Test fuer pracma::hausdorff_dist. Funktion hausFre_dif entsprechend geaendert
system.time(test <- hausFre_dif(my_list_week[1:20]))
##        User      System verstrichen 
## 0.111       0.001       0.111 



library(SimilarityMeasures)
pm1 <- as.matrix(pz1)
pm2 <- as.matrix(pz2)

Frechet(pm1, pm2)
## 2.104443 
klcluster::frechet_distance(pz1,pz2,0.000001)



hausdorff_dist(pm1, pm2)
## [1] 2.104443

DTW(pm1, pm2)
## [1] 34.25577


### testplot
plot(range(0:40), range(-1:10),  pty = "s", type = "n", xlab ="Week",  ylab="Scaled click-count")
axis(side = 1, at = seq(0,40, by = 1), tck = 1, lty = 2, col = "lightgrey")
axis(side = 2, at = seq(-1,10, by = 1), tck = 1, lty = 2, col = "lightgrey")
lines(pz1, col="blue", type="l")
lines(pz2, col="magenta", type="l")
points(pz1, col="blue", pch=20)
points(pz2, col="magenta", pch=20)


curve_len <- function(pcurve) {
  ## Hilfsfunktion euklidische Distanz
  oi <- function(x, y) sqrt(sum((x-y)^2))
  
  len <- 0
  for (i in 1:(nrow(pcurve)-1)) {
    len <- len + oi(pcurve[i,], pcurve[i+1,])
  }
  return(len)
}

test <- rbind(c(0,0), c(1,5), c(2,0), c(3,0.5), c(4,0), c(5,0.5), c(6,0))
test2 <- rbind(c(0,0), c(1,2), c(2,2), c(3,2), c(4,2), c(5,2), c(6,0))
lines(test)
lines(test2)

curve_len(test)
curve_len(test2)

p <- ggplot() +
  scale_x_continuous(name="Week", limits=c(0, 39), breaks = seq(0, 39, 1)) +
  scale_y_continuous(name="Clicks", limits=c(-1, 10), breaks = seq(-1, 10, 1)) +
  coord_fixed(ratio = 1)
for (i in 1:length(my_list_week)) {
  p <- p + 
    geom_path(data = my_list_week[[i]], aes(x=x, y=y)) 
}

pz1
dtwDist(pz1[,2], pz2[,2])
dist(pz1, method = "DTW")
# 2   6.407780 







knn_cl <- kNN_trajectories(my_list_week, l=15, dist_measure = 1, prec_eps = 0.001)
library(ggplot2)
klcluster::plot_all_clust(my_list_week, knn_cl, "1-kNN Clustering")


