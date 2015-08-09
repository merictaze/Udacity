-- Create the database
DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament;

-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.


CREATE TABLE IF NOT EXISTS Players(
  ID SERIAL PRIMARY KEY,
  NAME TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Matches(
  P1 INTEGER NOT NULL REFERENCES Players(ID),
  P2 INTEGER NOT NULL REFERENCES Players(ID),
  WINNER INTEGER NOT NULL REFERENCES Players(ID),
  PRIMARY KEY(P1,P2)
);

-- View for win count for each player
CREATE VIEW MatchWins AS
  SELECT P.ID,
         (SELECT COUNT(*) FROM Matches WHERE WINNER = ID) AS WINS
  FROM Players P
;

-- View for total match count for each player
CREATE VIEW MatchTotal AS
  SELECT P.ID,
         (SELECT COUNT(*) FROM Matches WHERE (P1 = ID OR P2 = ID)) AS TOTAL
  FROM Players P
;

-- aggregated view for Players, MatchWins, MatchTotal
CREATE VIEW Standings AS
  SELECT P.ID, P.NAME, W.WINS, T.TOTAL FROM Players P
  LEFT JOIN MatchWins W on W.ID=P.ID
  LEFT JOIN MatchTotal T on T.ID=P.ID
;

-- You can write comments in this file by starting them with two dashes, like
-- these lines here.


