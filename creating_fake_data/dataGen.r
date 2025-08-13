library(dplyr)
library(t)
library(lubridate)
library(RMariaDB)

generate_data <- function(start_date = "2023-01-01") {
  b2b_platforms <- c(
    "IndiaMart",
    "Ingram Micro",
    "Rashi Peripherals"
  )
  b2c_platforms <- c(
    "Amazon",
    "Flipkart",
    "Ebay",
    "Blinkit",
    "Reliance Digital",
    "Vijay Sales",
    "Apple Store Online",
    "Croma"
  )
  all_platforms <- c(b2b_platforms, b2c_platforms)
  indian_states <- c(
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal"
  )

  cities <- c(
    "Mumbai",
    "Delhi",
    "Bangalore",
    "Chennai",
    "Kolkata",
    "Hyderabad",
    "Pune",
    "Ahmedabad",
    "Jaipur",
    "Lucknow"
  )
  dates <- seq(as.Date(start_date), Sys.Date(), by = "day")
  products <- list(
    "iphone 16 128 gb" = c(89900, 94900),
    "iphone 15 128 gb" = c(77900, 82900),
    "macbook air m1 256 gb" = c(84900, 89900),
    "macbook pro m1 256 gb" = c(114900, 119900),
    "airpods pro 2nd gen" = c(24900, 26900),
    "airpods max" = c(54900, 59900),
    "apple watch series 9" = c(41900, 45900)
  )
  combination <- expand.grid(
    date = dates,
    product = names(products),
    platform = all_platforms,
    stringsAsFactors = FALSE
  )
  combination$states <- sample(indian_states, nrow(combination), replace = TRUE)
  combination$price <- sapply(1:nrow(combination), function(i) {
    price_range <- products[[combination$product[i]]]
    base_price <- runif(1, price_range[1], price_range[2])

    # Add seasonal variations
    month <- month(combination$date[i])

    # Seasonal factors
    seasonal_factor <- case_when(
      # Diwali season (October-November)
      month %in% c(10, 11) ~ runif(1, 1.0, 1.5),
      # New Year and End of Season Sales (January, July)
      month %in% c(1, 7) ~ runif(1, 0.7, 0.98),
      # Regular months
      TRUE ~ 1
    )

    # Platform-specific adjustments
    platform_factor <- case_when(
      # B2B platforms get lower prices
      combination$platform[i] %in% b2b_platforms ~ runif(1, 0.8, 0.97),
      # Premium for Apple Store Online and iStore
      combination$platform[i] %in% c("Apple Store Online", "iStore") ~ runif(
        1, 1, 1.2
      ),
      # Standard pricing for other B2C platforms
      TRUE ~ 1
    )

    # Calculate final price
    final_price <- base_price * seasonal_factor * platform_factor

    # Add small daily variations (±0.5%)
    daily_variation <- runif(1, 0.995, 1.005)

    round(final_price * daily_variation, 2)
  })

  return(as.data.frame(combination))
}
sample_data <- generate_data()

write.csv(sample_data, file = "sample_data.csv")
