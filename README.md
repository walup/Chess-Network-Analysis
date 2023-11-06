# Chess-Network-Analysis

This is a revised version from a chess project i started a while ago. The goal was to analyze how connectivity in a chess board changes 
as games progresses, and to examine if the network patterns depend on the opening that is used. I also want to study how "general principles"
affect network metrics. 

I felt that i complicated use of the code too much in the previous implementation by converting multiple times between chess notation and coordinates in a matrix. 
I want to adapt my methods so that chess notation is used alsmost everywhere except in a couple of functions. This will also simplify the reading of PGN files. 
I also want to be able to consider checks and checkmate, which is something that i did not implement in the previous version. 

Code will be more complex but it could be worth it. 

I actually think i'll start by simply exploring different games with the ChessGame class, and i'll add the network analysis later on. 
