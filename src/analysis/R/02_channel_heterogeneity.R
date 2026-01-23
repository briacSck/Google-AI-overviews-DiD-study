################################################################################
# Channel-Level Heterogeneity Analysis
# 
# Estimate AI Overviews impact by traffic channel (direct, search, referral, etc.)
# using monthly data with marketing channel breakdowns.
#
# Author: Briac Sockalingum
################################################################################

library(dplyr)
library(did)
library(ggplot2)
library(tidyr)

################################################################################
# DATA LOADING
################################################################################

data_dir <- "data/raw"

m_US <- read.csv(file.path(data_dir, 'm_2000_mediaos_US.csv'), stringsAsFactors = FALSE)
m_GB <- read.csv(file.path(data_dir, 'm_2000_mediaos_GB.csv'), stringsAsFactors = FALSE)
m_IE <- read.csv(file.path(data_dir, 'm_2000_mediaos_IE.csv'), stringsAsFactors = FALSE)

all_monthly <- bind_rows(m_US, m_GB, m_IE)

# Define main platforms
main_social_domains <- c(
  "youtube.com", "medium.com", "reddit.com",
  "pinterest.com", "discord.com", "messenger.com", "substack.com"
)

# Prepare monthly panel
panel_monthly <- all_monthly %>%
  filter(domain %in% main_social_domains, country %in% c("US", "GB", "IE")) %>%
  mutate(
    id = paste(domain, country, sep = "_"),
    dat = as.POSIXct(paste0(yearmonth, "-01"), format = "%Y-%m-%d"),
    all_traffic_visits = desktop_marketing_channels_visits + mobile_marketing_channels_visits,
    ln_visits = log(all_traffic_visits + 1)
  ) %>%
  filter(dat < as.POSIXct("2024-10-01"))

# Treatment indicator
panel_monthly_filtered <- panel_monthly %>%
  mutate(
    treated = if_else(
      country == "US" & dat < as.POSIXct("2024-05-01") |
      country == "GB" & dat < as.POSIXct("2024-08-01") |
      country == "IE", 0, 1
    ),
    date = as.numeric(dat),
    id = as.numeric(factor(id))
  ) %>%
  group_by(id) %>%
  mutate(G = ifelse(any(treated == 1), min(date[treated == 1]), 0)) %>%
  ungroup()

################################################################################
# CHANNEL-LEVEL ANALYSIS
################################################################################

# Compute channel shares
panel_monthly_with_shares <- panel_monthly_filtered %>%
  group_by(domain, country, dat) %>%
  mutate(total_visits = sum(all_traffic_visits, na.rm=TRUE)) %>%
  ungroup() %>%
  mutate(channel_share = all_traffic_visits / total_visits)

channels <- unique(panel_monthly_with_shares$channel)
results_shares <- list()

output_dir <- "output/did_channels"
dir.create(output_dir, showWarnings = FALSE, recursive = TRUE)

for (ch in channels) {
  cat("\n=== Channel:", ch, "===\n")
  
  temp_data <- panel_monthly_with_shares %>% filter(channel == ch)
  
  if (nrow(temp_data) < 10) {
    cat("Insufficient data for", ch, "\n")
    next
  }
  
  tryCatch({
    # DiD on channel share
    att_channel_share <- att_gt(
      yname = "channel_share",
      tname = "date",
      idname = "id",
      gname = "G",
      data = temp_data,
      control_group = "notyettreated",
      est_method = "dr",
      panel = FALSE
    )
    
    # Overall ATT
    agg <- aggte(att_channel_share, type = "simple")
    
    results_shares[[ch]] <- data.frame(
      channel = ch,
      ATT = round(agg$overall.att, 4),
      SE = round(agg$overall.se, 4),
      CI_lower = round(agg$overall.att - 1.96 * agg$overall.se, 4),
      CI_upper = round(agg$overall.att + 1.96 * agg$overall.se, 4)
    )
    
    # Event study plot
    if (!is.null(att_channel_share$egt)) {
      plot_data_channel <- data.frame(
        event_time = att_channel_share$egt,
        att = att_channel_share$att.egt,
        se = att_channel_share$se.egt
      ) %>% 
        filter(!is.na(att) & !is.na(se) & !is.na(event_time)) %>%
        mutate(
          ci_lower = att - 1.96 * se,
          ci_upper = att + 1.96 * se
        )
      
      if (nrow(plot_data_channel) > 0) {
        p <- ggplot(plot_data_channel, aes(x = event_time, y = att)) +
          geom_hline(yintercept = 0, linetype = "solid", color = "gray60") +
          geom_vline(xintercept = 0, linetype = "dashed", color = "black") +
          geom_point(size = 2, color = "#2166ac") +
          geom_errorbar(
            aes(ymin = ci_lower, ymax = ci_upper),
            width = 0.3, color = "#2166ac"
          ) +
          labs(
            title = paste("Event Study: Channel Share ATT –", ch),
            x = "Periods relative to treatment",
            y = "ATT (channel share)"
          ) +
          theme_minimal(base_size = 13) +
          theme(
            plot.title = element_text(hjust = 0.5, face = "bold", size = 13),
            axis.title = element_text(face = "bold"),
            panel.grid.minor = element_blank()
          )
        
        ggsave(
          filename = file.path(output_dir, paste0("eventstudy_", ch, ".png")),
          plot = p, width = 10, height = 6, dpi = 300
        )
      }
    }
    
  }, error = function(e) {
    cat("Error for channel", ch, ":", e$message, "\n")
  })
}

# Export channel results
results_shares_df <- bind_rows(results_shares)
write.csv(results_shares_df, file.path(output_dir, "channel_results.csv"), row.names = FALSE)

print(results_shares_df)
cat("\nChannel outputs saved to:", output_dir, "\n")
