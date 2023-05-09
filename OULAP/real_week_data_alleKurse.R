setwd("/home/drazan/myproject/Labor/Labordaten/")

library(data.table)

dt_studVle <- fread("../Labordaten/OULAP/studentVle.csv")
dt_courses <- fread("../Labordaten/OULAP/courses.csv")

### Funktion um die Daten zu transformieren und alle Kurse zu extrahieren
kurs_extract <- function(code_mod, code_pres) {
  kopie <- copy(dt_studVle)
  output <- kopie[code_module ==  code_mod & code_presentation == code_pres,
                  ][, "day_click" := sum(sum_click), by = .(id_student, date)
                    ][, c("code_module", "code_presentation", "id_site", "sum_click") := NULL
                      ][, .SD[1], by = .(id_student, date)
                        ][, week := ifelse(date < 0, 0, date)
                          ]
  
  #setcolorder(output, c("id_student", "week", "date", "day_click"))
  
  ## Hilfsmatrix
  x <- matrix(0:272, nrow = 7)
  
  for (i in 1:ncol(x)) {
    output[date %in% x[,i], "week"] <- i
  }
  
  dt_week <- output[, "date" := NULL
                    ][, "clicks" := sum(day_click), by = .(id_student, week)
                      ][, .SD[1], by = .(id_student, week)
                        ][, "day_click" := NULL
                          ][order(rank(id_student))
                            ][, "week_click" := scale(clicks), by = .(week)
                              ][, "clicks" := NULL
                                ]
  return(dt_week)
}

## Funktion um alle data.table, Listen von data.table und txt-Dateien zu erzeugen und abzuspeichern
create_data <- function() {
  code_mod <-  unique(dt_studVle$code_module)
  code_pres <- unique(dt_studVle$code_presentation)
 
  ## Alle 22 Kurse extrahieren und abspeichern
  for (mod in code_mod) {
    for (pres in code_pres) {
      dt <-  kurs_extract(code_mod = mod, code_pres = pres)
      
      setnames(dt, c("week", "week_click"), c("x", "y"))
      
      if(nrow(dt) > 0) {
        saveRDS(dt, paste0("../Labordaten/Courses_dt/", mod, pres, "_w.rds"))
        
        ## Anzahl der Kurstage zur Berechnung der Wochen bestimmen
        total_days <- dt_courses[code_module == mod & code_presentation == pres]$module_presentation_length
        
        dt.list <- split(dt, f = dt$id_student)
        dt.list <- lapply(dt.list, function(df) df[data.frame("x" = 0:ceiling(total_days / 7)), on = c(x = "x")
                                                   ][, c("id_student", "y") :=
                                                       .(ifelse(is.na(id_student), mean(id_student, na.rm = TRUE), id_student),
                                                         ifelse(is.na(y), 0, y))
                                                     ]
                          )
       
        saveRDS(dt.list, paste0("../Labordaten/Courses_list/", mod, pres, "_wlist.rds"))
        
        dir.create(file.path("../Labordaten/Courses_txt/", paste0(mod, pres)))
        
        lapply(dt.list, function(x) write.table(x[, 2:3],
                                                paste0("../Labordaten/Courses_txt/", mod, pres, "/id_", unique(x$id_student), ".txt"),
                                                sep = " \t", row.names = F)
        )
      }
    }
  }
}

system.time(create_data())
##   User      System verstrichen 
## 73.872       4.102      65.883

