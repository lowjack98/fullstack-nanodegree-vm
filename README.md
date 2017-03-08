# Tournament Results:

This is a Python module that uses a PostgreSQL database to keep
track of players and matches in a game tournament using Swiss tournament rules.

## Products
- [PostgreSQL database][1]

## Language
- [Python][2]

## Dependencies
- [psycopg2][3]

[1]: https://www.postgresql.org/
[2]: https://python.org
[3]: http://initd.org/psycopg/

# Setup

## Fork to 'https://github.com/lowjack98/fullstack-nanodegree-vm.git', so that
you have a version of your own within your Github account

## Next, clone to your local server running PostgreSQL and python.

To use this module you will need to have a PostgreSQL database running and
have the commandline psql availiable.

To setup the required database and tables
 run: `\i tournament.sql` from the folder you have stored the files.

## Module Methods

### connect(database_name): Connects to the PostgreSQL database.  
   Returns a database connection and cursor.

### deleteMatches(): Removes all the match records from the database.

### deletePlayers(): Removes all the player records from the database.

### countPlayers(): Returns the number of players currently registered.

### registerPlayer(name): Adds a player to the tournament database.
     Args:
       name: the player's full name (need not be unique).

### playerStandings(): Returns a list of the players and their win records, sorted by wins.

     The first entry in the list will be the player in first place, or a
     player tied for first place if there is currently a tie.

     Returns:
       A list of tuples, each of which contains (id, name, wins, matches):
         id: the player's unique id (assigned by the database)
         name: the player's full name (as registered)
         wins: the number of matches the player has won
         matches: the number of matches the player has played


### reportMatch(winner, loser): Records the outcome of a single match between two players.
     Args:
       winner:  the id number of the player who won
       loser:  the id number of the player who lost


### swissPairings(): Returns a list of pairs of players for the next round of a match.

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
