-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
DROP VIEW IF EXISTS matches_tally;
DROP VIEW IF EXISTS winners_tally;
DROP VIEW IF EXISTS losers_tally;
DROP TABLE IF EXISTS players;
DROP TABLE IF EXISTS matches;

CREATE TABLE players (
  player_id SERIAL primary key,
  name text
);

CREATE TABLE matches (
  match_id SERIAL primary key,
  winner integer,
  loser integer
);

-- This view provides a list of each player with their total number of wins
CREATE VIEW winners_tally
  AS SELECT p.player_id,
    SUM(CASE WHEN p.player_id = m.winner THEN 1 ELSE 0 END) AS win_tally
    FROM players p
    LEFT OUTER JOIN matches m ON p.player_id=m.winner
    GROUP BY p.player_id;

-- This view provides a list of each player with their total number of losses
CREATE VIEW losers_tally
  AS SELECT p.player_id,
    SUM(CASE WHEN p.player_id = m.loser THEN 1 ELSE 0 END) AS loss_tally
    FROM players p
    LEFT OUTER JOIN matches m ON p.player_id=m.loser
    GROUP BY p.player_id;

-- This view provides a list of each player with their total number of matches
-- It accomplishes this by summing their total wins and losses together
CREATE VIEW matches_tally
  AS SELECT player_id, SUM(match_tally) AS tot_num_matches
  FROM (
    SELECT player_id, win_tally AS match_tally
    FROM winners_tally
    UNION
    SELECT player_id, loss_tally AS match_tally
    FROM losers_tally
  ) AS matches_tally
  GROUP BY player_id;
