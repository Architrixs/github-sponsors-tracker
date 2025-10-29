import json
import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

def load_data(json_path):
    """Load the sponsors data from JSON file."""
    with open(json_path, 'r') as f:
        data = json.load(f)
    # Support both main data.json and per-strategy files
    sponsors_key = 'sponsors' if 'sponsors' in data else 'sponsors'
    sponsors = data.get(sponsors_key, data)
    # When file is main data.json, data['sponsors'] is list; when per-strategy, structure also has 'sponsors'
    return pd.DataFrame(sponsors)

def analyze_top_sponsored(df, top_n=100):
    """Analyze characteristics of top sponsored users."""
    top_users = df.nlargest(top_n, 'sponsorships_count')
    
    print(f"\n{'='*60}")
    print(f"ANALYSIS OF TOP {top_n} SPONSORED USERS")
    print(f"{'='*60}\n")
    
    # Basic statistics
    print("📊 BASIC STATISTICS:")
    print(f"   Average sponsors: {top_users['sponsorships_count'].mean():.2f}")
    print(f"   Median sponsors: {top_users['sponsorships_count'].median():.2f}")
    print(f"   Max sponsors: {top_users['sponsorships_count'].max()}")
    print(f"   Min sponsors (in top {top_n}): {top_users['sponsorships_count'].min()}")
    
    # Follower analysis
    print(f"\n👥 FOLLOWER ANALYSIS:")
    followers_bins = [0, 1000, 2000, 5000, 10000, float('inf')]
    followers_labels = ['<1K', '1K-2K', '2K-5K', '5K-10K', '10K+']
    top_users['follower_bin'] = pd.cut(top_users['followers'], bins=followers_bins, labels=followers_labels)
    print(top_users['follower_bin'].value_counts().sort_index())
    
    # Common follower threshold
    for threshold in [500, 1000, 2000, 5000]:
        pct = (top_users['followers'] > threshold).sum() / len(top_users) * 100
        print(f"   {pct:.1f}% have >={threshold} followers")
    
    # Repository analysis
    print(f"\n📦 REPOSITORY ANALYSIS:")
    repos_bins = [0, 20, 50, 100, 200, float('inf')]
    repos_labels = ['<20', '20-50', '50-100', '100-200', '200+']
    top_users['repos_bin'] = pd.cut(top_users['public_repos'], bins=repos_bins, labels=repos_labels)
    print(top_users['repos_bin'].value_counts().sort_index())
    
    for threshold in [20, 50, 100]:
        pct = (top_users['public_repos'] > threshold).sum() / len(top_users) * 100
        print(f"   {pct:.1f}% have >{threshold} repos")
    
    # Conversion rate analysis
    print(f"\n💰 CONVERSION RATE ANALYSIS:")
    print(f"   Average conversion rate: {top_users['sponsor_conversion_rate'].mean():.2f}%")
    print(f"   Median conversion rate: {top_users['sponsor_conversion_rate'].median():.2f}%")
    print(f"   Max conversion rate: {top_users['sponsor_conversion_rate'].max():.2f}%")
    
    # GitHub Stars
    stars_count = top_users['is_github_star'].sum()
    print(f"\n⭐ GITHUB STARS:")
    print(f"   {stars_count} ({stars_count/len(top_users)*100:.1f}%) are GitHub Stars")
    
    # Account age
    top_users['account_age_years'] = (pd.Timestamp.now() - pd.to_datetime(top_users['created_at'])).dt.days / 365.25
    print(f"\n📅 ACCOUNT AGE:")
    print(f"   Average age: {top_users['account_age_years'].mean():.1f} years")
    print(f"   Median age: {top_users['account_age_years'].median():.1f} years")
    
    # Sponsoring activity (how many they sponsor)
    print(f"\n🤝 SPONSORING ACTIVITY:")
    sponsors_others = (top_users['sponsoring_count'] > 0).sum()
    print(f"   {sponsors_others} ({sponsors_others/len(top_users)*100:.1f}%) also sponsor others")
    print(f"   Average sponsoring: {top_users['sponsoring_count'].mean():.1f} projects/users")
    
    return top_users

