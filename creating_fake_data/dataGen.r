# Load necessary libraries
# dplyr: for data manipulation functions like case_when
# lubridate: for easy date and time functions like month()
library(dplyr)
library(lubridate)

# This function generates a comprehensive dataset of product prices
# across various platforms, locations, and dates.
generate_data <- function(start_date = "2023-01-01") {

  # --- 1. Define Data Dimensions ---

  # Define B2B (Business-to-Business) platforms
  b2b_platforms <- c(
    "IndiaMart",
    "Ingram Micro",
    "Rashi Peripherals"
  )

  # Define B2C (Business-to-Consumer) platforms
  # NOTE: Added "iStore" as it was used in the pricing logic below but not defined here.
  b2c_platforms <- c(
    "Amazon",
    "Flipkart",
    "Ebay",
    "Blinkit",
    "Reliance Digital",
    "Vijay Sales",
    "Apple Store Online",
    "Croma",
    "iStore"
  )

  # Combine all platforms into a single list
  all_platforms <- c(b2b_platforms, b2c_platforms)

  # Define a list of Indian states for location simulation
  indian_states <- c(
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal"
  )

  # Define a sequence of dates from the start date to the current system date, by month
  dates <- seq(as.Date(start_date), Sys.Date(), by = "month")

  # Define the products and their typical price range [min, max]
  products <- list(
    "iphone 16 128 gb" = c(89900, 94900),
    "iphone 15 128 gb" = c(77900, 82900),
    "macbook air m1 256 gb" = c(84900, 89900),
    "macbook pro m1 256 gb" = c(114900, 119900),
    "airpods pro 2nd gen" = c(24900, 26900),
    "airpods max" = c(54900, 59900),
    "apple watch series 9" = c(41900, 45900)
  )

  # --- 2. Create the Base Data Frame ---

  # Use expand.grid to create a data frame with every possible combination
  # of date, product, platform, and state. This ensures a fully exhaustive dataset.
  combination <- expand.grid(
    date = dates,
    product = names(products),
    platform = all_platforms,
    state = indian_states, # Added states to the grid for full permutation
    stringsAsFactors = FALSE
  )

  # --- 3. Calculate Dynamic Pricing for Each Row ---

  # Use sapply to iterate over each row of the 'combination' data frame
  # and calculate a final price based on several factors.
  combination$price <- sapply(1:nrow(combination), function(i) {

    # Get the price range for the current product
    price_range <- products[[combination$product[i]]]
    # Generate a random base price within that range
    base_price <- runif(1, price_range[1], price_range[2])

    # Get the month from the date for seasonal adjustments
    month <- month(combination$date[i])

    # Adjust price based on seasonality (e.g., festivals, sales)
    seasonal_factor <- case_when(
      # Higher prices during Diwali season (October-November)
      month %in% c(10, 11) ~ runif(1, 1.0, 1.5),
      # Lower prices for New Year and End of Season Sales (January, July)
      month %in% c(1, 7) ~ runif(1, 0.7, 0.98),
      # No seasonal adjustment for other months
      TRUE ~ 1
    )

    # Adjust price based on the type of platform
    platform_factor <- case_when(
      # B2B platforms get lower prices (wholesale discount)
      combination$platform[i] %in% b2b_platforms ~ runif(1, 0.8, 0.97),
      # Premium pricing for official Apple channels
      combination$platform[i] %in% c("Apple Store Online", "iStore") ~ runif(1, 1.0, 1.2),
      # Standard pricing for other B2C platforms
      TRUE ~ 1
    )

    # Calculate the price after seasonal and platform adjustments
    final_price <- base_price * seasonal_factor * platform_factor

    # Add a small random daily price fluctuation (±0.5%)
    daily_variation <- runif(1, 0.995, 1.005)

    # Return the final price, rounded to 2 decimal places
    round(final_price * daily_variation, 2)
  })

  # Return the completed data frame
  return(as.data.frame(combination))
}

# --- 4. Generate and Save the Data ---

# Execute the function to generate the data
# This will create a large dataframe, but smaller than the daily version.
sample_data <- generate_data()

# Write the generated data to a CSV file in your working directory
write.csv(sample_data, file = "product_pricing_data_monthly.csv", row.names = FALSE)
