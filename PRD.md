# Crypto Discovery Bot - Product Requirements Document

## Overview
The Crypto Discovery Bot discovers promising new cryptocurrency tokens, evaluates them based on key metrics, and shares findings via Twitter. The system focuses on identifying early-stage opportunities with growth potential while minimizing rug pull risk.

## Core User Flow

1. **Discovery**: Bot scans DexScreener for tokens created in the last 24 hours
2. **Initial Evaluation**: Bot analyzes on-chain metrics to filter out high-risk tokens
3. **Social Research**: For promising tokens, bot checks Twitter sentiment
4. **Content Creation**: Bot generates and posts tweets about approved tokens
5. **Monitoring**: Bot tracks performance of featured tokens and tweet engagement

## System Architecture

### 1. Token Discovery Module
- **DexScreener Integration**
  - Connect to DexScreener API to monitor new token pairs
  - Filter tokens created within the last 24-72 hours
  - Focus on popular chains (Ethereum, BSC, Solana)
  
- **Data Collection**
  - Basic token information (name, symbol, address)
  - Key metrics (liquidity, volume, price change)
  - Transaction patterns (buys vs. sells)

### 2. Database Schema

**Tokens Table**
```
{
  id: UUID (primary key),
  name: String,
  symbol: String,
  contractAddress: String (unique),
  chainId: Integer,
  pairAddress: String,
  baseToken: String,
  quoteToken: String,
  
  // Discovery data
  createdAt: DateTime,
  discoveredAt: DateTime,
  
  // Key metrics
  initialPrice: Decimal,
  currentPrice: Decimal,
  initialLiquidity: Decimal,
  currentLiquidity: Decimal,
  volume24h: Decimal,
  priceChange24h: Decimal,
  marketCap: Decimal,
  fdv: Decimal,
  
  // Evaluation data
  status: Enum ['discovered', 'pending', 'approved', 'rejected', 'tweeted'],
  technicalScore: Decimal,
  socialScore: Decimal,
  riskScore: Decimal,
  
  // Additional info
  holderCount: Integer,
  buyCount24h: Integer,
  sellCount24h: Integer,
  uniqueBuyers24h: Integer,
  uniqueSellers24h: Integer,
  
  // Metadata
  socialLinks: JSON,
  lastUpdated: DateTime
}
```

**SocialData Table**
```
{
  id: UUID (primary key),
  tokenId: UUID (foreign key),
  platform: Enum ['twitter', 'telegram', 'discord'],
  timestamp: DateTime,
  mentionCount: Integer,
  sentimentScore: Decimal,
  influencerMentions: Integer,
  relevantPosts: JSON
}
```

**Tweets Table**
```
{
  id: UUID (primary key),
  tokenId: UUID (foreign key),
  tweetId: String,
  content: String,
  postedAt: DateTime,
  impressions: Integer,
  likes: Integer,
  retweets: Integer,
  replies: Integer
}
```

**PriceSnapshots Table**
```
{
  id: UUID (primary key),
  tokenId: UUID (foreign key),
  timestamp: DateTime,
  price: Decimal,
  liquidity: Decimal,
  volume24h: Decimal,
  marketCap: Decimal
}
```

### 3. Evaluation Engine
- **Technical Analysis**
  - Liquidity check (target: $10K+ minimum)
  - Transaction pattern analysis (buy/sell ratio)
  - Price momentum assessment
  
- **Risk Assessment**
  - Red flags detection:
    - Low liquidity with high FDV
    - Suspicious transaction patterns
    - Extreme concentration in few wallets
  
- **Decision Logic**
  - Simple scoring system (0-100) for each token
  - Threshold-based approval process
  - Automatic rejection for high-risk indicators

### 4. Social Media Integration
- **Twitter Research**
  - Search for token mentions
  - Basic sentiment analysis
  - Engagement metrics collection
  
- **Content Generation**
  - Template-based tweet creation
  - Key metrics inclusion
  - Appropriate disclaimers

### 5. Monitoring System
- **Token Tracking**
  - Hourly price and liquidity snapshots
  - Performance tracking post-tweet
  
- **Tweet Analytics**
  - Engagement metrics collection
  - Performance comparison across tokens

## Implementation Approach

### Phase 1: MVP (Current Focus)
- Basic DexScreener integration for token discovery
- Simple evaluation based on key metrics
- Twitter search for social validation
- Manual review before tweeting
- Basic database implementation

### Phase 2: Automation
- Fully automated evaluation process
- Improved social media analysis
- Scheduled tweet posting
- Performance tracking dashboard

### Phase 3: Advanced Features
- Multi-chain support
- Advanced risk detection
- ML-based token evaluation
- Community feedback integration

## Success Metrics
- Number of tokens discovered daily
- Percentage of tokens showing positive returns after featuring
- Twitter engagement metrics
- Follower growth rate

## MVP for today
* Find a new coin on DexScreener (created < 1 day ago)
* Store basic coin data in database
* Evaluate coin based on simple metrics
* If promising, search Twitter for mentions
* If social validation exists, compose and post tweet

