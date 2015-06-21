#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2

# Database constants
TABLE_PLAYERS = "Players"
TABLE_MATCHES = "Matches"
VIEW_STANDINGS = "Standings"
COL = {
  "ID"     : "id",
  "NAME"   : "name",
  "P1"     : "p1",
  "P2"     : "p2",
  "WINNER": "winner",
  "WINS"   : "wins",
  "TOTAL"  : "total"
}

class Connection:
    """Provides handful operations and destroys DB connection automatically"""

    def __init__(self):
        """Constructor to create an initial connection"""
        self.conn = self.connect()

    def connect(self):
        """Connect to the PostgreSQL database.  Returns a database connection."""
        return psycopg2.connect("dbname=tournament")

    def execute(self, query, args = None, update = False):
        """Executes the query and closes the connection
        
        Args:
          query : SQL query to be executed
          args  : (Optional) arguments in the query for prepared statements if there is any
          update: Set to True if it is an update operation and it needs to be committed
        """
        cur = self.conn.cursor()

        # call execute function depending on args
        if args:
            cur.execute(query, args)
        else:
            cur.execute(query)

        # commit the changes if it is an update operation
        if update:
            self.conn.commit()

        return cur

    def __del__(self):
        """Destructor to destroy the created connection"""
        self.conn.close()

# init a connection object to run the queries
conn = Connection()

def deleteMatches():
    """Remove all the match records from the database."""
    return conn.execute("DELETE FROM %s" % TABLE_MATCHES, update=True)

def deletePlayers():
    """Remove all the player records from the database."""
    return conn.execute("DELETE FROM %s" % TABLE_PLAYERS, update=True)


def countPlayers():
    """Returns the number of players currently registered."""
    return conn.execute("SELECT COUNT(*) FROM %s" % TABLE_PLAYERS).fetchone()[0]

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    return conn.execute("INSERT INTO {0} ({1}) VALUES (%s)".format(TABLE_PLAYERS, COL["NAME"]), [name], update=True)


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    return conn.execute("SELECT * FROM %s ORDER BY %s" % (VIEW_STANDINGS, COL["WINS"])).fetchall()


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    qry = "INSERT INTO {matches} ({p1},{p2},{winner}) VALUES (%s,%s, %s)".format(matches=TABLE_MATCHES,
                                                                                         p1=COL["P1"],p2=COL["P2"],
                                                                                         winner=COL["WINNER"])
    return conn.execute(qry, (winner,loser,winner), update=True)
 
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    # get standings and pair them
    players = playerStandings()
    return [(players[i][0], players[i][1],players[i+1][0], players[i+1][1]) for i in range(0,len(players),2)]

