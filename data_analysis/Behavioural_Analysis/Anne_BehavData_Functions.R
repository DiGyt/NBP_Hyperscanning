
## Function 1: Select Synchronous Trials ## 
# check in both directions, delete whole trial if taps are not synchronous
SynchTrials <- function(data) {

  k <-1 
  
  for (p in file_names) {
    
    #create data frame with only trials & taps of sub1 and sub2
    n = length(data[data$pair == p,]$ttap3)/2
    sub12 <- as_tibble(matrix(ncol=3,nrow=n))
    col <- c("sub1", "sub2", "trial")
    colnames(sub12) <- col
    sub12$sub1 <- data[data$pair == p & data$subject==1,]$ttap3
    sub12$sub2 <- data[data$pair == p & data$subject==2,]$ttap3
    sub12$trial <- rep(1:(n/9), each=9)
    
    #create variables to count how many trials are rejected (in both directions) and save rejected trials in list
    count1 <- 1
    count2 <- 1
    rejectedTrials1 <- c()
    rejectedTrials2 <- c()
    
    #loop through whole data set to check for synchrony (direction 1)
    for (i in 2:(length(sub12$sub1)-1)){
      trial = sub12$trial[i]  
      # for synchrony: tap(i) if sub2 must be the closest to tap(i) of sub1
      # set distance between sub1 and sub2 as minimum  
      min = abs(sub12$sub1[i] - sub12$sub2[i])
      # check distance to neighbouring taps of sub2 
      rightTap = abs(sub12$sub1[i] - sub12$sub2[i+1]) 
      leftTap = abs(sub12$sub1[i] - sub12$sub2[i-1])
      
      # compare whether one of the neighbouring taps of sub2 is closer to sub1 (smaller than minimum value)
      val1 = rightTap < min
      val2 = leftTap < min
      
      # reject trial (if one of the neiboughring taps is closer than tap i of sub2)
      if (val1 | val2){
        data[data$pair == p & data$trial==trial,]$ttap3 <- NA
        rejectedTrials1[count1] = trial
        count1 <- count1+1
      }
    }
    # remove duplicates from list of rejected trials
    rejectedTrials1 <- unique(rejectedTrials1)
    
    #loop through whole data set to check for synchrony (direction 2)
    for (i in 2:(length(sub12$sub2)-1)){
      trial = sub12$trial[i]  
      # for synchrony: tap(i) if sub1 must be the closest to tap(i) of sub2
      # set distance between sub1 and sub2 as minimum   
      min = abs(sub12$sub2[i] - sub12$sub1[i])
      # check distance to neighbouring taps of sub1
      rightTap = abs(sub12$sub2[i] - sub12$sub1[i+1]) 
      leftTap = abs(sub12$sub2[i] - sub12$sub1[i-1])
      
      # compare whether one of the neighbouring taps of sub1 is closer to sub2 (smaller than minimum value)
      val1 = rightTap < min
      val2 = leftTap < min
      
      # reject trial if one of the neiboughring taps is closer than tap i of sub2
      if (val1 | val2){
        data[data$pair == p & data$trial==trial,]$ttap3 <- NA
        rejectedTrials2[count2] = trial
        count2 <- count2+1
      }
    }
    # remove duplicates from list of rejected trials
    rejectedTrials2 <- unique(rejectedTrials2)
    
    # create list of all rejected trials (after checking in both directions), converging both lists
    allrejectedTrials <- c(rejectedTrials1, rejectedTrials2)
    # count hwo many trials have been rejected
    countDuplicates <- length(allrejectedTrials[duplicated(allrejectedTrials)])
    
    # final list of all rejected trials per pair, duplicates removed
    rejectedTrials <- unique(allrejectedTrials)
    
    k <- k+1
  }
  
  ### Copied to proper function ###
  # countTrials <- as_tibble(matrix(ncol=2, nrow=length(pair_names)))
  # col <- c("pair", "nrTrials")
  # colnames(countTrials) <- col
  # countTrials$pair <- pair_names
  # i <- 1
  # 
  # for (h in pair_names) {
  #   p <- data[data$pair == h,]$trial
  #   totalTrials$nrTrials[i] <- p[which.max(abs(p))]
  #   i <- i+1
  # }
  
  return(data)
  
}

