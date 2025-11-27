# Solana Meme Token Risk Radar

Goal: given a Solana token address, compute a transparent risk score based on:

- Holder concentration
- Liquidity depth vs likely trade size
- Token age and basic price volatility

Project structure:

- `src/data/` – data collection from public Solana / DEX APIs
- `src/features/` – compute risk features (concentration, liquidity, volatility)
- `src/models/` – unsupervised risk scoring and clustering
- `data/` – local cache of raw and processed token statistics
- `notebooks/` – EDA, modeling experiments, and visualizations

This is a portfolio project to demonstrate end-to-end data work:
API ingestion, feature engineering, unsupervised modeling, and simple reporting.
