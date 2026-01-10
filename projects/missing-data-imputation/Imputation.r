library(visdat) #for data visualization


#Load data
data <- read.csv("breast-cancer-wisconsin.txt", header = FALSE, na.strings = "?")
#Treat "?" as NA
vis_miss(data)

#head(data)
#              V1 V2 V3 V4 V5 V6 V7 V8 V9 V10 V11
#       1 1000025  5  1  1  1  2  1  3  1   1   2
#       2 1002945  5  4  4  5  7 10  3  2   1   2
#       3 1015425  3  1  1  1  2  2  3  1   1   2
#       4 1016277  6  8  8  1  3  4  3  7   1   2
#       5 1017023  4  1  1  3  2  1  3  1   1   2
#       6 1017122  8 10 10  8  7 10  9  7   1   4

# Find columns that contain any NA values and report them
na_cols <- which(sapply(data, anyNA))
#sapply(data, anyNA) — applies anyNA to each column of data.

#Because data is a data.frame, sapply iterates columns
#result is a logical vector (vector with TRUE/FALSE values for each column)
#which() returns the indices of the TRUE values

message("NA in column(s): ", paste(na_cols, collapse = ", "))
#use message() to print info without interfering with output values
#OUTPUT: NA in column(s): 7

message("Number of NAs in column 7: ", sum(is.na(data[ ,na_cols]))) #OUTPUT: 16
message("Number of rows in dataset: ", nrow(data)) #OUTPUT: 699
message("Portion of data to be imputed: ", sum(is.na(data[ ,na_cols])) / nrow(data)) #OUTPUT: 0.02288984, below 5% threshold per factor

hist(data$V7[!is.na(data$V7)], main="V7 histogram", xlab="V7") #histogram of V7 excluding NAs
#The distribution appears right-skewed and bimodal. A central tendency measure is a particularly ineffective imputation method here.
#The values in the middle of the distribution are the least common, so using mean or median imputation is not suitable for our distribution.
#We would actually be better off sampling values from the existing distribution to fill in the missing values.
#update: this method exists and is called hot-deck.

col_mean <- colMeans(data[na_cols], na.rm = TRUE) # compute row means, na.rm =ignoring NAs


message("Column mean: ", col_mean)
#output: 3.544656
#col_mode
#output: 1


#Data table copy for mean imputation
data_mean_imputed <- data
col_index <- na_cols #7 in this case

#Replace NA entries in target column of the copied data.frame
na_rows <- which(is.na(data[ ,col_index]))
data_mean_imputed[na_rows, col_index] <- col_mean #overwrite NAs with column mean

#verify no NAs remain
message("NAs remaining after mean imputation: ",sum(is.na(data_mean_imputed))) #OUTPUT: 0


set.seed(999) #for reproducibility
data_subset <- data[-na_rows,] #only use data that does not contain NAs for training and testing
train_data_indices <- sample(1:nrow(data_subset), size = 0.75 * nrow(data_subset)) #75% of data for training
train_data <- data_subset[train_data_indices, ]
test_data <- data_subset[-train_data_indices, ]

model <- lm(V7 ~ ., data = train_data, na.action = na.omit)
#na.action model argument used to handle missing data (what does nmodel do with NAs?)
#na.omit is the action that removes any rows with NA
#na.exclude is similar but preserves alignment for predictions/residuals

summary(model)
#Coefficients:
#              Estimate Std. Error t value Pr(>|t|)    
#(Intercept) -4.195e+00  4.003e-01 -10.480  < 2e-16 ***
#V1          -1.724e-07  1.441e-07  -1.197  0.23202    
#V2           7.989e-03  4.605e-02   0.173  0.86233    
#V3          -1.951e-01  7.908e-02  -2.468  0.01393 *  
#V4           2.185e-01  7.607e-02   2.873  0.00424 ** 
#V5           1.960e-01  4.800e-02   4.083 5.17e-05 ***
#V6           6.546e-02  6.520e-02   1.004  0.31585    
#V8           8.986e-02  6.391e-02   1.406  0.16032    
#V9          -9.668e-02  4.735e-02  -2.042  0.04170 *  
#V10         -7.130e-02  6.083e-02  -1.172  0.24176    
#V11          2.621e+00  2.038e-01  12.860  < 2e-16 ***


#Keep only significant predictors (p < 0.05)
model_2 <- lm (V7 ~  V3+ V4 + V5 + V9 + V11, data = train_data ,na.action = na.omit)


summary(model_2)
#Coefficients:
#            Estimate Std. Error t value Pr(>|t|)    
#(Intercept) -4.40786    0.34839 -12.652  < 2e-16 ***
#V3          -0.16813    0.07547  -2.228  0.02634 *  
#V4           0.22653    0.07531   3.008  0.00276 ** 
#V5           0.21296    0.04658   4.572 6.07e-06 ***
#V9          -0.08917    0.04618  -1.931  0.05405 .  
#V11          2.72963    0.18126  15.059  < 2e-16 ***

#Need to further refine model 2 by removing V9 (borderline)

