## Alles wichtige in einer dt

setwd("/home/drazan/Dokumente/TU Dortmund/Datenanalyse TU DO/Veranstaltungen/9_WiSe2022_23/Bachelorarbeit")

library(data.table)
library(ggplot2)

dt_ass <- fread("../Bachelorarbeit/Data_Sets/Student_Asses/assessments.csv")
dt_courses <- fread("../Bachelorarbeit/Data_Sets/Student_Asses/courses.csv")
dt_studAss <- fread("../Bachelorarbeit/Data_Sets/Student_Asses/studentAssessment.csv")
dt_studInfo <- fread("../Bachelorarbeit/Data_Sets/Student_Asses/studentInfo.csv")
dt_studReg <- fread("../Bachelorarbeit/Data_Sets/Student_Asses/studentRegistration.csv")
dt_studVle <- fread("../Bachelorarbeit/Data_Sets/Student_Asses/studentVle.csv")
dt_vle <- fread("../Bachelorarbeit/Data_Sets/Student_Asses/vle.csv")

unique(dt_studInfo$final_result)
## [1] "Pass"        "Withdrawn"   "Fail"        "Distinction"
clicknpass <- copy(dt_studVle)
clicknpass <- clicknpass[, c("id_site", "date") := NULL
                         ][, "total_click" := sum(sum_click, na.rm = TRUE), by = .(code_module, code_presentation, id_student)
                           ][, sum_click := NULL
                             ][, .SD[1], by = .(code_module, code_presentation, id_student)
                               ][order(rank(id_student))
                                 ]
setcolorder(clicknpass, c("id_student", "code_module", "code_presentation", "total_click"))

dt1 <- copy(dt_studInfo)
dt1 <- dt1[,c("id_student", "code_module", "code_presentation", "final_result")]


clicknpass <- dt1[clicknpass, on = c(id_student = "id_student",
                                     code_module = "code_module",
                                     code_presentation = "code_presentation")]


