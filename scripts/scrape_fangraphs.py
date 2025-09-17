import requests
from bs4 import BeautifulSoup
import json
import time
import re
from datetime import datetime

class FangraphsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.players = []

    def scrape_brewers_org(self):
        """Scrape all Brewers organization players from Fangraphs"""
        print("Scraping Brewers organization from Fangraphs...")
        
        # Brewers organization levels
        levels = {
            'MLB': 'https://www.fangraphs.com/roster.aspx?teamid=8&season=2025',
            'AAA': 'https://www.fangraphs.com/minorleagues.aspx?pos=all&stats=bat&lg=AAA&qual=0&type=8&season=2025&team=0&players=0',
            'AA': 'https://www.fangraphs.com/minorleagues.aspx?pos=all&stats=bat&lg=AA&qual=0&type=8&season=2025&team=0&players=0',
            'High-A': 'https://www.fangraphs.com/minorleagues.aspx?pos=all&stats=bat&lg=A%2B&qual=0&type=8&season=2025&team=0&players=0',
            'Low-A': 'https://www.fangraphs.com/minorleagues.aspx?pos=all&stats=bat&lg=A&qual=0&type=8&season=2025&team=0&players=0'
        }
        
        for level, url in levels.items():
            try:
                print(f"Scraping {level} level...")
                self.scrape_level(url, level)
                time.sleep(2)  # Be respectful
            except Exception as e:
                print(f"Error scraping {level}: {e}")

    def scrape_level(self, url, level):
        """Scrape a specific level"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'rgMasterTable'})
            
            if not table:
                print(f"No stats table found for {level}")
                return
                
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                try:
                    player_data = self.parse_player_row(row, level)
                    if player_data and 'Brewers' in str(row):  # Filter for Brewers players
                        self.players.append(player_data)
                        print(f"Added {player_data['name']} - {level}")
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"Error scraping level {level}: {e}")

    def parse_player_row(self, row, level):
        """Parse individual player row"""
        try:
            cells = row.find_all('td')
            if len(cells) < 10:
                return None
                
            name = cells[1].get_text(strip=True)
            if not name:
                return None
                
            # Create player ID
            player_id = name.lower().replace(' ', '-').replace('.', '').replace("'", '')
            
            # Extract basic stats
            stats = {
                'avg': self.safe_float(cells[10].get_text(strip=True)) if len(cells) > 10 else 0,
                'hr': self.safe_int(cells[8].get_text(strip=True)) if len(cells) > 8 else 0,
                'rbi': self.safe_int(cells[9].get_text(strip=True)) if len(cells) > 9 else 0,
                'ops': self.safe_float(cells[13].get_text(strip=True)) if len(cells) > 13 else 0
            }
            
            return {
                'id': player_id,
                'name': name,
                'position': cells[2].get_text(strip=True) if len(cells) > 2 else 'OF',
                'age': self.safe_int(cells[3].get_text(strip=True)) if len(cells) > 3 else 0,
                'level': level,
                'currentStats': stats
            }
            
        except Exception as e:
            return None

    def scrape_player_details(self, player_id, player_name):
        """Scrape detailed career stats for a player"""
        try:
            # Search for player on Fangraphs
            search_url = f"https://www.fangraphs.com/players/{player_name.replace(' ', '-').lower()}/stats"
            
            response = self.session.get(search_url, timeout=10)
            time.sleep(1)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find career stats table
            stats_table = soup.find('table', {'class': 'rgMasterTable'})
            if not stats_table:
                return []
                
            career_stats = []
            rows = stats_table.find_all('tr')[1:]
            
            for row in rows:
                try:
                    cells = row.find_all('td')
                    if len(cells) >= 15:
                        season_stats = {
                            'year': self.safe_int(cells[0].get_text(strip=True)),
                            'level': cells[1].get_text(strip=True),
                            'g': self.safe_int(cells[2].get_text(strip=True)),
                            'pa': self.safe_int(cells[3].get_text(strip=True)),
                            'ab': self.safe_int(cells[4].get_text(strip=True)),
                            'h': self.safe_int(cells[5].get_text(strip=True)),
                            'hr': self.safe_int(cells[8].get_text(strip=True)),
                            'rbi': self.safe_int(cells[9].get_text(strip=True)),
                            'avg': self.safe_float(cells[10].get_text(strip=True)),
                            'obp': self.safe_float(cells[11].get_text(strip=True)),
                            'slg': self.safe_float(cells[12].get_text(strip=True)),
                            'ops': self.safe_float(cells[13].get_text(strip=True)),
                            'wrcPlus': self.safe_int(cells[14].get_text(strip=True))
                        }
                        career_stats.append(season_stats)
                except:
                    continue
                    
            return career_stats
            
        except Exception as e:
            print(f"Error scraping details for {player_name}: {e}")
            return []

    def safe_int(self, value):
        try:
            return int(float(str(value).replace(',', '').replace('%', ''))) if value and str(value).strip() != '-' else 0
        except:
            return 0
    
    def safe_float(self, value):
        try:
            return float(str(value).replace(',', '').replace('%', '')) if value and str(value).strip() != '-' else 0.0
        except:
            return 0.0

    def save_data(self):
        """Save scraped data to JSON files"""
        import os
        os.makedirs('data', exist_ok=True)
        
        # Save player list
        with open('data/players.json', 'w') as f:
            json.dump(self.players, f, indent=2)
        
        print(f"Saved {len(self.players)} players to data/players.json")
        
        # Save individual player files with detailed stats
        for player in self.players:
            try:
                detailed_stats = self.scrape_player_details(player['id'], player['name'])
                if detailed_stats:
                    player_data = {
                        **player,
                        'careerStats': detailed_stats
                    }
                    
                    with open(f"data/player_{player['id']}.json", 'w') as f:
                        json.dump(player_data, f, indent=2)
                        
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error saving detailed stats for {player['name']}: {e}")

def main():
    scraper = FangraphsScraper()
    scraper.scrape_brewers_org()
    scraper.save_data()
    print("✅ Scraping complete!")

if __name__ == "__main__":
    main()
