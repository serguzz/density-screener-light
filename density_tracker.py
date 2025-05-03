from rich.console import Console
from rich.table import Table
from rich.style import Style
from IPython.display import clear_output
from datetime import datetime
import time


# Main Density Tracking Class
class DensityTracker:
    def __init__(self, exchange, db_manager, value_thresholds, display_price_threshold=0.05, display_detected_threshold=10):
        self.exchange = exchange
        self.db_manager = db_manager
        self.value_thresholds = value_thresholds
        self.display_price_threshold = display_price_threshold
        self.display_detected_threshold = display_detected_threshold
        # self.price_range_threshold = price_range_threshold  # obsolete - used before I started deeper Order Book fetching 

    def _process_pair_density(self, pair):
        """Process densities for a single pair."""
        # session = self.db_manager.Session()
        value_threshold = self.value_thresholds.get(pair.split('/')[0], 
                                                    self.value_thresholds['default'])

        # Fetch order book
        try:
            order_book = self.exchange.fetch_order_book(pair, limit=1000)
        except Exception as e:
            print(f"Error {e} occured while fetching Order Book for {pair}")
            return
        asks = order_book['asks']
        bids = order_book['bids']

        # max_ask_price = asks[-1][0] if asks else float('inf')
        min_ask_price = asks[0][0] if asks else 0
        max_bid_price = bids[0][0] if bids else float('inf')
        # min_bid_price = bids[-1][0] if bids else 0

        # Identify new densities in the order book
        new_densities = []
        for price, size in asks:
            worth = price * size
            if worth > value_threshold:
                new_densities.append({
                    "pair": pair,
                    "side": 'Ask',
                    "price": price,
                    "size": size,
                    "worth": worth,
                    "spread_price": min_ask_price
                })

        for price, size in bids:
            worth = price * size
            if worth > value_threshold:
                new_densities.append({
                    "pair": pair,
                    "side": 'Bid',
                    "price": price,
                    "size": size,
                    "worth": worth,
                    "spread_price": max_bid_price
                })

        # Fetch old densities for the pair from DB
        old_densities = self.db_manager.fetch_densities(pair)

        # Step 4: Compare old densities with new densities
        for old_density in old_densities:
            old_price = old_density.price
            old_side = old_density.side
            # old_worth = old_density.worth
            # old_spread_price = old_density.spread_price
            
            # Update existing densities
            matching_new_density = next(
                (d for d in new_densities 
                 if d["price"] == old_price and d["side"] == old_side), 
                None
            )
            if matching_new_density:
                self.db_manager.update_density(
                    old_density,
                    matching_new_density["side"],
                    matching_new_density["size"],
                    matching_new_density["worth"],
                    matching_new_density["spread_price"]
                )
                new_densities.remove(matching_new_density)
                continue
            
            # Remove densities not matching any condition
            self.db_manager.delete_density(old_density)

        # Add new densities that didn't match any old density
        for new_density in new_densities:
            self.db_manager.add_density(
                pair=new_density["pair"],
                side=new_density["side"],
                price=new_density["price"],
                size=new_density["size"],
                worth=new_density["worth"],
                spread_price=new_density["spread_price"]
            )

        # session.close()

    def display_all_densities(self):
        """Display all densities in a table."""

        console = Console()

        # Define background styles for highlighting
        ask_highlight_style = Style(bgcolor="#ffe4e1")  # Light red background for "Ask"
        bid_highlight_style = Style(bgcolor="#f0fff0")  # Light green background for "Bid"

        # TODO: Highlight densities < 1.5% and older than 30 mins
        
        display_price_threshold = self.display_price_threshold   # show only debsities within 5% from current price
        display_detected_threshold = self.display_detected_threshold  # minimum minutes to show the density

        # session = self.db_manager.Session()
        try:
            # densities = session.query(Density).order_by(Density.pair.asc(), Density.price.desc()).all()
            densities = self.db_manager.fetch_densities()
            # Create a Rich table
            table = Table(title="Spot and Futures Densities", show_header=True, header_style="bold magenta")
            
            # Add columns to the table
            table.add_column("Pair", justify="center")
            table.add_column("Side", justify="center")
            table.add_column("Price", justify="right")
            table.add_column("Size", justify="right")
            table.add_column("Worth ($)", justify="right")
            table.add_column("Distance (%)", justify="right")
            table.add_column("Detected", justify="right")
            
            # Add rows to the table
            for density in densities:
                distance = (density.price - density.spread_price) / density.spread_price
                # Show only rows that are not very far, e.g., 5% distance from the price
                if abs(distance) <= display_price_threshold:
                
                    # Calculate the relative time for the "detected" column
                    time_difference = datetime.utcnow() - density.timestamp
                    total_minutes = int(time_difference.total_seconds() // 60)
                    # Show only densities that are detected at least 10 mins ago
                    if total_minutes >= display_detected_threshold:
                        hours, minutes = divmod(total_minutes, 60)
                        
                        if hours > 0:
                            relative_time = f"{hours}h {minutes}m" if minutes > 0 else f"{hours}h"
                        else:
                            relative_time = f"{minutes}m" if minutes > 0 else "now"
                    
                        row_style = None
                        # Highlight rows that are older than 30 minutes
                        highlight = total_minutes >= 30
                        if highlight:
                            row_style = ask_highlight_style if density.side == "Ask" else bid_highlight_style
        
                        # Add row to the table with appropriate styles
                        table.add_row(
                            density.pair,  # Pair
                            density.side,  # Side
                            f"{density.price:,.4f}",  # Price
                            f"{density.size:,.0f}",  # Size
                            f"{int(round(density.worth / 50000) * 50000 // 1000)}k",  # Worth
                            f"{distance * 100:,.2f}%",  # Distance
                            relative_time,  # Relative Detected time
                            style=row_style,
                        )            
            # Display the Rich table
            console.print(table)
        except Exception as e:
            print(f"Error displaying densities: {e}")
        finally:
            # session.close()
            pass

    def send_telegram_alert(self):
        densities = self.db_manager.fetch_densities()
        for density in densities:
            if density.detected > "older_than_two_hours" and abs(density.spread_price - density.price) / density.price < 0.01:
                # TODO: send_alert_to_telegram_channel
                pass
    
    def run(self, pairs, display=True, telegram_alert=False):
        """Process densities for all pairs and display results."""
        try:
            while True:  # Infinite loop to fetch data repeatedly                
                if display:
                    # Display all densities           
                    # Clear previous output in the notebook cell
                    clear_output(wait=True)
                    time.sleep(1)
                    self.display_all_densities()
                for pair in pairs:
                    self._process_pair_density(pair)
                if telegram_alert:
                    # TODO: send telegram alerts
                    self.seld_telegram_alert()
                    pass
        except KeyboardInterrupt:
            print("\nProcess interrupted. Exiting...")