## Function 2:Count how many trials have been rejected / how many are left? ## 
CountLeftTrials <- function(data) {
  
  # create a list assigning the total number of trials to each pair and the absolute and relative amount of left-over trials
  countTrials <- as_tibble(matrix(ncol=4, nrow=length(file_names)))
  col <- c("pair", "totalTrials", "leftTrials","inPercent" )
  colnames(countTrials) <- col
  countTrials$pair <- file_names
  i <- 1
  
  remNA <- data[complete.cases(data),]
  
  # count trials befor removing non-synchronous trials:
  # remNA <- data
  
  for (p in file_names) {
    q <- remNA[remNA$pair == p,]$trial
    countTrials$totalTrials[i] <- q[which.max(abs(q))]
    countTrials$leftTrials[i] <- length(unique(q))
    countTrials$inPercent[i] <- round(length(unique(q))/3)
    i <- i+1
  }
  
  countLeftTrials <- countTrials[countTrials$totalTrials > 200,]
  return(countLeftTrials)
}

## Function 3: Compute inter-tap intervals between all taps of all subjects ##
# (ITI = interval between the taps for one subject, Result: df with two columns of ITIsub~1~ and ITIsub~2~)
ComputeITI <- function(data) {
  
  # pairs with less than 300 trails removed!!!!
  
  inter_tap1 <- c()
  inter_tap2 <- c()
  pair <- c()
  block <- c()
  trial <- c()
  tapnr <- c()
  
  # create own dataframe for each pair
  for (p in pair_names) {
    test <- data[data$pair == p,]
    # subset dataframe into sub1 and sub2
    x_val1 <- test[test$subject == 1, ]
    x_val2 <- test[test$subject == 2, ]
    
    for (i in 1: (length(x_val1$ttap3)-1)){
      pair <- c(pair, p)
      block <- c(block, x_val1$block[i])
      trial <- c(trial, x_val1$trial[i])
      tapnr <- c(tapnr, x_val1$tapnr[i])
      
      # for all NA's: keep NA as ITI, else calculates ITI (tap[i+1] - tap[i])
      # 1. loop through sub 1 
      if (is.na(x_val1$ttap3[i])){
        inter_tap1 <- c(inter_tap1, NA)
      }
      else{
        inter_tap1 <- c(inter_tap1, (x_val1$ttap3[i+1] - x_val1$ttap3[i]))
        
        # 2. loop through sub 2
      }
      if (is.na(x_val2$ttap3[i])) {
        inter_tap2 <- c(inter_tap2, NA)
      }
      else{
        inter_tap2 <- c(inter_tap2, (x_val2$ttap3[i+1] - x_val2$ttap3[i]))
      }
    }
  }
  # create dataframe of the lists from above (inter_tap1 and inter_tap2 = ITI of sub1 and sub2 respectively)
  ITI <- cbind(pair, block, trial, tapnr, inter_tap1, inter_tap2)
  ITI <- as_tibble(ITI) ## not already a dataframe??
  
  # remove tap nr.9: no subsequent tap to calculate interval > no sensible ITI value
  ITI <- ITI[ITI$tapnr !=9,]
  #remove all NA's and  delete non-synchronous trials (might not be always usefule, because reduces size of data frame!)
  ITI <- ITI[complete.cases(ITI),]
  ITI[] <- lapply(ITI, function(x) as.numeric(as.character(x)))
  
  
  return(ITI)
}


