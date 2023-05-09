########################################
## DataTable fuer die Analyse anlegen ##
########################################
setwd("/home/drazan/myproject/Labor/Labordaten/")

library(data.table)

## Daten einlesen
dtv <- fread("../Labordaten/OULAP/studentVle.csv")
dtc <- fread("../Labordaten/OULAP/courses.csv")
dti <- fread("../Labordaten/OULAP/studentInfo.csv")

## Nur Studis die am finalen Examen eines Kurses teilgenommen haben rausfiltern. Distinct und Pass werden zusammengefasst
dti <- dti[, .(code_module, code_presentation, id_student, final_result)
           ][final_result != "Withdrawn"
             ][, final_result := ifelse(final_result == "Fail", 0, 1)]

## Tabellen zusammenfuehren
keycols <- c("code_module", "code_presentation", "id_student")
setkeyv(dti, keycols)
setkeyv(dtv, keycols)
output <- merge(dtv, dti)
rm(dtv, dti)

## Alle clicks eines Studis an einem Tag werden zusammengezaehlt
output <- output[, "day_click" := sum(sum_click), by = .(code_module, code_presentation, id_student, date)
                  ][, c("id_site", "sum_click") := NULL
                    ][, .SD[1], by = .(code_module, code_presentation, id_student, date)
                      ]

## Clicks wochenweise aggregieren:
## Hilfsmatrix
x <- matrix(-28:272, nrow = 7)

for (i in 1:ncol(x)) {
  output[date %in% x[,i], "week"] <- i-4
}
rm(x,i, keycols)

output <- output[, "date" := NULL
                  ][, "week_click" := sum(day_click), by = .(code_module, code_presentation, id_student, week)
                    ][, .SD[1], by = .(code_module, code_presentation, id_student, week)
                      ][, "day_click" := NULL
                      ]

setkeyv(output, c("code_module", "code_presentation"))
setkeyv(dtc, c("code_module", "code_presentation"))
output <- merge(output, dtc)
rm(dtc)

liste <- split(output, by = c("code_module",
                              "code_presentation",
                              "id_student"),
               flatten = TRUE
               )
rm(output)

## Fehlende Wochen, an denen nicht geclickt wurde einfuegen und week_click = 0 setzen
liste <- lapply(liste, 
                function(dt) {
                  max_woche <- ceiling(unique(dt$module_presentation_length) / 7)
                  x <- -3:max_woche
                  idx <- x[!(x %in% dt$week)]
                  
                  df <- data.table("code_module" = unique(dt$code_module),     
                                   "code_presentation" = unique(dt$code_presentation),
                                   "id_student" = unique(dt$id_student),
                                   "week" = idx,
                                   "final_result" = unique(dt$final_result),
                                   "week_click" = 0,
                                   "module_presentation_length" = 0)
                  return(rbind(dt, df))               
                  }
)

## datatable anlegen, 46 erzeugte NAs und unnoetiges entfernen. Dann sortieren
dt <- rbindlist(liste)
dt <- dt[-which(is.na(dt$week)),
         ][, module_presentation_length := NULL
           ][order(code_module, code_presentation, id_student, week)
             ]

saveRDS(dt, "All_Courses/datatable_complete.rds")
