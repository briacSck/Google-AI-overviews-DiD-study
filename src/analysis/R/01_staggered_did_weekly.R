################################################################################
# Staggered DiD Analysis: Weekly Traffic Data
# 
# This script implements Callaway & Sant'Anna (2021) staggered DiD estimation
# for AI Overviews impact on social media platform traffic.
#
# Treatment timing:
# - US: May 14, 2024 (Wave 1)
# - GB: August 28, 2024 (Wave 2)  
# - IE: Never treated (control)
#
# Author: Briac Sockalingum
# Research context: AI Overviews impact study with Prof. Maximilian Schäfer
################################################################################

# Required packages
required_packages <- c("dplyr", "did", "ggplot2", "ggdid", "xtable")
for (pkg in required_packages) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(pkg)
    library(pkg, character.only = TRUE)
  }
}

################################################################################
# DATA LOADING AND STRUCTURING
################################################################################

# Main social media platforms (excluding x.com due to data anomalies)
main_social_domains <- c(
  "youtube.com", "medium.com", "reddit.com",
  "pinterest.com", "discord.com", "messenger.com", "substack.com"
)

# Load weekly data for all three countries
# NOTE: Update paths to your actual data location
data_dir <- "data/raw"  # Relative to project root

w_US <- read.csv(file.path(data_dir, 'w_2000_mediaos_US.csv'), stringsAsFactors = FALSE)
w_GB <- read.csv(file.path(data_dir, 'w_2000_mediaos_GB.csv'), stringsAsFactors = FALSE)
w_IE <- read.csv(file.path(data_dir, 'w_2000_mediaos_IE.csv'), stringsAsFactors = FALSE)

# Combine all weekly data
all_weekly <- bind_rows(w_US, w_GB, w_IE)

# Filter and prepare panel
panel_weekly <- all_weekly %>%
  filter(
    domain %in% main_social_domains,
    country %in% c("US", "GB", "IE")
  ) %>%
  mutate(
    date_ct = as.POSIXct(date, format = "%Y-%m-%d")
  ) %>%
  filter(!is.na(date_ct) & date_ct < as.POSIXct("2024-10-01"))

# Keep only platforms with at least 1 weekly observation
panel_weekly <- panel_weekly %>%
  group_by(domain) %>%
  filter(any(all_traffic_visits > 0, na.rm = TRUE)) %>%
  ungroup()

# Structure for DiD estimation
panel_weekly <- panel_weekly %>%
  mutate(
    id_str = paste(domain, country, sep = "_"),
    # Treatment indicator: 1 if post-treatment, 0 otherwise
    treated = if_else(
      country == "US" & date_ct < as.POSIXct("2024-05-01") |
      country == "GB" & date_ct < as.POSIXct("2024-08-01") |
      country == "IE", 0, 1
    ),
    date_num = as.numeric(date_ct),
    id_num = as.numeric(factor(id_str))
  ) %>%
  group_by(id_num) %>%
  mutate(G = ifelse(any(treated == 1), min(date_num[treated == 1]), 0)) %>%
  ungroup()

cat("Final panel:\n")
cat("  Rows:", nrow(panel_weekly), "\n")
cat("  Platforms:", paste(unique(panel_weekly$domain), collapse = ", "), "\n")
cat("  Date range:", format(min(panel_weekly$date_ct), "%Y-%m-%d"), 
    "to", format(max(panel_weekly$date_ct), "%Y-%m-%d"), "\n\n")

################################################################################
# STAGGERED DID ESTIMATION (CALLAWAY-SANT'ANNA)
################################################################################

output_dir <- "output/did_weekly"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

# Helper function to format POSIX dates
to_date <- function(x) format(as.POSIXct(x, origin="1970-01-01"), "%Y-%m-%d")

# Store results
results_summary <- data.frame()