model_3 <- lm (V7 ~  V3+ V4 + V5 + V11, data = train_data ,na.action = na.omit)
summary(model_3)
#Coefficients:
#            Estimate Std. Error t value Pr(>|t|)    
#(Intercept) -4.28418    0.34337 -12.477  < 2e-16 ***
#V3          -0.19883    0.07398  -2.688  0.00743 ** 
#V4           0.21829    0.07539   2.895  0.00395 ** 
#V5           0.20246    0.04638   4.365 1.54e-05 ***
#V11          2.64539    0.17641  14.996  < 2e-16 ***
#Now all predictors are significant at 0.05 level



#TEST MODELS
#R squared for model 2 (inclusive)
y_true <- test_data$V7
y_pred <- predict(model_2, newdata = test_data)
rss <- sum((y_true - y_pred)^2)  #residual sum of squares
tss <- sum((y_true - mean(y_true))^2)  #total sum
r_squared <- 1 - (rss / tss)
message("R-squared for model 2 on test data: ", r_squared)

#adjusted R squared for model 2 (inclusive)
n <- nrow(test_data)
p <- length(coef(model_2)) - 1 #number of predictors
adj_r_squared <- 1 - (1 - r_squared) * ((n - 1) / (n - p - 1))
message("Adjusted R-squared for model 2 on test data: ", adj_r_squared)

#R squared for model 3 (more refined/exclusive)
y_pred_e <- predict(model_3, newdata = test_data)
rss_e <- sum((y_true - y_pred_e)^2)  #residual sum of squares
r_squared_e <- 1 - (rss_e / tss)
message("R-squared for model 3 on test data: ", r_squared_e)

#adjusted R squared for model 3
n <- nrow(test_data)
p <- length(coef(model_3)) - 1 #number of predictors
adj_r_squared <- 1 - (1 - r_squared) * ((n - 1) / (n - p - 1))
message("Adjusted R-squared for model 3 on test data: ", adj_r_squared)

#test model_1 (unrefined) just to see how it comapres
#R squared for model 3 (more refined/exclusive)
y_pred_e <- predict(model, newdata = test_data)
rss_e <- sum((y_true - y_pred_e)^2)  #residual sum of squares
r_squared_e <- 1 - (rss_e / tss)
message("R-squared for model on test data: ", r_squared_e)

#adjusted R squared for model 1 (unrefined) 
n <- nrow(test_data)
p <- length(coef(model)) - 1 #number of predictors
adj_r_squared <- 1 - (1 - r_squared) * ((n - 1) / (n - p - 1))
message("Adjusted R-squared for model on test data: ", adj_r_squared)

#OUTPUT
#R-squared for model 2 on test data: 0.709707963594459
#Adjusted R-squared for model 2 on test data: 0.700911235218533
#R-squared for model 3 on test data: 0.709039501032617
#Adjusted R-squared for model 3 on test data: 0.70271297476541
#R-squared for model on test data: 0.716220705929633
#Adjusted R-squared for model on test data: 0.691564711319112

#model 3 is marginally best (may not be real/based in chance) 
#retrain model 3 on full dataset without NAs
model_3 <- lm (V7 ~  V3+ V4 + V5 + V11, data = data_subset ,na.action = na.omit)

predictions <- predict(model_3, newdata = data[na_rows,])
predictions

#      24       41      140      146      159      165      236      250 
#6.682551 3.221454 1.238670 1.597542 1.418106 1.238670 1.776978 1.238670 
#     276      293      295      298      316      322      412      618 
#1.597542 6.628811 1.238670 1.153505 2.357393 1.238670 1.238670 1.238670 

regression_imputation_data <- data
regression_imputation_data[na_rows,na_cols] <- predictions
message("NAs remaining after regression imputation: ", sum(is.na(regression_imputation_data))) #OUTPUT: 0


#Imputation with perturbation added to each regression prediction
#Multivariate Imputation by Chained Equations (MICE)
library(mice) #creates multiple imputations (replacement values) for multivariate missing data

set.seed(999) #for reproducibility
imputed_w_perturbation<- mice(data, m = 8, maxit = 10, method = 'pmm')
#m is number of multiple imputations (how many dataset versions we get). The default is m=5. 
#since imputation is stochastic, each dataset will be slightly different.
#maxit is number of iterations to run the imputation process. Default is 5.
#The 'method' argument dictates the statistical technique mice will use to predict missing values.
#PMM means Predictive Mean Matching and it's a non-parametric approach particularly suited for continuous data.
# PMM operates by finding observed values with similar predictive characteristics to the missing entries.
#The missing values are then imputed, thus preserving the distribution and variance of the original data more
#effectively than simpler methods, such as mean imputation.
#ppm is actualy default for numeric data in mice, so we could have omitted method argument here

plot(imputed_w_perturbation) #trace plot to visualize convergence of the imputation process
#checks that maxit iterations were sufficient for stable imputations
#overlapping chains without dift indicate distribution of imputed means/SDs stops changing with iteration
#showing a kind of 'settling' or convergence
completed_data <- complete(imputed_w_perturbation, action = 1)
#The 'complete' function extracts a single completed dataset from the multiple imputations created by mice
