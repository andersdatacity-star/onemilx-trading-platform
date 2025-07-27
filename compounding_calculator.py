import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json

class AdvancedCompoundCalculator:
    def __init__(self, initial_capital: float = 1000):
        self.initial_capital = initial_capital
        self.scenarios = {}
        
    def calculate_compound_growth(self, 
                                initial_capital: float,
                                daily_return: float,
                                days: int,
                                monthly_deposit: float = 0,
                                volatility: float = 0) -> pd.DataFrame:
        """
        Calculate compound growth with optional monthly deposits and volatility
        
        Args:
            initial_capital: Starting capital
            daily_return: Expected daily return (as decimal)
            days: Number of days to simulate
            monthly_deposit: Monthly deposit amount
            volatility: Daily volatility (standard deviation of returns)
        """
        
        dates = pd.date_range(start=datetime.now(), periods=days, freq='D')
        capital = [initial_capital]
        daily_returns = []
        
        for i in range(1, days):
            # Add volatility to daily return
            actual_return = daily_return + np.random.normal(0, volatility)
            
            # Calculate new capital
            new_capital = capital[-1] * (1 + actual_return)
            
            # Add monthly deposit (every 30 days)
            if i % 30 == 0:
                new_capital += monthly_deposit
            
            capital.append(new_capital)
            daily_returns.append(actual_return)
        
        df = pd.DataFrame({
            'date': dates,
            'capital': capital,
            'daily_return': [0] + daily_returns,
            'cumulative_return': [(c - initial_capital) / initial_capital for c in capital]
        })
        
        return df
    
    def run_scenario(self, 
                    scenario_name: str,
                    daily_return: float,
                    days: int = 365,
                    monthly_deposit: float = 0,
                    volatility: float = 0) -> dict:
        """Run a specific scenario and store results"""
        
        df = self.calculate_compound_growth(
            self.initial_capital,
            daily_return,
            days,
            monthly_deposit,
            volatility
        )
        
        # Calculate key metrics
        final_capital = df['capital'].iloc[-1]
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        max_drawdown = self.calculate_max_drawdown(df['capital'])
        sharpe_ratio = self.calculate_sharpe_ratio(df['daily_return'])
        
        scenario_results = {
            'data': df,
            'final_capital': final_capital,
            'total_return': total_return,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'parameters': {
                'daily_return': daily_return,
                'days': days,
                'monthly_deposit': monthly_deposit,
                'volatility': volatility
            }
        }
        
        self.scenarios[scenario_name] = scenario_results
        return scenario_results
    
    def calculate_max_drawdown(self, capital_series: pd.Series) -> float:
        """Calculate maximum drawdown"""
        peak = capital_series.expanding().max()
        drawdown = (capital_series - peak) / peak
        return drawdown.min()
    
    def calculate_sharpe_ratio(self, returns: pd.Series) -> float:
        """Calculate Sharpe ratio"""
        if len(returns) < 2:
            return 0
        
        # Remove first element (which is 0)
        returns = returns[1:]
        
        if returns.std() == 0:
            return 0
        
        return returns.mean() / returns.std() * np.sqrt(252)  # Annualized
    
    def run_whale_trap_scenarios(self) -> dict:
        """Run realistic Whale Trap strategy scenarios"""
        
        scenarios = {
            'Conservative': {
                'daily_return': 0.005,  # 0.5% daily
                'volatility': 0.02,     # 2% daily volatility
                'monthly_deposit': 100
            },
            'Moderate': {
                'daily_return': 0.01,   # 1% daily
                'volatility': 0.03,     # 3% daily volatility
                'monthly_deposit': 200
            },
            'Aggressive': {
                'daily_return': 0.015,  # 1.5% daily
                'volatility': 0.04,     # 4% daily volatility
                'monthly_deposit': 300
            },
            'Ultra': {
                'daily_return': 0.02,   # 2% daily
                'volatility': 0.05,     # 5% daily volatility
                'monthly_deposit': 500
            }
        }
        
        results = {}
        for name, params in scenarios.items():
            results[name] = self.run_scenario(
                name,
                params['daily_return'],
                365,  # 1 year
                params['monthly_deposit'],
                params['volatility']
            )
        
        return results
    
    def generate_report(self) -> str:
        """Generate a comprehensive report of all scenarios"""
        
        if not self.scenarios:
            return "No scenarios have been run yet."
        
        report = f"""
# OneMilX Trading Platform - Compounding Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Initial Capital: ${self.initial_capital:,.2f}

## Scenario Results:
"""
        
        for scenario_name, results in self.scenarios.items():
            params = results['parameters']
            report += f"""
### {scenario_name} Strategy
- **Daily Return**: {params['daily_return']*100:.2f}%
- **Volatility**: {params['volatility']*100:.2f}%
- **Monthly Deposit**: ${params['monthly_deposit']:,.2f}
- **Final Capital**: ${results['final_capital']:,.2f}
- **Total Return**: {results['total_return']*100:.2f}%
- **Max Drawdown**: {results['max_drawdown']*100:.2f}%
- **Sharpe Ratio**: {results['sharpe_ratio']:.2f}
"""
        
        return report
    
    def plot_scenarios(self, save_path: str = None):
        """Plot all scenarios for comparison"""
        
        if not self.scenarios:
            print("No scenarios to plot")
            return
        
        plt.figure(figsize=(15, 10))
        
        # Capital growth plot
        plt.subplot(2, 2, 1)
        for name, results in self.scenarios.items():
            plt.plot(results['data']['date'], results['data']['capital'], 
                    label=name, linewidth=2)
        
        plt.title('Capital Growth Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Capital ($)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Returns comparison
        plt.subplot(2, 2, 2)
        scenario_names = list(self.scenarios.keys())
        final_capitals = [results['final_capital'] for results in self.scenarios.values()]
        
        bars = plt.bar(scenario_names, final_capitals, 
                      color=['#667eea', '#764ba2', '#f093fb', '#f5576c'])
        plt.title('Final Capital by Scenario', fontsize=14, fontweight='bold')
        plt.ylabel('Final Capital ($)')
        
        # Add value labels on bars
        for bar, value in zip(bars, final_capitals):
            plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(final_capitals)*0.01,
                    f'${value:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        # Risk metrics
        plt.subplot(2, 2, 3)
        max_drawdowns = [results['max_drawdown']*100 for results in self.scenarios.values()]
        sharpe_ratios = [results['sharpe_ratio'] for results in self.scenarios.values()]
        
        x = np.arange(len(scenario_names))
        width = 0.35
        
        plt.bar(x - width/2, max_drawdowns, width, label='Max Drawdown (%)', color='#ff6b6b')
        plt.bar(x + width/2, sharpe_ratios, width, label='Sharpe Ratio', color='#4ecdc4')
        
        plt.title('Risk Metrics', fontsize=14, fontweight='bold')
        plt.xlabel('Scenario')
        plt.ylabel('Value')
        plt.xticks(x, scenario_names)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Monthly growth rate
        plt.subplot(2, 2, 4)
        for name, results in self.scenarios.items():
            monthly_returns = results['data']['capital'].resample('M').last().pct_change()
            plt.plot(monthly_returns.index, monthly_returns.values, 
                    label=name, marker='o', markersize=4)
        
        plt.title('Monthly Growth Rates', fontsize=14, fontweight='bold')
        plt.xlabel('Month')
        plt.ylabel('Monthly Return (%)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        
        plt.show()
    
    def export_results(self, filename: str = 'compounding_results.json'):
        """Export results to JSON file"""
        
        export_data = {
            'initial_capital': self.initial_capital,
            'generated_at': datetime.now().isoformat(),
            'scenarios': {}
        }
        
        for name, results in self.scenarios.items():
            export_data['scenarios'][name] = {
                'final_capital': results['final_capital'],
                'total_return': results['total_return'],
                'max_drawdown': results['max_drawdown'],
                'sharpe_ratio': results['sharpe_ratio'],
                'parameters': results['parameters'],
                'data': results['data'].to_dict('records')
            }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"Results exported to {filename}")

def main():
    """Example usage of the Advanced Compound Calculator"""
    
    # Initialize calculator
    calculator = AdvancedCompoundCalculator(initial_capital=1000)
    
    # Run Whale Trap scenarios
    print("Running Whale Trap strategy scenarios...")
    results = calculator.run_whale_trap_scenarios()
    
    # Generate and print report
    report = calculator.generate_report()
    print(report)
    
    # Plot results
    calculator.plot_scenarios('whale_trap_analysis.png')
    
    # Export results
    calculator.export_results('whale_trap_results.json')
    
    # Example of custom scenario
    print("\nRunning custom scenario...")
    custom_result = calculator.run_scenario(
        "Custom Strategy",
        daily_return=0.008,  # 0.8% daily
        days=180,            # 6 months
        monthly_deposit=150,
        volatility=0.025     # 2.5% daily volatility
    )
    
    print(f"Custom scenario final capital: ${custom_result['final_capital']:,.2f}")
    print(f"Total return: {custom_result['total_return']*100:.2f}%")

if __name__ == "__main__":
    main() 