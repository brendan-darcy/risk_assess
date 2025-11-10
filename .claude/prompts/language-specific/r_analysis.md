# Skills: r, tidyverse, statistical_analysis, data_visualization, reproducible_research
# SSDF Practice Group: PW (Produce Well-Secured Software)
# ARMATech Principles: Data-Driven, Modern
# Language: R
# Context: Apprise Risk Solutions P&T Team - R Statistical Analysis

## Security Reminder
⚠️ **CRITICAL**: R scripts may process sensitive valuation data. Ensure no production data is committed to version control, use secure data paths, and generate reproducible reports with dummy data examples.

## Security Checklist
- [ ] .claudeignore exists and includes: **/*.csv, **/data/**, **/*.env, credentials.json
- [ ] Working in Dev/Sandbox environment only (NOT Production)
- [ ] Using dummy test data (NO client/production data)
- [ ] Will delete Claude Code chat history after this session
- [ ] Pre-flight check passed (`./pre-flight-check.sh`)

## Placeholders
- `[SCRIPT_NAME]` - R script name (snake_case, e.g., "valuation_analysis", "territory_comparison")
- `[ANALYSIS_TYPE]` - Analysis type (descriptive | regression | hypothesis_testing | time_series | clustering)
- `[DATA_SOURCE]` - Data source (CSV path, database connection, S3 path)
- `[OUTPUT_FORMAT]` - Output format (HTML | PDF | Word | PowerPoint)

---

## Task: R Statistical Analysis Development

You are a data analyst/statistician at Apprise Risk Solutions developing R scripts for statistical analysis and reporting on the ARMATech valuation platform. Generate production-ready, reproducible, well-documented R code following tidyverse standards and Apprise coding practices.

### Context

**Company**: Apprise Risk Solutions
- R/POSIT for statistical analysis and reporting
- Tidyverse for data manipulation and visualization
- R Markdown for reproducible reports
- ISO 27001:2022 compliant, minimum 70% test coverage

**R Environment**:
- **Version**: R 4.3.1
- **IDE**: POSIT Workbench (formerly RStudio Server)
- **Packages**: tidyverse, data.table, testthat, knitr, rmarkdown
- **Package Management**: renv for reproducibility

**R Standards at Apprise**:
- **Style**: Tidyverse style guide (snake_case, <- for assignment)
- **Packages**: Tidyverse for most tasks, data.table for large datasets
- **Documentation**: Roxygen2-style comments for functions
- **Testing**: testthat for unit tests (70%+ coverage)
- **Reproducibility**: R Markdown for reports, renv for package management

---

## R Development Specification

**Script Name**: [SCRIPT_NAME]

**Analysis Type**: [ANALYSIS_TYPE]

**Data Source**: [DATA_SOURCE]

**Output Format**: [OUTPUT_FORMAT]

**Test Coverage Target**: 70% minimum

---

## Instructions

### Phase 1: DESIGN (Analysis Architecture)

**1. Project Structure**

```
[project_name]/
├── R/
│   ├── 01_data_import.R          # Data loading functions
│   ├── 02_data_cleaning.R        # Cleaning & validation
│   ├── 03_analysis.R             # Statistical analysis
│   ├── 04_visualization.R        # Plotting functions
│   └── utils.R                   # Helper functions
├── tests/
│   └── testthat/
│       ├── test-import.R
│       ├── test-cleaning.R
│       └── test-analysis.R
├── reports/
│   └── analysis_report.Rmd       # R Markdown report
├── data/
│   ├── raw/                      # Raw data (gitignored)
│   └── processed/                # Processed data
├── output/
│   ├── figures/                  # Saved plots
│   └── tables/                   # Saved tables
├── renv/                         # Package environment
├── renv.lock                     # Package versions
├── .Rprofile                     # Project-specific settings
└── README.md                     # Project documentation
```

**2. Package Management (renv)**

```r
# Initialize renv for project
renv::init()

# Install packages
install.packages(c("tidyverse", "data.table", "testthat", "knitr", "rmarkdown"))

# Save package versions
renv::snapshot()

# Restore environment (for collaborators)
renv::restore()
```

**3. tidyverse vs data.table**

**Use tidyverse** (default):
- Dataset < 1 GB
- Readability important
- Standard transformations (filter, mutate, summarize)
- Data visualization (ggplot2)

**Use data.table** (performance):
- Dataset > 1 GB
- Speed critical
- Complex joins/aggregations
- Memory efficiency needed

---

### Phase 2: IMPLEMENT (R Code Generation)

**1. Data Import** (`R/01_data_import.R`)