##Function 4: Compute Delta between all taps of all trials ##
# (Delta = distance between tap~i~ of sub~1~ and sub~2~, Result: df with two columns of DeltaTap~i~ and DeltaTap~i+1~)*  
# (if delta is negative: sub~1~ is leading, if positive: sub~2~ is leading)*
ComputeDelta <- function(data) {
  
  # non-synchronous trials / NA's in the data not yet removed!!!!
  # to remove run: data <- data[complete.cases(data),]
  # loop of trials has to run through list: trialsPair <- unique(data[data$pair == y,]$trial)
  
  # Create new dataframe for Delta's
  Delta <- as_tibble(matrix(ncol=6,nrow=0))
  pair <- c()
  block <- c()
  trial <- c()
  tapnr <- c()
  delta <- c()
  delta1 <- c()

  
  # pairs with less than 300 trails removed!!!!
  
  for (p in pair_names) {
    # loop through all trials (nr. of tirals not always 300!!)
    for (z in 1:LeftTrials[LeftTrials$pair==p,]$totalTrials) {
      # list of all ttap3 for each trial of one pair
      x_val <- data[data$pair == p & data$trial == z,]$ttap3
      k <- 1
      # loop trough trials: substract tap(i) of sub1 from tap(i) of sub2 
      # if delta is negative: sub1 is leading, if positive: sub2 is leading
      for (x in 1:9) {
        pair <- c(pair, p)
        trial <- c(trial, z)
        tapnr <- c(tapnr, x)
        block <- c(block,  data[data$pair == p & data$trial == z,]$block[1])
        delta <- c(delta, (x_val[k] - x_val[k+9])) # subtract tap(i)sub2 from tap(i)sub1
        k <- k+1
      }
    }
  }
  
  #save Delta's in a proper dataframe 
  Delta <- cbind(pair, block, trial, tapnr, delta, delta1)
  Delta <- as_tibble(Delta)
  
  #Add column for delta of subsequent tap  (delta i+1)
  for (i in 1:length(Delta$delta)) {
    Delta$delta1[i] <- Delta$delta[i+1]
  }
  
  #remove all rows with NA's and thus all non-synchronous trials
  DeltaSync <- Delta[complete.cases(Delta),]
  #remove 9th tap (does not have delta+1)
  DeltaSync<- DeltaSync[DeltaSync$tapnr != 9,]#
  DeltaSync[] <- lapply(DeltaSync, function(x) as.numeric(as.character(x)))
  
  return(DeltaSync)
}

## Function 5.2: Compute Cross Correlation (without windows!!)
## of the two time series: ITIsub~1~ and ITIsub~2~ ##

ComputeCCF <- function(ITI) {
  
  # data frame "ITI" contains the ITI of both subjects (inter_tap1 = ITI of sub1, inter_tap2 = ITI of sub2) 
  CCFfull <- c()
  
  # pairs with less than 300 trails removed!!!!
  # sample:
  # pair_names <- c("208", "211","204")
  
  for(p in pair_names){
    
    resultPair <-  ITI[ITI$pair == p,]
    
    resultPair[] <- lapply(resultPair, function(x) as.numeric(as.character(x)))
    trialsPair <- unique(resultPair$trial)
    
    trials <- c()  
    lags <- c()
    value <- c()
    block <- c()
    
    #loop through all trials
    for (t in trialsPair){
      # max. lag 4, suppressing the plots
      ITIsub1 <-resultPair[resultPair$trial == t,]$inter_tap1 
      ITIsub2 <-resultPair[resultPair$trial ==t,]$inter_tap2 
      ccfvalues <- ccf(ITIsub1, ITIsub2, lag = 4, pl = FALSE)
      trials <- c(trials, t)
      lags <- c(lags, ccfvalues$lag)
      value <- c(value, ccfvalues$acf)
      block <- c(block, resultPair[resultPair$trial == t,]$block[1])
    }
    
    
    # repeat by 9: 9 correlation values for each window 
    block <- rep(block, each = 9)
    trials <- rep(trials, each = 9)
    
    # create dafa-frame of the CCF-values
    CCF <- cbind(block,trials, lags, value)
    CCF <- as_tibble(CCF)
    
    pair<- rep(p, times = length(CCF$value))
    CCF <- cbind(pair, CCF)
    CCFfull <- rbind(CCFfull, CCF)
  }
  return(CCFfull)
}

