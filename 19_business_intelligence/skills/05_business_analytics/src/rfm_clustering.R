# Business Analytics R Script
library(tidyverse)
library(forecast)

# Load data
data <- read_csv("data.csv")

# Perform analysis
results <- data %>%
  group_by(segment) %>%
  summarise(
    count = n(),
    mean_value = mean(metric),
    median_value = median(metric)
  )

print(results)