def create_visualizations(df, output_dir='analysis_plots'):
    """Create comprehensive visualizations."""
    Path(output_dir).mkdir(exist_ok=True)
    
    # 1. Sponsors vs Followers (scatter)
    plt.figure(figsize=(12, 8))
    plt.scatter(df['followers'], df['sponsorships_count'], alpha=0.5, s=50)
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Followers (log scale)', fontsize=12)
    plt.ylabel('Number of Sponsors (log scale)', fontsize=12)
    plt.title('Relationship: Followers vs Sponsors', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    # Add correlation
    correlation = df['followers'].corr(df['sponsorships_count'])
    plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
             transform=plt.gca().transAxes, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/followers_vs_sponsors.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: followers_vs_sponsors.png")
    plt.close()
    
    # 2. Repos vs Sponsors (scatter)
    plt.figure(figsize=(12, 8))
    plt.scatter(df['public_repos'], df['sponsorships_count'], alpha=0.5, s=50, color='green')
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Public Repositories (log scale)', fontsize=12)
    plt.ylabel('Number of Sponsors (log scale)', fontsize=12)
    plt.title('Relationship: Public Repos vs Sponsors', fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    
    correlation = df['public_repos'].corr(df['sponsorships_count'])
    plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
             transform=plt.gca().transAxes, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/repos_vs_sponsors.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: repos_vs_sponsors.png")
    plt.close()
    
    # 3. Conversion Rate Distribution
    plt.figure(figsize=(12, 8))
    plt.hist(df['sponsor_conversion_rate'], bins=50, edgecolor='black', alpha=0.7)
    plt.xlabel('Sponsor Conversion Rate (%)', fontsize=12)
    plt.ylabel('Number of Users', fontsize=12)
    plt.title('Distribution of Sponsor Conversion Rates', fontsize=14, fontweight='bold')
    plt.axvline(df['sponsor_conversion_rate'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: {df["sponsor_conversion_rate"].mean():.2f}%')
    plt.axvline(df['sponsor_conversion_rate'].median(), color='orange', linestyle='--', 
                linewidth=2, label=f'Median: {df["sponsor_conversion_rate"].median():.2f}%')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/conversion_rate_distribution.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: conversion_rate_distribution.png")
    plt.close()
    
    # 4. Top 20 Most Sponsored Users
    top_20 = df.nlargest(20, 'sponsorships_count')
    plt.figure(figsize=(14, 10))
    y_pos = np.arange(len(top_20))
    plt.barh(y_pos, top_20['sponsorships_count'], color='skyblue', edgecolor='black')
    plt.yticks(y_pos, top_20['login'])
    plt.xlabel('Number of Sponsors', fontsize=12)
    plt.title('Top 20 Most Sponsored Users', fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/top_20_sponsored.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: top_20_sponsored.png")
    plt.close()
    
    # 5. Heatmap: Follower bins vs Repo bins
    df['follower_bin'] = pd.cut(df['followers'], bins=[0, 1000, 2000, 5000, 10000, float('inf')],
                                  labels=['<1K', '1K-2K', '2K-5K', '5K-10K', '10K+'])
    df['repos_bin'] = pd.cut(df['public_repos'], bins=[0, 20, 50, 100, 200, float('inf')],
                              labels=['<20', '20-50', '50-100', '100-200', '200+'])
    
    heatmap_data = df.groupby(['follower_bin', 'repos_bin'])['sponsorships_count'].mean().unstack()
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt='.0f', cmap='YlOrRd', cbar_kws={'label': 'Avg Sponsors'})
    plt.xlabel('Repository Count', fontsize=12)
    plt.ylabel('Follower Count', fontsize=12)
    plt.title('Average Sponsors by Follower & Repo Count', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(f'{output_dir}/heatmap_followers_repos.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: heatmap_followers_repos.png")
    plt.close()
    
    # 6. GitHub Stars comparison
    plt.figure(figsize=(10, 6))
    stars_comparison = df.groupby('is_github_star')['sponsorships_count'].agg(['mean', 'median'])
    x = ['Not GitHub Star', 'GitHub Star']
    width = 0.35
    x_pos = np.arange(len(x))
    
    plt.bar(x_pos - width/2, stars_comparison['mean'], width, label='Mean', color='blue', alpha=0.7)
    plt.bar(x_pos + width/2, stars_comparison['median'], width, label='Median', color='orange', alpha=0.7)
    
    plt.xlabel('GitHub Star Status', fontsize=12)
    plt.ylabel('Number of Sponsors', fontsize=12)
    plt.title('Sponsor Count: GitHub Stars vs Non-Stars', fontsize=14, fontweight='bold')
    plt.xticks(x_pos, x)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f'{output_dir}/github_stars_comparison.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: github_stars_comparison.png")
    plt.close()
    
    # 7. Account Age vs Sponsors
    df['account_age_years'] = (pd.Timestamp.now() - pd.to_datetime(df['created_at'])).dt.days / 365.25
    
    plt.figure(figsize=(12, 8))
    plt.scatter(df['account_age_years'], df['sponsorships_count'], alpha=0.5, s=50, color='purple')
    plt.xlabel('Account Age (years)', fontsize=12)
    plt.ylabel('Number of Sponsors', fontsize=12)
    plt.title('Relationship: Account Age vs Sponsors', fontsize=14, fontweight='bold')
    plt.yscale('log')
    plt.grid(True, alpha=0.3)
    
    correlation = df['account_age_years'].corr(df['sponsorships_count'])
    plt.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
             transform=plt.gca().transAxes, fontsize=12, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='plum', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/account_age_vs_sponsors.png', dpi=300, bbox_inches='tight')
    print(f"✅ Saved: account_age_vs_sponsors.png")
    plt.close()

def find_common_criteria(df, top_n=100):
    """Find common criteria among top sponsored users."""
    top_users = df.nlargest(top_n, 'sponsorships_count')
    
    print(f"\n{'='*60}")
    print(f"COMMON CRITERIA FOR TOP {top_n} SPONSORED USERS")
    print(f"{'='*60}\n")
    
    criteria = []
    
    # Check various thresholds
    thresholds = {
        'followers': [500, 1000, 2000, 5000],
        'public_repos': [20, 50, 100, 200],
        'account_age_years': [1, 2, 5, 10]
    }
    
    top_users['account_age_years'] = (pd.Timestamp.now() - pd.to_datetime(top_users['created_at'])).dt.days / 365.25
    
    print("🎯 THRESHOLD ANALYSIS:")
    print("\nFollowers:")
    for threshold in thresholds['followers']:
        pct = (top_users['followers'] >= threshold).sum() / len(top_users) * 100
        print(f"   >={threshold:5d}: {pct:5.1f}% of top {top_n}")
        if pct >= 90:
            criteria.append(f"followers >= {threshold}")
    
    print("\nPublic Repos:")
    for threshold in thresholds['public_repos']:
        pct = (top_users['public_repos'] >= threshold).sum() / len(top_users) * 100
        print(f"   >={threshold:3d}: {pct:5.1f}% of top {top_n}")
        if pct >= 90:
            criteria.append(f"public_repos >= {threshold}")
    
    print("\nAccount Age:")
    for threshold in thresholds['account_age_years']:
        pct = (top_users['account_age_years'] >= threshold).sum() / len(top_users) * 100
        print(f"   >={threshold:2d} years: {pct:5.1f}% of top {top_n}")
        if pct >= 90:
            criteria.append(f"account_age >= {threshold} years")
    
    # Conversion rate
    print(f"\n💰 CONVERSION RATE:")
    conv_thresholds = [1, 5, 10, 20]
    for threshold in conv_thresholds:
        pct = (top_users['sponsor_conversion_rate'] >= threshold).sum() / len(top_users) * 100
        print(f"   >={threshold:2d}%: {pct:5.1f}% of top {top_n}")
    
    # Summary
    print(f"\n✨ COMMON CRITERIA (>90% of top {top_n}):")
    if criteria:
        for c in criteria:
            print(f"   ✓ {c}")
    else:
        print("   No single criterion covers 90%+ of top users")
        print("   This suggests diverse paths to high sponsorship!")
    
    return criteria

def main():
    """Main analysis function with optional per-strategy comparison."""
    parser = argparse.ArgumentParser(description="Analyze GitHub Sponsors data")
    parser.add_argument("--input", "-i", type=str, nargs="*", help="Path(s) to JSON data files to analyze")
    parser.add_argument("--strategies", action="store_true", help="Analyze all per-strategy files under frontend/public/strategies")
    parser.add_argument("--top", type=int, default=100, help="Top N users to analyze")
    parser.add_argument("--no-plots", action="store_true", help="Skip generating plots")
    args = parser.parse_args()

    def analyze_one(path: Path, label: str):
        print(f"\n{'='*60}")
        print(f"Analyzing: {label}")
        print(f"Path: {path}")
        print(f"{'='*60}")
        df_local = load_data(path)
        print(f"✅ Loaded {len(df_local)} records")
        analyze_top_sponsored(df_local, top_n=args.top)
        find_common_criteria(df_local, top_n=args.top)
        if not args.no_plots:
            create_visualizations(df_local, output_dir=f"analysis_plots/{label}")

    if args.input:
        for p in args.input:
            analyze_one(Path(p), label=Path(p).stem)
        print("\n✅ Analysis complete for provided files.")
        return

    if args.strategies:
        strat_dir = Path(__file__).parent.parent / "frontend" / "public" / "strategies"
        if not strat_dir.exists():
            print(f"❌ Strategies directory not found at {strat_dir}")
            print("   Run scraper.py first to generate per-strategy files.")
            return
        files = sorted(strat_dir.glob("strategy_*.json"))
        if not files:
            print("❌ No per-strategy files found. Run scraper.py to generate them.")
            return
        for f in files:
            analyze_one(f, label=f.stem)
        print("\n✅ Analysis complete for all strategies.")
        return

    # Default: analyze the main aggregated data.json
    data_path = Path(__file__).parent.parent / "frontend" / "public" / "data.json"
    if not data_path.exists():
        print(f"❌ Error: Data file not found at {data_path}")
        print("   Please run scraper.py first!")
        return
    print("📂 Loading data...")
    df = load_data(data_path)
    print(f"✅ Loaded {len(df)} sponsored users\n")
    analyze_top_sponsored(df, top_n=args.top)
    find_common_criteria(df, top_n=args.top)
    if not args.no_plots:
        print(f"\n{'='*60}")
        print("CREATING VISUALIZATIONS")
        print(f"{'='*60}\n")
        create_visualizations(df)
        print(f"\n{'='*60}")
        print("✅ ANALYSIS COMPLETE!")
        print(f"{'='*60}")
        print(f"📊 Plots saved in: analysis_plots/")
        print(f"📈 Generated {7} visualization files")

if __name__ == "__main__":
    main()