# Function 6: Compute mean-CCF ##
# for all windows over blocks: average ccf-values according to the lags  
# Result: one mean value per lag > 7 mean-values per window > 3 windows per trial

SumCCF <- function(CCF){
  
  sumCCF <- summarySE(data = CCF, measurevar = "value", groupvars = c("pair","block","lags"), na.rm = FALSE, conf.interval = 0.95, .drop = TRUE)
  #sumBlockCCF <- summarySE(data = CCF, measurevar = "value", groupvars = c("pair", "lags"), na.rm = FALSE, conf.interval = 0.95, .drop = TRUE)
  
  return(sumCCF)
}

# Function 7: SYNC INDEX (from Novembre, 2017)
# alpha = alpha measure (range [0:360])
# alpha_lin = linearized alpha (range[0:180])
ComputeAlpha <- function(data){

dataSync <- data[complete.cases(data),]
  
alpha <- c()
alpha_lin <- c()
Alpha <- c()
pair <- c()
block <- c()
trial <- c()
tapnr <- c()
count <- 1

for (p in pair_names){
  trials <- unique(dataSync[dataSync$pair == p,]$trial)
  for (tr in trials){
    # alternate which subject is reference subject and which is follower subject in the circular measure
    if (tr %% 2 > 0){ 
      ref_sj = 1
      fol_sj = 2
    }else{
      ref_sj = 2
      fol_sj = 1
    }
    tapFol <- dataSync[dataSync$pair == p & dataSync$trial == tr & dataSync$subject == fol_sj,]$ttap3
    tapRef <- dataSync[dataSync$subject == ref_sj & dataSync$pair == p  & dataSync$trial == tr,]$ttap3

    for (i in 1:8){
      counter = tapFol[i] - tapRef[i]
      denominator = tapRef[i+1] - tapRef[i]
      
      idx = abs((counter/denominator) * 360)
      idx_lin = abs((180 - abs(idx - 180)))
      
      alpha <- c(alpha, idx)
      alpha_lin <- c(alpha_lin, idx_lin)
      count <- count+1
      tapnr <- c(tapnr, i)
      trial <- c(trial, tr)
      block <- c(block,  dataSync[dataSync$pair == p & dataSync$trial == tr,]$block[1])
      pair <- c(pair, p)
    }

  }
  Alpha = cbind(pair, block, trial, tapnr, alpha, alpha_lin) #append vector to dataframe
  Alpha <- as_tibble(Alpha)
}
  Alpha[] <- lapply(Alpha, function(x) as.numeric(as.character(x)))
  return(Alpha)
}

### AVERAGE ALPHA over Taps ###
SumAlpha <- function(Alpha){
  
sumAlpha <- summarySE(data = Alpha, measurevar = "alpha_lin", groupvars = c("pair","block","tapnr"), na.rm = FALSE, conf.interval = 0.95, .drop = TRUE)

#sumAlphaPair <- summarySE(data = ITI, measurevar = "alpha", groupvars = c("pair"), na.rm = FALSE, conf.interval = 0.95, .drop = TRUE)
return(sumAlpha)

# look for min/max value for plotting range
minMax <- sumAlpha$alpha[which.min(sumAlpha$alpha)]
}

# Sample1: sample both (x,y) from the respective distribution delta(i), delta(i+1)
SampleDelta <- function(Delta){
  
  sampleAll <- c()
  Delta[] <- lapply(Delta, function(x) as.numeric(as.character(x)))
  
  # Sample1: sample both (x,y) from the respective distribution delta(i), delta(i+1)
  for(p in pair_names){
    
    # choose pair 
    DeltaPair <- Delta[Delta$pair==p,]
    sampleTap <- c()
    
    for (i in 1:8) {
      # choose deltas of tap(i) to sample 
      DeltaTap <- DeltaPair[DeltaPair$tapnr==i,]
      # draw 400 samples from this distribution to create new data...
      sampleTap <- rbind(sampleTap, sample_n(DeltaTap, replace = TRUE, length(DeltaPair$tapnr)))
      
    }
    sampleAll <- rbind(sampleAll, sampleTap)
  }
return(sampleAll)
}