```r
#' Import Valuation Data
#'
#' Reads valuation data from CSV file and performs basic validation.
#'
#' @param file_path Path to CSV file
#' @return tibble with valuation data
#' @export
#' @examples
#' data <- import_valuation_data("data/raw/valuations.csv")
import_valuation_data <- function(file_path) {
  # Input validation
  if (!file.exists(file_path)) {
    stop(glue::glue("File not found: {file_path}"))
  }

  # Read CSV
  data <- readr::read_csv(
    file_path,
    col_types = readr::cols(
      job_number = readr::col_character(),
      territory = readr::col_factor(levels = c("NSW_ACT", "QLD", "VIC_TAS", "SA_NT", "WA")),
      date_lodged = readr::col_date(format = "%Y-%m-%d"),
      status = readr::col_character(),
      days_to_complete = readr::col_double()
    ),
    na = c("", "NA", "NULL")
  )

  # Basic validation
  if (nrow(data) == 0) {
    warning("Dataset is empty")
  }

  # Log import
  message(glue::glue("Imported {nrow(data)} records from {basename(file_path)}"))

  return(data)
}
```

**2. Data Cleaning** (`R/02_data_cleaning.R`)

```r
library(tidyverse)

#' Clean Valuation Data
#'
#' Performs data cleaning and standardization.
#'
#' @param data Raw valuation data (tibble)
#' @return Cleaned tibble
#' @export
clean_valuation_data <- function(data) {
  data_clean <- data %>%
    # Remove duplicates
    distinct(job_number, .keep_all = TRUE) %>%

    # Filter valid dates
    filter(!is.na(date_lodged)) %>%
    filter(date_lodged >= as.Date("2020-01-01")) %>%

    # Standardize status
    mutate(
      status = case_when(
        status %in% c("Completed", "jobCompleted", "Valuation Completed") ~ "completed",
        status %in% c("In Progress", "inProgress") ~ "in_progress",
        status %in% c("Canceled", "Cancelled") ~ "canceled",
        TRUE ~ tolower(trimws(status))
      )
    ) %>%

    # Handle missing values
    mutate(
      days_to_complete = if_else(is.na(days_to_complete), 0, days_to_complete)
    ) %>%

    # Add derived columns
    mutate(
      year = lubridate::year(date_lodged),
      month = lubridate::month(date_lodged, label = TRUE),
      quarter = lubridate::quarter(date_lodged)
    ) %>%

    # Arrange by date
    arrange(date_lodged)

  # Validation checks
  n_removed <- nrow(data) - nrow(data_clean)
  if (n_removed > 0) {
    message(glue::glue("Removed {n_removed} invalid records"))
  }

  return(data_clean)
}

#' Validate Data Quality
#'
#' Checks data quality and prints summary.
#'
#' @param data Cleaned data (tibble)
#' @return List with validation results
#' @export
validate_data_quality <- function(data) {
  # Check for nulls in critical columns
  null_checks <- data %>%
    summarise(
      across(
        c(job_number, territory, date_lodged),
        ~sum(is.na(.)),
        .names = "null_{.col}"
      )
    )

  # Check for duplicates
  duplicate_count <- data %>%
    group_by(job_number) %>%
    filter(n() > 1) %>%
    nrow()

  # Date range
  date_range <- data %>%
    summarise(
      min_date = min(date_lodged, na.rm = TRUE),
      max_date = max(date_lodged, na.rm = TRUE)
    )

  # Print summary
  cat("\n=== Data Quality Summary ===\n")
  cat(glue::glue("Total records: {nrow(data)}"), "\n")
  cat(glue::glue("Null job_number: {null_checks$null_job_number}"), "\n")
  cat(glue::glue("Null territory: {null_checks$null_territory}"), "\n")
  cat(glue::glue("Null date_lodged: {null_checks$null_date_lodged}"), "\n")
  cat(glue::glue("Duplicate job_numbers: {duplicate_count}"), "\n")
  cat(glue::glue("Date range: {date_range$min_date} to {date_range$max_date}"), "\n")

  return(list(
    null_checks = null_checks,
    duplicate_count = duplicate_count,
    date_range = date_range
  ))
}
```

**3. Statistical Analysis** (`R/03_analysis.R`)