for (platform in main_social_domains) {
  cat("\n========================================\n")
  cat("Running DiD for:", platform, "\n")
  cat("========================================\n")
  
  subdata <- panel_weekly %>% filter(domain == platform)
  
  if (nrow(subdata) < 10) {
    cat("Insufficient data - skipping.\n")
    next
  }
  
  # Prepare log-transformed outcome
  panel_weekly_log <- panel_weekly %>%
    filter(domain == platform) %>%
    mutate(ln2_visits = log2(all_traffic_visits + 1))
  
  #-----------------------------------------------------------------------------
  # 1. CLASSIC LEVELS SPECIFICATION
  #-----------------------------------------------------------------------------
  
  didfit <- att_gt(
    yname = "all_traffic_visits",
    tname = "date_num",
    idname = "id_num",
    gname = "G",
    xformla = ~1,
    data = subdata,
    control_group = "notyettreated",
    est_method = "dr",  # Doubly-robust
    panel = FALSE
  )
  
  agg_classic <- aggte(didfit, type = "simple")
  agg_dyn_classic <- aggte(didfit, type = "dynamic", na.rm = TRUE)
  
  #-----------------------------------------------------------------------------
  # 2. LOG SPECIFICATION
  #-----------------------------------------------------------------------------
  
  did_log <- att_gt(
    yname = "ln2_visits",
    tname = "date_num",
    idname = "id_num",
    gname = "G",
    data = panel_weekly_log,
    control_group = "notyettreated",
    est_method = "dr",
    bstrap = TRUE,
    biters = 999,
    panel = FALSE
  )
  
  att_overall_log <- aggte(did_log, type = "simple")
  att_event_log <- aggte(did_log, type = "dynamic")
  
  # Convert log2 ATT to percentage change
  att_log_pct <- 100 * (2^(att_overall_log$overall.att) - 1)
  
  cat("Results:\n")
  cat("  Classic ATT:", round(agg_classic$overall.att, 2), "\n")
  cat("  Log2 ATT (%):", round(att_log_pct, 2), "%\n\n")
  
  # Store summary
  results_summary <- bind_rows(results_summary, data.frame(
    platform = platform,
    att_classic = agg_classic$overall.att,
    se_classic = agg_classic$overall.se,
    att_log_pct = att_log_pct,
    se_log = att_overall_log$overall.se
  ))
  
  #-----------------------------------------------------------------------------
  # 3. EVENT STUDY PLOT (LEVELS)
  #-----------------------------------------------------------------------------
  
  plot_data <- data.frame(
    event_time = agg_dyn_classic$egt,
    att = agg_dyn_classic$att.egt,
    se = agg_dyn_classic$se.egt
  ) %>% 
    filter(!is.na(att) & !is.na(se) & !is.na(event_time)) %>%
    mutate(
      ci_lower = att - 1.96 * se,
      ci_upper = att + 1.96 * se
    )
  
  if (nrow(plot_data) > 0) {
    p <- ggplot(plot_data, aes(x = event_time, y = att)) +
      geom_hline(yintercept = 0, linetype = "solid", color = "gray60") +
      geom_vline(xintercept = 0, linetype = "dashed", color = "black") +
      geom_point(size = 2, color = "#2166ac") +
      geom_errorbar(
        aes(ymin = ci_lower, ymax = ci_upper),
        width = 0.3, color = "#2166ac"
      ) +
      labs(
        title = paste("Event Study: ATT Dynamics –", platform),
        x = "Periods relative to treatment",
        y = "ATT (weekly visits)"
      ) +
      theme_minimal(base_size = 13) +
      theme(
        plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
        axis.title = element_text(face = "bold"),
        panel.grid.minor = element_blank()
      )
    
    ggsave(
      filename = file.path(output_dir, paste0(gsub("\\.", "_", platform), "_eventstudy.png")),
      plot = p, width = 10, height = 6, dpi = 300
    )
  }
  
  #-----------------------------------------------------------------------------
  # 4. EVENT STUDY PLOT (LOG)
  #-----------------------------------------------------------------------------
  
  plot_data_log <- data.frame(
    event_time = att_event_log$egt,
    att = att_event_log$att.egt,
    se = att_event_log$se.egt
  ) %>% 
    filter(!is.na(att) & !is.na(se) & !is.na(event_time)) %>%
    mutate(
      ci_lower = att - 1.96 * se,
      ci_upper = att + 1.96 * se
    )
  
  if (nrow(plot_data_log) > 0) {
    p_log <- ggplot(plot_data_log, aes(x = event_time, y = att)) +
      geom_hline(yintercept = 0, linetype = "solid", color = "gray60") +
      geom_vline(xintercept = 0, linetype = "dashed", color = "black") +
      geom_point(size = 2, color = "#d6604d") +
      geom_errorbar(
        aes(ymin = ci_lower, ymax = ci_upper),
        width = 0.3, color = "#d6604d"
      ) +
      labs(
        title = paste("Event Study (Log): ATT Dynamics –", platform),
        x = "Periods relative to treatment",
        y = "ATT (log2 visits)"
      ) +
      theme_minimal(base_size = 13) +
      theme(
        plot.title = element_text(hjust = 0.5, face = "bold", size = 14),
        axis.title = element_text(face = "bold"),
        panel.grid.minor = element_blank()
      )
    
    ggsave(
      filename = file.path(output_dir, paste0(gsub("\\.", "_", platform), "_eventstudy_log.png")),
      plot = p_log, width = 10, height = 6, dpi = 300
    )
  }
}

################################################################################
# EXPORT SUMMARY RESULTS
################################################################################

write.csv(results_summary, file.path(output_dir, "summary_results.csv"), row.names = FALSE)

cat("\n========================================\n")
cat("All outputs saved to:", output_dir, "\n")
cat("========================================\n")
