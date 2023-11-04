# Chess-Network-Analysis

This is a revised version from a chess project i started a while ago. The goal was to analyze how connectivity in a chess board changes 
as games progresses, and to examine if the network patterns depend on the opening that is used. I also want to study how "general principles"
affect network metrics. 

I felt that i complicated the code too much in the previous implementation by converting multiple times between chess notation and coordinates in a matrix. 
I want to adapt my methods so that chess notation is used alsmost everywhere except in a couple of functions. This will also simplify the reading of PGN files. 