```r
library(tidyverse)

#' Calculate Territory Metrics
#'
#' Calculates completion rates and average days by territory.
#'
#' @param data Cleaned valuation data
#' @return tibble with territory metrics
#' @export
calculate_territory_metrics <- function(data) {
  metrics <- data %>%
    group_by(territory) %>%
    summarise(
      total_jobs = n(),
      completed_jobs = sum(status == "completed"),
      completion_rate = completed_jobs / total_jobs,
      avg_days = mean(days_to_complete, na.rm = TRUE),
      median_days = median(days_to_complete, na.rm = TRUE),
      sd_days = sd(days_to_complete, na.rm = TRUE),
      .groups = "drop"
    ) %>%
    arrange(desc(completion_rate))

  return(metrics)
}

#' Perform t-test Between Territories
#'
#' Tests if completion rates differ significantly between two territories.
#'
#' @param data Cleaned valuation data
#' @param territory_a First territory
#' @param territory_b Second territory
#' @return t-test result
#' @export
compare_territories <- function(data, territory_a, territory_b) {
  # Filter to two territories
  data_subset <- data %>%
    filter(territory %in% c(territory_a, territory_b))

  if (nrow(data_subset) < 10) {
    stop("Insufficient data for t-test (need at least 10 observations)")
  }

  # Perform t-test
  result <- t.test(
    days_to_complete ~ territory,
    data = data_subset,
    var.equal = FALSE  # Welch's t-test
  )

  # Print result
  cat("\n=== Territory Comparison ===\n")
  cat(glue::glue("{territory_a} vs {territory_b}"), "\n")
  cat(glue::glue("t-statistic: {round(result$statistic, 3)}"), "\n")
  cat(glue::glue("p-value: {round(result$p.value, 4)}"), "\n")
  cat(glue::glue("95% CI: [{round(result$conf.int[1], 2)}, {round(result$conf.int[2], 2)}]"), "\n")

  if (result$p.value < 0.05) {
    cat("Result: Statistically significant difference (p < 0.05)\n")
  } else {
    cat("Result: No statistically significant difference (p ≥ 0.05)\n")
  }

  return(result)
}

#' Linear Regression Model
#'
#' Builds regression model to predict completion days.
#'
#' @param data Cleaned valuation data
#' @return lm model object
#' @export
build_regression_model <- function(data) {
  # Build model
  model <- lm(
    days_to_complete ~ territory + year + quarter,
    data = data
  )

  # Print summary
  print(summary(model))

  # Model diagnostics
  par(mfrow = c(2, 2))
  plot(model)
  par(mfrow = c(1, 1))

  return(model)
}
```

**4. Data Visualization** (`R/04_visualization.R`)

```r
library(tidyverse)
library(scales)

#' Plot Completion Rate by Territory
#'
#' Creates bar chart of completion rates.
#'
#' @param metrics Territory metrics tibble
#' @return ggplot object
#' @export
plot_completion_rate <- function(metrics) {
  p <- ggplot(metrics, aes(x = reorder(territory, completion_rate), y = completion_rate)) +
    geom_col(fill = "#0070d2", alpha = 0.8) +
    geom_text(
      aes(label = percent(completion_rate, accuracy = 0.1)),
      hjust = -0.2,
      size = 4
    ) +
    coord_flip() +
    scale_y_continuous(labels = percent, limits = c(0, 1.1)) +
    labs(
      title = "Completion Rate by Territory",
      subtitle = "Percentage of valuations completed",
      x = "Territory",
      y = "Completion Rate"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      plot.subtitle = element_text(size = 12),
      axis.title = element_text(size = 12),
      axis.text = element_text(size = 10)
    )

  return(p)
}

#' Plot Time Series
#'
#' Creates time series plot of daily jobs.
#'
#' @param data Cleaned valuation data
#' @return ggplot object
#' @export
plot_time_series <- function(data) {
  # Aggregate by date
  daily_jobs <- data %>%
    count(date_lodged, name = "jobs")

  p <- ggplot(daily_jobs, aes(x = date_lodged, y = jobs)) +
    geom_line(color = "#0070d2", size = 1) +
    geom_smooth(method = "loess", color = "red", linetype = "dashed", se = FALSE) +
    scale_x_date(date_breaks = "3 months", date_labels = "%b %Y") +
    labs(
      title = "Daily Valuation Jobs Over Time",
      subtitle = "With LOESS trend line",
      x = "Date",
      y = "Number of Jobs"
    ) +
    theme_minimal() +
    theme(
      plot.title = element_text(size = 16, face = "bold"),
      axis.text.x = element_text(angle = 45, hjust = 1)
    )

  return(p)
}

#' Save Plot
#'
#' Saves ggplot to file with consistent formatting.
#'
#' @param plot ggplot object
#' @param filename Output filename
#' @param width Width in inches
#' @param height Height in inches
#' @export
save_plot <- function(plot, filename, width = 10, height = 6) {
  ggsave(
    filename,
    plot = plot,
    width = width,
    height = height,
    dpi = 300,
    bg = "white"
  )

  message(glue::glue("Plot saved to: {filename}"))
}
```