# Steady State: only sample from x --> delta(i+1) sampled from delta(i)
SampleSteadyState <- function(Delta){
  
  Delta[] <- lapply(Delta, function(x) as.numeric(as.character(x)))
  SteadyStateAll <- c()
  
  for(p in pair_names){
    
    # choose pair 
    DeltaPair <- Delta[Delta$pair==p,]
    SteadyStateTap <- c()
    s2 <- c()
    
    for (i in 1:8) {
      # choose deltas of tap(i) to sample 
      DeltaTap <- DeltaPair[DeltaPair$tapnr==i,]
      # draw 400 samples from this distribution to create new data...
      SteadyStateTap <- rbind(SteadyStateTap, sample_n(DeltaTap, replace = TRUE, length(DeltaPair$tapnr)))
      # take a new sample 
      s2 <- rbind(s2, sample_n(DeltaTap, replace = TRUE, length(DeltaPair$tapnr)))
      # use samples from delta (x-axis) of the second sample (s2) to simulate delta(i+1) of the first sample
      SteadyStateTap$delta1 <- s2$delta
      
    }
    SteadyStateAll <- rbind(SteadyStateAll, SteadyStateTap)
  }
return(SteadyStateAll)
}

# compute median value for all delta(i) and delta(i+1) sampling methods (simple, steady state, original)
ComputeMedian <- function(sampleAll, SteadyStateAll, Delta){
  
  medianTest <- c()
  for (p in pair_names){
    # separate data frame by pairs
    SimpleSample <-sampleAll[sampleAll$pair==p,]
    SteadyState <-SteadyStateAll[SteadyStateAll$pair==p,]
    SampleOriginal <-Delta[Delta$pair==p,]
    
    #compute median values, ignore grouping-columns (automatically created by aggregate-function)
    Median1 <- aggregate(SimpleSample[, 5:6], list(SimpleSample$tapnr), median)[,2:3]
    Median2 <- aggregate(SteadyState[, 5:6], list(SteadyState$tapnr), median)[,2:3]
    Median3 <- aggregate(SampleOriginal[, 5:6], list(SampleOriginal$tapnr), median)[,2:3]
    medianPair <- cbind(Median1, Median2, Median3)
    medianTest <- rbind(medianTest, medianPair)
  }
  # cretae dataframe with all the median values
  medianTest <- cbind(pair = rep(pair_names, each = 8), tapnr =rep(seq(1:8), times = 8) , medianTest)
  col <- c("pair", "tapnr","simpleSampleD","simpleSampleD1", "SteadyStateD", "SteadyStateD1","OriginalD", "OriginalD1")
  colnames(medianTest) <- col
  
  return(medianTest)
}

# for tap (each pair): compute median, mode and mean value for all delta
# save in Dataframe "MMM"
ComputeMMM <- function(Delta){
  
  MMM <- as_tibble(matrix(ncol=5,nrow=128))
  col <- c("pair", "tapnr", "median","mode", "mean" )
  colnames(MMM) <- col
  MMM$pair <- rep(pair_names, each = 8)
  MMM$tapnr <- rep(seq(1,8), times = 16)

  for (p in pair_names){
    DeltaPair <- Delta[Delta$pair == p,]
    # calculate median and mean via aggregate function: grouping by taps
    MMM[MMM$pair==p,]$median <- aggregate(DeltaPair$delta, by = list(DeltaPair$tapnr), FUN = median)$x
    MMM[MMM$pair==p,]$mean <- aggregate(DeltaPair$delta, by = list(DeltaPair$tapnr), FUN = mean)$x
    # calculate mode by computing location of the peak of the delta-density(highest density of delta values)
    for (t in 1:8){
    MMM[MMM$pair==p & MMM$tapnr==t,]$mode <- density(DeltaPair[DeltaPair$tapnr == t,]$delta)$x[which.max(density(DeltaPair[DeltaPair$tapnr == 5,]$delta)$y)]
    }
  }
  return(MMM)
  
}