**5. R Markdown Report** (`reports/analysis_report.Rmd`)

````markdown
---
title: "Valuation Analysis Report"
author: "P&T Team - Apprise Risk Solutions"
date: "`r Sys.Date()`"
output:
  html_document:
    toc: true
    toc_float: true
    theme: cosmo
    highlight: tango
    code_folding: hide
params:
  data_path: "data/raw/valuations.csv"
  start_date: "2024-01-01"
  end_date: "2024-12-31"
---

```{r setup, include=FALSE}
knitr::opts_chunk$set(
  echo = TRUE,
  message = FALSE,
  warning = FALSE,
  fig.width = 10,
  fig.height = 6
)

library(tidyverse)
library(knitr)
source("../R/01_data_import.R")
source("../R/02_data_cleaning.R")
source("../R/03_analysis.R")
source("../R/04_visualization.R")
```

## Executive Summary

This report analyzes valuation completion metrics for the period **`r params$start_date`** to **`r params$end_date`**.

## Data Import

```{r import}
data_raw <- import_valuation_data(params$data_path)
data_clean <- clean_valuation_data(data_raw)
```

Imported **`r nrow(data_clean)`** records.

## Data Quality

```{r quality}
validation <- validate_data_quality(data_clean)
```

## Territory Analysis

```{r territory-metrics}
metrics <- calculate_territory_metrics(data_clean)

kable(
  metrics,
  digits = 2,
  col.names = c("Territory", "Total Jobs", "Completed", "Completion Rate", "Avg Days", "Median Days", "SD Days"),
  caption = "Territory Performance Metrics"
)
```

### Completion Rate Visualization

```{r plot-completion}
plot_completion_rate(metrics)
```

## Time Series Analysis

```{r plot-timeseries}
plot_time_series(data_clean)
```

## Statistical Testing

```{r ttest}
compare_territories(data_clean, "NSW_ACT", "QLD")
```

## Regression Model

```{r regression}
model <- build_regression_model(data_clean)
```

## Conclusions

- Territory **`r metrics$territory[1]`** has the highest completion rate at **`r percent(metrics$completion_rate[1], accuracy = 0.1)`**
- Average completion time is **`r round(mean(data_clean$days_to_complete, na.rm = TRUE), 1)`** days
- Statistical analysis shows [summarize key findings]

---

*Report generated on `r Sys.time()`*
```
````

---

### Phase 3: TEST (70% Coverage Target)

**Unit Tests** (`tests/testthat/test-analysis.R`)

```r
library(testthat)
library(tibble)
source("../../R/03_analysis.R")

test_that("calculate_territory_metrics works correctly", {
  # Arrange
  test_data <- tribble(
    ~territory, ~status, ~days_to_complete,
    "NSW_ACT", "completed", 5,
    "NSW_ACT", "completed", 7,
    "NSW_ACT", "in_progress", 0,
    "QLD", "completed", 10
  )

  # Act
  result <- calculate_territory_metrics(test_data)

  # Assert
  expect_equal(nrow(result), 2)
  expect_equal(result$total_jobs[result$territory == "NSW_ACT"], 3)
  expect_equal(result$completed_jobs[result$territory == "NSW_ACT"], 2)
  expect_equal(result$completion_rate[result$territory == "NSW_ACT"], 2/3)
})

test_that("compare_territories requires sufficient data", {
  # Arrange
  test_data <- tribble(
    ~territory, ~days_to_complete,
    "NSW_ACT", 5,
    "QLD", 10
  )

  # Act & Assert
  expect_error(
    compare_territories(test_data, "NSW_ACT", "QLD"),
    "Insufficient data"
  )
})
```

**Run Tests**:
```r
# Run all tests
testthat::test_dir("tests/testthat")

# With coverage
covr::package_coverage()
```

---

## Output Expected

1. **R Scripts**: `R/*.R` (modular functions)
2. **Tests**: `tests/testthat/test-*.R` (70%+ coverage)
3. **Report**: `reports/analysis_report.Rmd` (reproducible)
4. **Output**: HTML/PDF report, saved plots, tables

---

## Related Templates

- Use `../workflows/data_analyst_csv.md` for CSV analysis patterns
- Use `../core-workflows/secure_feature_development.md` for overall feature development

---

**Template Version**: 1.0
**Last Updated**: October 2025
**Owner**: P&T Team / AI Approach Project
